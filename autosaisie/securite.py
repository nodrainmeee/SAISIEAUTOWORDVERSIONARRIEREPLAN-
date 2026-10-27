"""Détection fiable de Microsoft Word et décision d'autoriser (ou non) la saisie.

Règle : si la fenêtre active n'est pas identifiée de façon fiable comme la fenêtre
principale de Microsoft Word, aucun caractère n'est envoyé.
"""

import ntpath
import os
import sys
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

NOM_EXE_WORD = "winword.exe"
CLASSE_FENETRE_WORD = "OpusApp"  # fenêtre principale de Word (pas les boîtes de dialogue)


@dataclass(frozen=True)
class FenetreInfo:
    identifiant: int
    pid: int
    chemin_exe: str
    classe: str

    @property
    def nom_exe(self) -> str:
        return ntpath.basename(self.chemin_exe).lower() if self.chemin_exe else ""


FournisseurFenetre = Callable[[], Optional[FenetreInfo]]


def obtenir_fenetre_active() -> Optional[FenetreInfo]:
    """Lit la fenêtre active via l'API Windows. Retourne None en cas d'échec."""
    if sys.platform != "win32":
        return None
    from . import winapi
    donnees = winapi.fenetre_active()
    if donnees is None:
        return None
    identifiant, pid, chemin, classe = donnees
    return FenetreInfo(identifiant, pid, chemin, classe)


def evaluer_fenetre(info: Optional[FenetreInfo]) -> Tuple[bool, str]:
    """Décide si la fenêtre est bien la fenêtre principale de Word.

    Retourne (autorisé, code). Le code sert au journal et aux tests.
    """
    if info is None:
        return False, "detection_echouee"
    if info.pid == os.getpid():
        return False, "fenetre_propre_logiciel"
    if not info.chemin_exe:
        return False, "processus_non_identifie"
    if info.nom_exe != NOM_EXE_WORD:
        return False, "autre_application"
    if info.classe != CLASSE_FENETRE_WORD:
        return False, "word_boite_de_dialogue_ou_autre_fenetre"
    return True, "ok"


def verifier_word_actif(fournisseur: FournisseurFenetre = obtenir_fenetre_active) -> Tuple[bool, str]:
    """Lit la fenêtre active et l'évalue. Toute exception = refus."""
    try:
        info = fournisseur()
    except Exception:
        return False, "detection_echouee"
    return evaluer_fenetre(info)


# --- État de Word (affichage uniquement, jamais utilisé pour autoriser la saisie) ---

ETAT_NON_INSTALLE = "non_installe"
ETAT_FERME = "ferme"
ETAT_OUVERT_NON_ACTIF = "ouvert_non_actif"
ETAT_ACTIF = "actif"


def etat_word(fournisseur: FournisseurFenetre = obtenir_fenetre_active) -> str:
    if verifier_word_actif(fournisseur)[0]:
        return ETAT_ACTIF
    if sys.platform != "win32":
        return ETAT_NON_INSTALLE
    from . import winapi
    try:
        if winapi.fenetres_word_ouvertes() > 0:
            return ETAT_OUVERT_NON_ACTIF
        if not winapi.word_installe():
            return ETAT_NON_INSTALLE
    except Exception:
        return ETAT_FERME
    return ETAT_FERME
