"""Tous les textes visibles par l'utilisateur (interface entièrement en français)."""

NOM_LOGICIEL = "AutoSaisie Word"

# Modes
MODE_RAPIDE = "Mode rapide"
MODE_HUMAIN = "Mode humain"

# Zones
ZONE_TEXTE = "Texte à saisir"
ZONE_IMPORT = "Importation de fichiers"
ZONE_PARAMETRES = "Paramètres de saisie"
ZONE_COMMANDES = "Commandes"
ZONE_PROGRESSION = "Progression"

# Boutons
BTN_IMPORT_TXT = "Importer un fichier texte"
BTN_IMPORT_DOCX = "Importer un document Word"
BTN_DEMARRER = "Démarrer la saisie"
BTN_PAUSE = "Mettre en pause"
BTN_REPRENDRE = "Reprendre la saisie"
BTN_ARRETER = "Arrêter la saisie"
BTN_EFFACER = "Effacer le texte"
BTN_IMPORTER = "Importer un fichier"
BTN_PARAMETRES = "Paramètres"
BTN_APROPOS = "À propos"
BTN_QUITTER = "Quitter"
BTN_FERMER = "Fermer"

# Paramètres
LBL_MODE = "Mode de saisie"
LBL_VITESSE = "Vitesse de frappe (caractères par seconde)"
LBL_INTENSITE = "Intensité des pauses (mode humain)"
LBL_DELAI = "Délai avant le démarrage (secondes)"
LBL_NB_CARACTERES = "Nombre de caractères à traiter"
LBL_ETAT_WORD = "État de la fenêtre Word"
LBL_TAILLE_GROUPE = "Taille des groupes de caractères (mode rapide)"
LBL_JOURNAL = "Enregistrer un journal technique local (sans le contenu du texte)"

# Progression
LBL_CARACTERES_SAISIS = "Caractères saisis"
LBL_SUR = "sur"
LBL_ETAT = "État"
LBL_MODE_UTILISE = "Mode utilisé"
LBL_VITESSE_REELLE = "Vitesse réellement obtenue"
UNITE_CPS = "caractères/seconde"

# États de l'application
ETAT_ATTENTE = "En attente"
ETAT_VERIFICATION = "Vérification de Microsoft Word"
ETAT_PRET = "Prêt à démarrer"
ETAT_COMPTE_A_REBOURS = "Placez-vous dans Word : démarrage imminent"
ETAT_EN_COURS = "Saisie en cours"
ETAT_PAUSE = "Saisie en pause"
ETAT_SUSPENDUE = "Saisie suspendue"
ETAT_ARRETEE = "Saisie arrêtée"
ETAT_TERMINEE = "Saisie terminée"
ETAT_ERREUR_WORD = "Erreur de détection de Word"
ETAT_ERREUR = "Erreur pendant la saisie"

# État de Word
WORD_DETECTE = "Microsoft Word détecté"
WORD_NON_DETECTE = "Microsoft Word non détecté"
WORD_OUVERT_NON_ACTIF = "Microsoft Word ouvert, mais pas au premier plan"
WORD_NON_INSTALLE = "Microsoft Word n'est pas installé"

# Messages
MSG_WORD_REQUIS = (
    "Saisie impossible : Microsoft Word doit être la fenêtre active. "
    "Ouvrez votre document Word, placez le curseur à l'endroit souhaité, "
    "puis réessayez."
)
MSG_SUSPENDU = (
    "Saisie suspendue pour votre sécurité : Microsoft Word n'est plus la "
    "fenêtre active. Revenez dans Word et vérifiez la position du curseur "
    "avant de reprendre."
)
MSG_TEXTE_VIDE = "Le texte est vide. Collez du texte ou importez un fichier avant de démarrer."
MSG_WORD_NON_INSTALLE = (
    "Microsoft Word ne semble pas installé sur cet ordinateur. "
    "AutoSaisie Word a besoin de Microsoft Word pour fonctionner."
)
MSG_WORD_FERME = (
    "Microsoft Word est fermé. Ouvrez Word et un document, puis réessayez."
)
MSG_ERREUR_SAISIE = (
    "Une erreur est survenue pendant la saisie. La saisie a été arrêtée. "
    "Votre texte source est conservé."
)
MSG_ARRET_URGENCE = (
    "Arrêt d'urgence activé. La saisie a été interrompue. "
    "Votre texte source est conservé."
)
MSG_FICHIER_ILLISIBLE = (
    "Ce fichier est illisible ou n'est pas dans un format pris en charge."
)
MSG_DEPENDANCE_MANQUANTE = (
    "Un composant nécessaire à l'importation des documents Word est manquant."
)
MSG_CONFIRMER_EFFACER = "Voulez-vous vraiment effacer tout le texte ?"
MSG_CONFIRMER_QUITTER = (
    "Une saisie est en cours. Voulez-vous l'arrêter et quitter le logiciel ?"
)
MSG_LIMITE_DOCX = (
    "Le texte du document Word a été extrait (paragraphes et tableaux). "
    "Les images, zones de texte, notes de bas de page et mises en forme "
    "ne sont pas reprises. Vérifiez le contenu avant de démarrer."
)

# Dialogues
TITRE_ERREUR = "Erreur"
TITRE_INFO = "Information"
TITRE_ATTENTION = "Attention"
TITRE_CONFIRMATION = "Confirmation"
TITRE_OUVRIR_FICHIER = "Choisir un fichier"
TYPE_TXT = "Fichiers texte"
TYPE_DOCX = "Documents Word"
TYPE_TOUS = "Fichiers pris en charge"

RACCOURCI_URGENCE = "touche Pause/Attn, ou Ctrl + Alt + X"

TEXTE_APROPOS = (
    "{nom} — version {version}\n\n"
    "Saisit progressivement un texte dans Microsoft Word, uniquement lorsque "
    "Word est la fenêtre active.\n\n"
    "• Fonctionne entièrement sur votre ordinateur.\n"
    "• Aucun envoi de données, aucun suivi, aucun compte.\n"
    "• Arrêt d'urgence : {urgence}.\n\n"
    "Limite connue : Windows peut changer de fenêtre entre deux vérifications. "
    "La sécurité est renforcée (vérification avant chaque petit groupe de "
    "caractères) mais ne peut pas être garantie à 100 %."
)

INFOBULLES = {
    "mode": "Mode rapide : frappe régulière et rapide. Mode humain : rythme variable avec des pauses.",
    "vitesse": "Vitesse visée. La vitesse réellement obtenue dépend de Windows et de Word et peut être plus basse.",
    "intensite": "0 = presque aucune pause, 10 = pauses fréquentes et longues (mode humain uniquement).",
    "delai": "Temps dont vous disposez, après avoir cliqué sur Démarrer, pour cliquer dans votre document Word.",
}

# Saisie en arrière-plan
LBL_ARRIERE_PLAN = "Saisie en arrière-plan (Word peut être réduit ou masqué)"
MSG_ARRIERE_REQUIS = (
    "Saisie impossible : Microsoft Word doit être ouvert avec un document "
    "modifiable. Ouvrez votre document, placez le curseur à l'endroit "
    "souhaité, puis réessayez."
)
MSG_ARRIERE_SUSPENDU = (
    "Saisie suspendue pour votre sécurité : Word ne répond plus, le document "
    "est inaccessible, protégé ou a été modifié. Vérifiez votre document, "
    "puis reprenez la saisie."
)
INFOBULLES["arriere_plan"] = (
    "Le texte est envoyé directement au document Word, sans clavier : vous pouvez "
    "réduire Word et utiliser d'autres logiciels. Placez le curseur dans Word avant "
    "de démarrer et ne modifiez pas ce document pendant la saisie."
)
