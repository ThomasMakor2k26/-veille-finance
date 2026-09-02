# Veille automatisée — Finance / Économie

Collecte les articles de 11 sources RSS financières, extrait leur texte, les classe par
thème, les note de 0 à 10 selon leur pertinence pour ton métier via Claude, et produit un
classeur Excel trié, colorié, avec une feuille de synthèse.

## Contenu du projet

| Fichier | Rôle |
|---|---|
| `config.py` | **Le seul fichier à modifier** : sources, thèmes, couleurs, profil métier |
| `scraper.py` | La mécanique. Pas besoin d'y toucher |
| `requirements.txt` | Les bibliothèques à installer |
| `lancer_veille.bat` | Lanceur pour le Planificateur de tâches Windows |
| `.gitignore` | Fichiers à exclure d'un dépôt Git |

## Installation

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Sur Mac / Linux, remplacer la deuxième ligne par `source venv/bin/activate`.

## Clé API

Le script lit la variable d'environnement `ANTHROPIC_API_KEY` (à créer sur
console.anthropic.com).

```
setx ANTHROPIC_API_KEY "sk-ant-..."
```

Puis redémarrer VS Code. Sans clé, le script ne plante pas : il bascule automatiquement en
collecte seule et te le signale.

Ne jamais écrire la clé dans le code, ne jamais la committer.

## Utilisation

```
python scraper.py                  Exécution normale
python scraper.py --sans-ia        Collecte seule, aucun appel API (gratuit)
python scraper.py --max 3          3 articles par source, pour tester vite
python scraper.py --sortie test.xlsx
```

## Le fichier Excel produit

**Feuille « Articles »** — une ligne par article, triée par pertinence, puis score, puis
thème, puis date. Fond coloré selon le thème, articles pertinents en gras, titres
cliquables vers l'article, dégradé rouge-jaune-vert sur la colonne score, en-tête figé et
filtres automatiques.

**Feuille « Synthèse »** — total d'articles, nombre et taux de pertinents, score moyen,
sources actives, date de dernière collecte, puis la répartition par thème et par source.

## Ce qui a changé par rapport à la version précédente

**Fiabilité** — réessais automatiques avec temporisation croissante sur les erreurs réseau
(429, 500, 502, 503, 504) et sur les appels IA ; délai d'attente sur chaque requête ; une
source en panne est journalisée au lieu d'être ignorée en silence ; si Excel est ouvert au
moment de l'écriture, le fichier est enregistré sous un autre nom au lieu de planter.

**Journalisation** — un fichier par jour dans `logs/`, plus un affichage lisible dans le
terminal. Les erreurs détaillées vont dans le fichier, pas à l'écran.

**Anti-doublons** — les URL sont nettoyées de leurs paramètres de suivi (`utm_*`, `fbclid`…)
avant comparaison, donc le même article partagé via deux canaux n'est plus compté deux fois.
Les liens Google News sont résolus vers l'URL réelle du média.

**Données** — vraie date de publication issue du flux (au lieu de l'heure de collecte),
filtre d'ancienneté configurable, résumé de l'article et justification de la note stockés.

**Notation IA** — score de 0 à 10 au lieu d'un Oui/Non, avec un barème explicite ; réponse
au format JSON, donc analysable de façon fiable ; seuil de pertinence réglable dans
`config.py` ; en cas d'échec, l'article est marqué `?` et la collecte continue.

**Structure** — configuration isolée dans `config.py`, code annoté de types, options en
ligne de commande, codes de sortie corrects pour un lancement planifié.

## Version en ligne (lien internet, sans IA)

Pour consulter la veille en direct depuis un navigateur, sur une page publique qui se
met à jour toute seule toutes les 5 min et où les articles de plus de 24 h disparaissent :
voir **`DEPLOIEMENT.md`**. Cette version tourne sur les serveurs GitHub (gratuit) et
n'utilise que `veille_web.py` + `docs/`. Elle ne remplace pas la sortie Excel : les deux
usages coexistent.

## Automatisation quotidienne (Windows)

1. Ouvrir le **Planificateur de tâches** → Créer une tâche de base
2. Déclencheur : quotidien, à l'heure voulue
3. Action : Démarrer un programme → sélectionner `lancer_veille.bat`
4. Dans « Commencer dans », indiquer le dossier du projet

## Pistes suivantes

- Alerte email sur les articles notés 9 ou 10
- Historique glissant : archiver les articles de plus de 90 jours
- Graphique d'évolution du volume par thème
- Versionner le projet avec Git pour ne plus dépendre d'une machine
