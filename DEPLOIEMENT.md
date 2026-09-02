# Obtenir le lien de la veille — 100 % dans le navigateur

Aucun logiciel à installer. Il te faut juste un compte GitHub et le fichier
`veille-finance.zip` (décompressé).

Résultat : `https://TON-PSEUDO.github.io/veille-finance/`
→ page publique, collecte toutes les 5 min, articles effacés au bout de 24 h, sans IA.

---

## 1. Décompresser le zip

Clic droit sur `veille-finance.zip` → **Extraire tout**.
Tu obtiens un dossier `veille-finance` contenant `config.py`, `veille_web.py`,
`docs\`, `.github\`, etc.

## 2. Créer le dépôt

1. Aller sur **https://github.com/new**
2. *Repository name* : `veille-finance`
3. Cocher **Public**
4. Ne rien cocher d'autre (pas de README) → **Create repository**

## 3. Envoyer les fichiers

Sur la page qui s'affiche, cliquer sur le lien **« uploading an existing file »**.

1. Ouvrir le dossier `veille-finance` extrait à l'étape 1.
2. Sélectionner **tout ce qu'il y a dedans** (Ctrl+A) et le glisser dans la zone de dépôt du navigateur.
3. En bas : **Commit changes**.

> Si le dossier `.github` n'est pas parti (Windows le cache parfois) :
> bouton **Add file → Create new file**, taper dans le nom :
> `.github/workflows/veille.yml`
> puis coller le contenu du fichier `veille.yml` du zip → **Commit changes**.

## 4. Activer la page web

Dans le dépôt : **Settings** (onglet en haut) → **Pages** (menu de gauche)
- *Source* : **Deploy from a branch**
- *Branch* : **main** — dossier : **/docs** → **Save**

## 5. Lancer la première collecte

Onglet **Actions** → s'il y a un bandeau vert *« I understand my workflows, enable them »*, cliquer dessus.
Puis, à gauche : **Veille en direct** → bouton **Run workflow** → **Run workflow**.
Attendre 1 à 2 min (le point devient vert).

## 6. Le lien

Retour dans **Settings → Pages** : l'adresse est affichée en haut
(*« Your site is live at … »*). C'est ce lien que tu copies partout.

À partir de là tout est automatique : la collecte repart toute seule toutes les 5 min,
la page se rafraîchit toute seule toutes les 2 min.

---

### Si ça ne marche toujours pas

Dis-moi **à quelle étape** ça bloque et **le message exact** affiché.
Sans ça je ne peux pas deviner ce qui coince.

Limite connue : GitHub vise 5 min mais peut retarder de quelques minutes aux heures de pointe (offre gratuite).
