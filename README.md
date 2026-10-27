# AutoSaisie Word

**AutoSaisie Word** est un logiciel Windows 10 qui saisit progressivement un texte dans **Microsoft Word**, comme si vous le tapiez au clavier. Il fonctionne uniquement sur votre ordinateur : aucun envoi de données, aucun suivi, aucun compte, aucune clé API.

> **Principe de sécurité n° 1 :** le logiciel n'envoie du texte **que** lorsque la fenêtre active est bien la fenêtre principale de Microsoft Word (processus `WINWORD.EXE`). En cas de doute, il s'arrête.

---

## 1. Fonctionnalités

- Zone de texte : collez, modifiez, sélectionnez et supprimez votre texte.
- Importation de fichiers `.txt` (UTF-8, accents français, retours à la ligne) et `.docx` (paragraphes et tableaux).
- **Mode rapide** : frappe régulière à vitesse réglable.
- **Mode humain** : vitesse variable, petites variations, pauses aléatoires et pauses plus longues après la ponctuation et les paragraphes (intensité réglable). Le texte saisi reste strictement identique au texte source.
- Boutons : Démarrer, Mettre en pause, Reprendre, Arrêter, Effacer, Importer, Paramètres, À propos, Quitter.
- Barre de progression, nombre de caractères saisis, état, mode utilisé et **vitesse réellement obtenue** (elle peut être plus basse que la vitesse demandée).
- **Arrêt d'urgence** : touche **Pause/Attn** ou **Ctrl + Alt + X**.
- **Saisie en arrière-plan** : Word peut être réduit ou masqué pendant la saisie (voir section 3 bis).
- Interface sombre inspirée de Telegram : barre latérale pour les réglages, grande zone de texte, bulle de progression et barre de commandes en bas.
- Interface entièrement en français.

---

## 2. Obtenir le logiciel (sans installer Python)

La compilation se fait **dans le cloud**, sur les ordinateurs de GitHub. Vous n'installez rien.

### Étape A — Créer un compte et un dépôt GitHub

1. Allez sur <https://github.com> et créez un compte gratuit (ou connectez-vous).
2. Cliquez sur le bouton vert **New** (ou **Nouveau**), en haut à gauche.
3. Nom du dépôt : `AutoSaisieWord`. Laissez **Public** (ou Private, au choix).
4. Ne cochez aucune case « Add a README » ou « .gitignore ». Cliquez sur **Create repository**.

### Étape B — Envoyer les fichiers du projet

1. Décompressez l'archive `AutoSaisieWord.zip` sur votre ordinateur. Vous obtenez un dossier `AutoSaisieWord`.
2. Sur la page de votre dépôt vide, cliquez sur le lien **uploading an existing file**.
3. Ouvrez le dossier `AutoSaisieWord` dans l'Explorateur de fichiers, sélectionnez **tout son contenu** (Ctrl + A) et faites-le glisser dans la page GitHub.
4. **Important :** le dossier caché `.github` doit être envoyé. Si vous ne le voyez pas, dans l'Explorateur : onglet **Affichage** → cochez **Éléments masqués**, puis recommencez.
5. Si GitHub refuse de prendre le dossier `.github` par glisser-déposer : cliquez sur **Add file → Create new file**, tapez comme nom `.github/workflows/build-windows.yml`, copiez-y le contenu du fichier du même nom, puis cliquez sur **Commit changes**.
6. En bas de la page, cliquez sur **Commit changes**.

### Étape C — Lancer la compilation

La compilation démarre **automatiquement** à chaque envoi de fichiers. Pour la lancer à la main :

1. Ouvrez l'onglet **Actions** de votre dépôt.
2. Si GitHub demande d'activer les workflows, cliquez sur le bouton d'activation.
3. Choisissez à gauche **Compiler AutoSaisie Word (Windows)**.
4. Cliquez sur **Run workflow**, puis sur le bouton vert **Run workflow**.
5. Patientez quelques minutes. Une pastille verte ✔ indique le succès ; une pastille rouge ✘ indique un échec (ouvrez-la pour lire le message).

### Étape D — Télécharger le logiciel

1. Dans **Actions**, cliquez sur la compilation réussie (pastille verte).
2. Descendez jusqu'à la section **Artifacts**.
3. Cliquez sur **AutoSaisieWord-Windows** : un fichier `.zip` se télécharge.
4. Faites un clic droit sur le zip → **Extraire tout**.
5. Vous obtenez `AutoSaisieWord.exe` (et `AutoSaisieWord.exe.sha256.txt`, voir la section Vérification).

### Facultatif — Publier une version (GitHub Releases)

Pour obtenir un lien de téléchargement stable, créez une « Release » avec un tag commençant par `v` (par exemple `v1.0.0`) : onglet **Releases** → **Create a new release** → tapez `v1.0.0` dans **Choose a tag** → **Publish release**. Le `.exe` n'est ajouté à la version **que si les tests et la compilation ont réussi**.

---

## 3. Utiliser le logiciel

1. Double-cliquez sur `AutoSaisieWord.exe`.
2. Collez votre texte dans la grande zone, ou cliquez sur **Importer un fichier texte** / **Importer un document Word**. Relisez et corrigez si besoin.
3. Choisissez le **mode**, la **vitesse** et le **délai avant le démarrage** (5 secondes par défaut).
4. Ouvrez votre document Word et placez le curseur à l'endroit voulu (avec le clavier ou la souris).
5. Revenez dans AutoSaisie Word et cliquez sur **Démarrer la saisie**.
6. Pendant le compte à rebours, **cliquez dans votre document Word** pour qu'il devienne la fenêtre active. À la fin du délai, le logiciel vérifie que Word est bien actif, puis commence.
7. Utilisez **Mettre en pause**, **Arrêter la saisie** ou le raccourci d'urgence si besoin. Pour continuer après une pause, cliquez sur **Reprendre la saisie** puis recliquez dans Word pendant le délai.

Le texte source n'est **jamais** effacé automatiquement, et Word n'est jamais fermé par le logiciel.

---

## 3 bis. Saisie en arrière-plan (Word réduit ou masqué)

Par défaut, le logiciel simule le clavier : Word doit donc rester la fenêtre active. Pour faire autre chose pendant la saisie, cochez **« Saisie en arrière-plan (Word peut être réduit ou masqué) »**.

Dans ce mode, le texte est envoyé **directement au document Word** (automatisation de Word, comme une macro), sans touches de clavier :

1. Ouvrez votre document Word et **placez le curseur** à l'endroit voulu.
2. Dans AutoSaisie Word, cochez l'option puis cliquez sur **Démarrer la saisie** (pas de délai : la saisie commence tout de suite).
3. Vous pouvez réduire Word, le masquer derrière d'autres fenêtres et utiliser votre ordinateur.

**Règles et limites de ce mode**
- Le texte ne peut aller que dans le document Word choisi au démarrage ; il ne peut pas partir dans une autre application.
- **Ne modifiez pas ce document** pendant la saisie et ne changez pas le curseur : le logiciel écrit à une position mémorisée. Si le document est modifié, fermé, protégé ou si Word est occupé (boîte de dialogue ouverte), la saisie est **suspendue** ; elle ne reprend jamais toute seule (bouton **Reprendre la saisie**).
- Word doit rester ouvert (ne le fermez pas) et le document doit être modifiable (pas en lecture seule ni en mode protégé).
- Les corrections automatiques de Word ne s'appliquent pas dans ce mode : le texte arrive tel quel.
- Le mode humain fonctionne aussi (rythme variable), mais le texte est inséré par l'automatisation de Word et non par de vraies frappes.
- Ce mode nécessite Word installé en version de bureau. Il est livré avec la bibliothèque `pywin32` (incluse dans l'exécutable).

## 4. Règles de sécurité

- La saisie ne démarre que si la fenêtre active est la **fenêtre principale de Word** et que son processus est `WINWORD.EXE` (le titre de la fenêtre n'est pas utilisé). Une boîte de dialogue Word est refusée.
- Chrome, Edge, Claude, Bloc-notes, Explorateur, Invite de commandes, PowerShell et toute autre application sont **refusés**.
- La fenêtre active est vérifiée **avant chaque petit groupe de caractères** (4 par défaut en mode rapide, 1 en mode humain ; réglable dans *Paramètres*).
- Si Word perd le focus ou si la détection échoue : la saisie est **suspendue** (état « Saisie suspendue »). Elle **ne reprend jamais toute seule** quand Word redevient actif ; il faut cliquer sur **Reprendre la saisie**, et Word doit alors être actif.
- Le raccourci d'urgence est surveillé par un fil séparé, indépendant de la boucle de saisie.

### Limites techniques connues (à lire)

- **La sécurité n'est pas absolue.** Windows peut changer de fenêtre entre la vérification et l'envoi d'un caractère. Le risque est réduit (petits groupes, vérification juste avant l'envoi) mais pas supprimé : un à quelques caractères peuvent, dans de rares cas, partir dans une autre fenêtre. Ne laissez pas le logiciel tourner sans surveillance et ne manipulez pas d'autres fenêtres pendant la saisie.
- Le logiciel simule le clavier : si vous appuyez sur des touches pendant la saisie (surtout avec Ctrl ou Alt), cela peut perturber le texte ou déclencher des raccourcis Word.
- Les corrections automatiques de Word (majuscules automatiques, listes à puces, remplacement de guillemets…) s'appliquent comme si vous tapiez : le texte dans Word peut donc légèrement différer de la source.
- Le *mode rapide* a une vitesse maximale réelle liée à Windows et à Word, souvent inférieure à la vitesse réglée. La valeur réelle est affichée.
- Word en « Mode protégé » (document téléchargé) ou en lecture seule ne peut pas recevoir de texte : activez la modification avant de démarrer.
- Importation `.docx` : paragraphes et tableaux uniquement (pas les images, zones de texte, notes de bas de page ni la mise en forme).
- Si Word s'exécute en mode administrateur et pas AutoSaisie Word, Windows peut empêcher l'envoi de touches ; lancez alors les deux de la même façon.
- Compatibilité : conçu pour Windows 10 (64 bits). Non testé sur d'autres versions.
- Testé automatiquement : la logique (texte, sécurité simulée, pause/reprise/arrêt). **L'interface graphique et l'envoi réel de touches ne peuvent être validés que sur un vrai Windows avec Word** : faites un premier essai sur un document de test.

---

## 5. Vérification du fichier et avertissements Windows

- Le `.exe` n'est **pas signé numériquement** : Windows SmartScreen peut afficher « Windows a protégé votre ordinateur ». C'est normal pour un logiciel non signé. **Ne désactivez pas Windows Defender.** Si vous avez compilé le logiciel vous-même depuis votre dépôt, cliquez sur **Informations complémentaires** puis **Exécuter quand même**.
- Téléchargez uniquement depuis **votre propre dépôt GitHub** (onglet Actions ou Releases).
- Vérifier l'intégrité : le fichier `AutoSaisieWord.exe.sha256.txt` contient l'empreinte SHA-256. Dans PowerShell : `Get-FileHash .\AutoSaisieWord.exe` — la valeur doit être identique.
- Si Defender met le fichier en quarantaine (faux positif possible avec les programmes qui simulent le clavier), vérifiez l'empreinte puis restaurez-le depuis l'historique de protection ; n'ajoutez d'exception que pour ce seul fichier.

---

## 6. Problèmes fréquents

| Problème | Solution |
|---|---|
| « Saisie impossible : Microsoft Word doit être la fenêtre active… » | Cliquez dans votre document Word pendant le délai de démarrage (augmentez-le si besoin). |
| « Microsoft Word est fermé » | Ouvrez Word et un document avant de démarrer. |
| « Microsoft Word n'est pas installé » | Le logiciel nécessite Microsoft Word (version de bureau). |
| « Saisie suspendue » | Word n'était plus actif. Revenez dans Word, vérifiez le curseur, puis **Reprendre la saisie**. |
| La compilation échoue (pastille rouge) | Ouvrez-la dans Actions, repérez l'étape rouge et copiez le message d'erreur pour obtenir de l'aide. |
| Le dossier `.github` n'a pas été envoyé | Voir l'étape B, points 4 et 5. |
| La vitesse réelle est plus basse que prévu | Normal : voir « Limites techniques ». Baissez la vitesse ou la taille des groupes. |
| Le texte contient des différences dans Word | Vérifiez les options de correction automatique de Word. |

---

## 7. Pour les curieux : structure du projet

```
app.py                      point d'entrée
autosaisie/                 code du logiciel (interface, sécurité, saisie, import, rythme)
tests/                      tests automatisés
AutoSaisieWord.spec         configuration PyInstaller
requirements.txt            dépendances
build.bat                   compilation locale FACULTATIVE (inutile pour vous)
.github/workflows/          compilation automatique GitHub Actions
```

Tests automatiques : `python -m unittest discover -s tests -t . -v` (lancés par GitHub Actions à chaque compilation).
