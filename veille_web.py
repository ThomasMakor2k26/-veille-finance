"""
Collecte pour la veille en ligne (version web, sans IA).

Lit les flux RSS de config.py, classe chaque article par thème, et met à jour
docs/articles.json — le fichier que la page web consulte.

Fenêtre glissante : un article disparaît du JSON 24 h après avoir été vu pour
la première fois (champ « vu_le »). La date de publication, elle, ne sert qu'au
tri et à l'affichage.

Usage :
    python veille_web.py
    python veille_web.py --heures 48      # garder 48 h au lieu de 24
    python veille_web.py --max 5          # 5 articles par source (test rapide)
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import feedparser
import requests
import trafilatura
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

FICHIER_JSON = Path("docs") / "articles.json"
FENETRE_HEURES = 24

NAVIGATEUR = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

PARAMS_PARASITES = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "xtor", "ref", "ncid", "at_medium", "at_campaign",
}


def log(message: str) -> None:
    print(f"{datetime.now():%H:%M:%S}  {message}", flush=True)


def creer_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": NAVIGATEUR, "Accept-Language": "fr-FR,fr;q=0.9"})
    politique = Retry(
        total=2,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adaptateur = HTTPAdapter(max_retries=politique, pool_maxsize=config.NB_THREADS_PARALLELES * 2)
    session.mount("https://", adaptateur)
    session.mount("http://", adaptateur)
    return session


SESSION = creer_session()


def normaliser_url(url: str) -> str:
    """Retire les paramètres de tracking pour comparer deux liens de façon fiable."""
    try:
        morceaux = urlparse(url)
        params = {k: v for k, v in parse_qs(morceaux.query).items()
                  if k.lower() not in PARAMS_PARASITES}
        propre = morceaux._replace(query=urlencode(params, doseq=True), fragment="")
        return urlunparse(propre).rstrip("/")
    except Exception:
        return url


def resoudre_redirection(url: str) -> str:
    """Les liens Google News pointent vers une redirection : on récupère l'URL réelle."""
    if "news.google.com" not in url:
        return url
    try:
        reponse = SESSION.get(url, timeout=config.TIMEOUT_SECONDES, allow_redirects=True)
        return reponse.url
    except requests.RequestException:
        return url


def classer_article(texte: str) -> str:
    if not texte:
        return config.THEME_PAR_DEFAUT
    minuscules = texte.lower()
    scores = {
        theme: sum(minuscules.count(mot) for mot in infos["mots_cles"])
        for theme, infos in config.THEMES.items()
    }
    meilleur = max(scores, key=scores.get)
    return meilleur if scores[meilleur] > 0 else config.THEME_PAR_DEFAUT


def couleur_theme(theme: str) -> str:
    return config.THEMES.get(theme, {}).get("couleur", config.COULEUR_DEFAUT)


def date_publication(entree) -> datetime | None:
    for champ in ("published_parsed", "updated_parsed"):
        valeur = entree.get(champ)
        if valeur:
            try:
                return datetime(*valeur[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def extraire_texte(url: str, secours: str) -> str:
    try:
        page = SESSION.get(url, timeout=config.TIMEOUT_SECONDES)
        texte = trafilatura.extract(page.text, include_comments=False, include_tables=False)
        if texte and len(texte) > 200:
            return texte
    except Exception:
        pass
    return trafilatura.html2txt(secours) if secours else ""


def lire_flux(nom: str, url_flux: str) -> list[dict]:
    try:
        reponse = SESSION.get(url_flux, timeout=config.TIMEOUT_SECONDES)
        reponse.raise_for_status()
        flux = feedparser.parse(reponse.content)
    except requests.RequestException as erreur:
        log(f"  {nom} injoignable : {erreur}")
        return []

    if not flux.entries:
        log(f"  {nom} : flux vide")
        return []

    limite_age = (
        datetime.now(timezone.utc) - timedelta(days=config.AGE_MAX_JOURS)
        if config.AGE_MAX_JOURS else None
    )

    retenues = []
    for entree in flux.entries[: config.NB_ARTICLES_PAR_SOURCE]:
        lien = entree.get("link", "")
        if not lien:
            continue
        publiee = date_publication(entree)
        if limite_age and publiee and publiee < limite_age:
            continue
        retenues.append({
            "source": nom,
            "titre": entree.get("title", "Sans titre").strip(),
            "url": lien,
            "resume_rss": entree.get("summary", ""),
            "date_publication": publiee.isoformat() if publiee else "",
        })
    return retenues


def enrichir(brut: dict) -> dict:
    url_reelle = resoudre_redirection(brut["url"])
    texte = extraire_texte(url_reelle, brut["resume_rss"])
    theme = classer_article(f"{brut['titre']} {texte}")
    maintenant = datetime.now(timezone.utc).isoformat()
    return {
        "titre": brut["titre"],
        "source": brut["source"],
        "theme": theme,
        "couleur": couleur_theme(theme),
        "url": url_reelle,
        "url_propre": normaliser_url(url_reelle),
        "date_publication": brut["date_publication"],
        "vu_le": maintenant,
        "resume": " ".join(texte.split())[:300],
    }


def charger_existant() -> list[dict]:
    if not FICHIER_JSON.exists():
        return []
    try:
        donnees = json.loads(FICHIER_JSON.read_text(encoding="utf-8"))
        return donnees.get("articles", [])
    except Exception as erreur:
        log(f"articles.json illisible ({erreur}) — on repart à zéro.")
        return []


def dans_la_fenetre(article: dict, limite: datetime) -> bool:
    try:
        return datetime.fromisoformat(article["vu_le"]) >= limite
    except (KeyError, ValueError):
        return False


def cle_tri(article: dict) -> str:
    return article.get("date_publication") or article.get("vu_le") or ""


def main() -> int:
    parseur = argparse.ArgumentParser(description="Collecte pour la veille en ligne")
    parseur.add_argument("--heures", type=int, default=FENETRE_HEURES,
                         help="durée de vie d'un article dans la veille (défaut 24)")
    parseur.add_argument("--max", type=int, metavar="N",
                         help="articles par source (test rapide)")
    args = parseur.parse_args()

    if args.max:
        config.NB_ARTICLES_PAR_SOURCE = args.max

    debut = datetime.now(timezone.utc)
    limite = debut - timedelta(hours=args.heures)

    existants = charger_existant()
    connus = {a.get("url_propre") for a in existants}
    log(f"{len(existants)} article(s) déjà en veille.")

    bruts = []
    for nom, url_flux in config.SOURCES.items():
        lus = lire_flux(nom, url_flux)
        bruts.extend(lus)
        log(f"{nom} : {len(lus)} lu(s)")

    nouveaux_bruts = []
    vus_ce_tour = set()
    for b in bruts:
        cle = normaliser_url(b["url"])
        if cle in connus or cle in vus_ce_tour:
            continue
        vus_ce_tour.add(cle)
        nouveaux_bruts.append(b)

    log(f"{len(nouveaux_bruts)} nouvel(s) article(s) à enrichir...")

    nouveaux = []
    if nouveaux_bruts:
        with ThreadPoolExecutor(max_workers=config.NB_THREADS_PARALLELES) as pool:
            futurs = {pool.submit(enrichir, b): b for b in nouveaux_bruts}
            for futur in as_completed(futurs):
                try:
                    nouveaux.append(futur.result())
                except Exception as erreur:
                    log(f"  abandonné : {futurs[futur]['titre'][:50]} ({erreur})")

    # fusion + dédoublonnage sur url_propre, puis fenêtre glissante
    fusion = {}
    for a in existants + nouveaux:
        cle = a.get("url_propre") or a.get("url")
        if cle in fusion:
            # on garde la date « vu_le » la plus ancienne
            if a.get("vu_le", "") < fusion[cle].get("vu_le", ""):
                fusion[cle]["vu_le"] = a["vu_le"]
            continue
        fusion[cle] = a

    vivants = [a for a in fusion.values() if dans_la_fenetre(a, limite)]
    vivants.sort(key=cle_tri, reverse=True)
    expires = len(fusion) - len(vivants)

    FICHIER_JSON.parent.mkdir(parents=True, exist_ok=True)
    sortie = {
        "genere_le": debut.isoformat(),
        "fenetre_heures": args.heures,
        "nb_articles": len(vivants),
        "articles": vivants,
    }
    FICHIER_JSON.write_text(
        json.dumps(sortie, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    log(f"Écrit {FICHIER_JSON} : {len(vivants)} article(s) "
        f"(+{len(nouveaux)} nouveau(x), -{expires} expiré(s)).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as erreur:
        # ne jamais faire échouer le workflow pour une panne réseau isolée
        log(f"Erreur non fatale : {erreur}")
        sys.exit(0)
