"""
Configuration de la veille.

C'est LE seul fichier que tu as besoin de modifier au quotidien.
scraper.py contient la mécanique et n'a pas à être touché.
"""

# ============================================================
# SOURCES
# ============================================================
# Format : "Nom affiché dans Excel": "URL du flux RSS"
# Pour ajouter une source sans flux RSS officiel, passe par Google News :
#   https://news.google.com/rss/search?q=site:LESITE.com&hl=fr&gl=FR&ceid=FR:fr

SOURCES = {
    "Le Figaro Economie":  "https://www.lefigaro.fr/rss/figaro_economie.xml",
    "Le Figaro Bourse":    "https://www.lefigaro.fr/rss/figaro_bourse.xml",
    "Le Monde Economie":   "https://www.lemonde.fr/economie/rss_full.xml",
    "Investir":            "https://services.lesechos.fr/rss/investir-conseils-boursiers.xml",
    "Wall Street Journal": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "Financial Times":     "https://www.ft.com/rss/home/international",
    "Challenges Economie": "https://www.challenges.fr/economie/rss.xml",
    "Investing.com":       "https://fr.investing.com/rss/market_overview.rss",
    "Boursorama":          "https://news.google.com/rss/search?q=site:boursorama.com+bourse&hl=fr&gl=FR&ceid=FR:fr",
    "BFM Business":        "https://news.google.com/rss/search?q=site:bfmtv.com+bfmbusiness&hl=fr&gl=FR&ceid=FR:fr",
    "ZoneBourse":          "https://news.google.com/rss/search?q=site:zonebourse.com&hl=fr&gl=FR&ceid=FR:fr",
}

# ============================================================
# COLLECTE
# ============================================================

NB_ARTICLES_PAR_SOURCE = 10    # articles récents lus par source à chaque passage
NB_THREADS_PARALLELES  = 5     # requêtes simultanées (baisse à 2-3 si des sites bloquent)
TIMEOUT_SECONDES       = 15    # abandon d'un site qui ne répond pas
AGE_MAX_JOURS          = 7     # ignore les articles plus vieux que ça (0 = pas de limite)

# ============================================================
# THÈMES ET COULEURS
# ============================================================
# Chaque thème : mots-clés de détection + couleur de fond Excel (hexadécimal)
# L'ordre compte : en cas d'égalité de score, le premier thème listé gagne.

THEMES = {
    "Bourse / Marchés": {
        "mots_cles": ["bourse", "action", "indice", "cac 40", "wall street", "nasdaq",
                      "marché financier", "cotation", "volatilité", "obligation"],
        "couleur": "FFD966",
    },
    "Entreprises": {
        "mots_cles": ["entreprise", "société", "résultats", "chiffre d'affaires", "bénéfice",
                      "rachat", "fusion", "acquisition", "dividende", "trimestriel"],
        "couleur": "9DC3E6",
    },
    "Macroéconomie": {
        "mots_cles": ["inflation", "banque centrale", "taux d'intérêt", "pib", "bce", "fed",
                      "croissance économique", "récession", "chômage", "déficit"],
        "couleur": "A9D18E",
    },
    "International": {
        "mots_cles": ["chine", "états-unis", "europe", "commerce international", "exportation",
                      "tarifs douaniers", "géopolitique", "sanctions"],
        "couleur": "F4B183",
    },
}

THEME_PAR_DEFAUT = "Finance / Economie (général)"
COULEUR_DEFAUT   = "D9D9D9"

# ============================================================
# ÉVALUATION PAR L'IA
# ============================================================

PROFIL_METIER = (
    "analyste de marché / trading : je m'intéresse aux mouvements de marchés, à la volatilité, "
    "aux taux, aux décisions de banques centrales, aux résultats d'entreprises qui influencent "
    "les cours, et à l'actualité macroéconomique ayant un impact direct sur le prix des actifs."
)

MODELE_IA        = "claude-sonnet-5"
SEUIL_PERTINENCE = 6     # score minimum (sur 10) pour qu'un article soit marqué "pertinent"
IA_ACTIVE        = True  # False = collecte seule, sans appel à l'API (gratuit)

# ============================================================
# FICHIERS
# ============================================================

FICHIER_SORTIE = "articles_tries.xlsx"
DOSSIER_LOGS   = "logs"
