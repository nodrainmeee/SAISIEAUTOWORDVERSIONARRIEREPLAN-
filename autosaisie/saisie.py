"""Moteur de saisie : fil d'exécution séparé, pause/reprise/arrêt, sécurité Word."""

import random
import threading
import time
from enum import Enum
from typing import Callable, Optional

from . import journal
from . import libelles as L
from .rythme import MODE_HUMAIN, MODE_RAPIDE, delai_apres, prochain_groupe
from .securite import FournisseurFenetre, verifier_word_actif
from .texte import texte_est_vide


class Etat(Enum):
    ATTENTE = "attente"
    COMPTE_A_REBOURS = "compte_a_rebours"
    VERIFICATION = "verification"
    EN_COURS = "en_cours"
    PAUSE = "pause"
    SUSPENDUE = "suspendue"
    ARRETEE = "arretee"
    TERMINEE = "terminee"
    ERREUR_WORD = "erreur_word"
    ERREUR = "erreur"


ETAT_LIBELLE = {
    Etat.ATTENTE: L.ETAT_ATTENTE,
    Etat.COMPTE_A_REBOURS: L.ETAT_COMPTE_A_REBOURS,
    Etat.VERIFICATION: L.ETAT_VERIFICATION,
    Etat.EN_COURS: L.ETAT_EN_COURS,
    Etat.PAUSE: L.ETAT_PAUSE,
    Etat.SUSPENDUE: L.ETAT_SUSPENDUE,
    Etat.ARRETEE: L.ETAT_ARRETEE,
    Etat.TERMINEE: L.ETAT_TERMINEE,
    Etat.ERREUR_WORD: L.ETAT_ERREUR_WORD,
    Etat.ERREUR: L.ETAT_ERREUR,
}

ETATS_ACTIFS = (Etat.COMPTE_A_REBOURS, Etat.VERIFICATION, Etat.EN_COURS)
ETATS_REPRISE = (Etat.PAUSE, Etat.SUSPENDUE)


class CibleClavier:
    """Saisie par simulation du clavier : Word doit être la fenêtre active."""

    message_demarrage = L.MSG_WORD_REQUIS
    message_suspension = L.MSG_SUSPENDU

    def __init__(self, fournisseur: FournisseurFenetre, envoyeur: Callable[[str], None]):
        self._fournisseur = fournisseur
        self._envoyeur = envoyeur

    def ouvrir(self, reprise: bool):
        return self.verifier()

    def verifier(self):
        return verifier_word_actif(self._fournisseur)

    def envoyer(self, texte: str) -> None:
        self._envoyeur(texte)

    def fermer(self) -> None:
        pass


class MoteurSaisie:
    """Envoie le texte par petits groupes, en vérifiant Word avant chaque envoi.

    L'état est lisible depuis l'interface (etat, message, position, total).
    Aucune reprise automatique : après une suspension, seule une action
    explicite de l'utilisateur permet de continuer.
    """

    def __init__(self, fournisseur_fenetre: FournisseurFenetre,
                 envoyeur: Callable[[str], None],
                 alea: Optional[random.Random] = None,
                 fabrique_arriere_plan: Optional[Callable[[], object]] = None):
        self._fournisseur = fournisseur_fenetre
        self._envoyeur = envoyeur
        self._fabrique_arriere_plan = fabrique_arriere_plan
        self.arriere_plan = False
        self._cible = None
        self._alea = alea or random.Random()
        self._verrou = threading.Lock()
        self._fil: Optional[threading.Thread] = None
        self._signal = threading.Event()
        self._demande: Optional[str] = None  # None, "pause", "arret", "urgence"

        self.etat = Etat.ATTENTE
        self.message = ""
        self.texte = ""
        self.position = 0
        self.mode = MODE_RAPIDE
        self.cps = 40.0
        self.intensite = 5.0
        self.taille_groupe = 4
        self._t_debut = 0.0
        self._pos_debut = 0
        self._t_fin = 0.0

    # --- Propriétés utiles à l'interface ---

    @property
    def total(self) -> int:
        return len(self.texte)

    def en_cours(self) -> bool:
        return self.etat in ETATS_ACTIFS

    def vitesse_reelle(self) -> float:
        """Caractères par seconde réellement obtenus depuis le dernier (re)départ."""
        if not self._t_debut:
            return 0.0
        fin = time.monotonic() if self.en_cours() else (self._t_fin or time.monotonic())
        duree = fin - self._t_debut
        if duree <= 0.2:
            return 0.0
        return (self.position - self._pos_debut) / duree

    # --- Commandes ---

    def configurer(self, texte: str, mode: str, cps: float, intensite: float,
                   taille_groupe: int, arriere_plan: bool = False) -> None:
        if self.en_cours() or self.etat in ETATS_REPRISE:
            return
        self.arriere_plan = bool(arriere_plan) and self._fabrique_arriere_plan is not None
        self.texte = texte
        self.mode = mode
        self.cps = max(1.0, float(cps))
        self.intensite = float(intensite)
        self.taille_groupe = 1 if mode == MODE_HUMAIN else max(1, int(taille_groupe))

    def demarrer(self, delai: float) -> bool:
        with self._verrou:
            if self.en_cours() or self.etat in ETATS_REPRISE:
                return False
            if texte_est_vide(self.texte):
                self._definir(Etat.ERREUR, L.MSG_TEXTE_VIDE)
                return False
            self.position = 0
            if self.arriere_plan:
                self._cible = self._fabrique_arriere_plan()
            else:
                self._cible = CibleClavier(self._fournisseur, self._envoyeur)
            self._lancer(delai, reprise=False)
            return True

    def reprendre(self, delai: float) -> bool:
        with self._verrou:
            if self.etat not in ETATS_REPRISE:
                return False
            self._lancer(delai, reprise=True)
            return True

    def mettre_en_pause(self) -> None:
        if self.en_cours():
            self._demande = "pause"
            self._signal.set()

    def arreter(self) -> None:
        self._demander_arret("arret")

    def urgence(self) -> None:
        self._demander_arret("urgence")

    def attendre_fin(self, timeout: float = 5.0) -> None:
        fil = self._fil
        if fil is not None:
            fil.join(timeout)

    # --- Interne ---

    def _demander_arret(self, nature: str) -> None:
        if self.en_cours():
            self._demande = nature
            self._signal.set()
        elif self.etat in ETATS_REPRISE:
            self._definir(Etat.ARRETEE, L.MSG_ARRET_URGENCE if nature == "urgence" else "")

    def _definir(self, etat: Etat, message: str = "") -> None:
        self.etat = etat
        self.message = message
        journal.ecrire("etat=" + etat.value)

    def _lancer(self, delai: float, reprise: bool) -> None:
        self._demande = None
        self._signal = threading.Event()
        self._t_debut = 0.0
        self._definir(Etat.COMPTE_A_REBOURS if delai > 0 else Etat.VERIFICATION)
        self._fil = threading.Thread(
            target=self._boucle, args=(float(delai), reprise, self._signal, self._cible),
            daemon=True)
        self._fil.start()

    def _traiter_demande(self) -> bool:
        """Applique une demande pause/arrêt. Retourne True si la boucle doit s'arrêter."""
        demande = self._demande
        if demande is None:
            return False
        self._t_fin = time.monotonic()
        if demande == "pause":
            self._definir(Etat.PAUSE)
        elif demande == "urgence":
            self._definir(Etat.ARRETEE, L.MSG_ARRET_URGENCE)
        else:
            self._definir(Etat.ARRETEE)
        return True

    def _boucle(self, delai: float, reprise: bool, signal: threading.Event, cible) -> None:
        try:
            if delai > 0:
                signal.wait(delai)
                if self._traiter_demande():
                    return
            self._definir(Etat.VERIFICATION)
            ok, code = cible.ouvrir(reprise)
            if not ok:
                journal.ecrire("refus=" + code)
                if reprise:
                    self._definir(Etat.SUSPENDUE, cible.message_demarrage)
                else:
                    self._definir(Etat.ERREUR_WORD, cible.message_demarrage)
                return

            self._definir(Etat.EN_COURS)
            self._t_debut = time.monotonic()
            self._pos_debut = self.position
            self._t_fin = 0.0

            while self.position < len(self.texte):
                if self._traiter_demande():
                    return
                # Vérification immédiatement avant chaque groupe de caractères.
                ok, code = cible.verifier()
                if not ok:
                    journal.ecrire("refus=" + code)
                    self._t_fin = time.monotonic()
                    self._definir(Etat.SUSPENDUE, cible.message_suspension)
                    return
                if self._traiter_demande():  # dernière chance avant l'envoi
                    return
                groupe = prochain_groupe(self.texte, self.position, self.taille_groupe)
                try:
                    cible.envoyer(groupe)
                except Exception:
                    self._t_fin = time.monotonic()
                    self._definir(Etat.ERREUR, L.MSG_ERREUR_SAISIE)
                    return
                self.position += len(groupe)
                pause = delai_apres(groupe, self.mode, self.cps, self.intensite, self._alea)
                signal.wait(pause)  # se réveille tout de suite si pause/arrêt demandé

            self._t_fin = time.monotonic()
            self._definir(Etat.TERMINEE)
        except Exception:
            self._t_fin = time.monotonic()
            self._definir(Etat.ERREUR, L.MSG_ERREUR_SAISIE)
        finally:
            try:
                cible.fermer()
            except Exception:
                pass


class SurveillanceUrgence(threading.Thread):
    """Fil indépendant de la boucle de saisie : surveille le raccourci d'urgence.

    Raccourcis : touche Pause/Attn, ou Ctrl + Alt + X.
    """

    def __init__(self, moteur: MoteurSaisie):
        super().__init__(daemon=True)
        self._moteur = moteur
        self._evt_arret = threading.Event()

    def arreter(self) -> None:
        self._evt_arret.set()

    def run(self) -> None:
        from . import winapi
        deja_actif = False
        while not self._evt_arret.wait(0.02):
            try:
                actif = winapi.touche_enfoncee(winapi.VK_PAUSE) or (
                    winapi.touche_enfoncee(winapi.VK_CONTROL)
                    and winapi.touche_enfoncee(winapi.VK_MENU)
                    and winapi.touche_enfoncee(winapi.VK_X))
            except Exception:
                actif = False
            if actif and not deja_actif:
                self._moteur.urgence()
            deja_actif = actif
