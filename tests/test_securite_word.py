"""Tests de sécurité : la saisie ne doit jamais partir hors de Microsoft Word.

TESTS SIMULÉS : les fenêtres actives sont des objets factices et l'« envoyeur »
enregistre le texte dans une liste. Aucune frappe réelle n'est envoyée.
Un seul test lit réellement la fenêtre active (lecture seule) sous Windows.
"""

import os
import sys
import threading
import time
import unittest

from autosaisie import libelles as L
from autosaisie import securite
from autosaisie.rythme import MODE_RAPIDE
from autosaisie.saisie import Etat, MoteurSaisie
from autosaisie.securite import FenetreInfo, evaluer_fenetre, verifier_word_actif

FAUX_PID = os.getpid() + 1000


def fenetre(exe, classe="Autre"):
    return FenetreInfo(1, FAUX_PID, exe, classe)


WORD = fenetre(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE", "OpusApp")
CHROME = fenetre(r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome_WidgetWin_1")
EDGE = fenetre(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Chrome_WidgetWin_1")
CLAUDE = fenetre(r"C:\Users\x\AppData\Local\AnthropicClaude\claude.exe", "Chrome_WidgetWin_1")
BLOC_NOTES = fenetre(r"C:\Windows\System32\notepad.exe", "Notepad")
EXPLORATEUR = fenetre(r"C:\Windows\explorer.exe", "CabinetWClass")
CMD = fenetre(r"C:\Windows\System32\cmd.exe", "ConsoleWindowClass")
POWERSHELL = fenetre(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "ConsoleWindowClass")


class Scenario:
    """Fournisseur de fenêtres scripté + envoyeur qui enregistre au lieu de taper."""

    def __init__(self, sequence, ensuite=None):
        self.sequence = list(sequence)
        self.ensuite = ensuite
        self.appels = 0
        self.envoye = []

    def fournisseur(self):
        self.appels += 1
        if self.sequence:
            element = self.sequence.pop(0)
        else:
            element = self.ensuite
        if isinstance(element, Exception):
            raise element
        return element

    def envoyeur(self, texte):
        self.envoye.append(texte)


def moteur_pour(scenario, texte="Bonjour le monde, ceci est un test.", cps=2000):
    m = MoteurSaisie(scenario.fournisseur, scenario.envoyeur)
    m.configurer(texte, MODE_RAPIDE, cps, 5, 3)
    return m


class TestDecisionFenetre(unittest.TestCase):
    def test_word_autorise(self):
        self.assertEqual(evaluer_fenetre(WORD), (True, "ok"))

    def test_applications_refusees(self):
        for f in (CHROME, EDGE, CLAUDE, BLOC_NOTES, EXPLORATEUR, CMD, POWERSHELL):
            ok, code = evaluer_fenetre(f)
            self.assertFalse(ok, f.chemin_exe)
            self.assertEqual(code, "autre_application")

    def test_titre_contenant_word_ne_suffit_pas(self):
        # Le titre n'est jamais utilisé : un faux « Word » (autre exe) est refusé.
        faux = fenetre(r"C:\Temp\faux_word.exe", "OpusApp")
        self.assertFalse(evaluer_fenetre(faux)[0])

    def test_word_mais_boite_de_dialogue_refusee(self):
        dialogue = fenetre(WORD.chemin_exe, "#32770")
        self.assertEqual(evaluer_fenetre(dialogue), (False, "word_boite_de_dialogue_ou_autre_fenetre"))

    def test_processus_non_identifie_refuse(self):
        self.assertEqual(evaluer_fenetre(fenetre("", "OpusApp")), (False, "processus_non_identifie"))

    def test_aucune_fenetre_refuse(self):
        self.assertEqual(evaluer_fenetre(None), (False, "detection_echouee"))

    def test_exception_de_detection_refuse(self):
        def casse():
            raise RuntimeError("boum")
        self.assertEqual(verifier_word_actif(casse), (False, "detection_echouee"))

    def test_propre_fenetre_du_logiciel_refusee(self):
        moi = FenetreInfo(1, os.getpid(), WORD.chemin_exe, "OpusApp")
        self.assertFalse(evaluer_fenetre(moi)[0])


class TestDemarrage(unittest.TestCase):
    def test_refus_si_une_autre_application_est_active(self):
        for f in (CHROME, CLAUDE, BLOC_NOTES, EDGE, EXPLORATEUR, CMD, POWERSHELL):
            sc = Scenario([], ensuite=f)
            m = moteur_pour(sc)
            m.demarrer(0)
            m.attendre_fin()
            self.assertEqual(m.etat, Etat.ERREUR_WORD)
            self.assertEqual(m.message, L.MSG_WORD_REQUIS)
            self.assertEqual(sc.envoye, [], "Aucun caractère ne doit partir")
            self.assertEqual(m.position, 0)

    def test_demarrage_autorise_uniquement_si_word_actif(self):
        sc = Scenario([], ensuite=WORD)
        m = moteur_pour(sc, texte="Été : ça marche.\nLigne deux.")
        m.demarrer(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.TERMINEE)
        self.assertEqual("".join(sc.envoye), "Été : ça marche.\nLigne deux.")

    def test_texte_vide_refuse_sans_verifier_ni_envoyer(self):
        sc = Scenario([], ensuite=WORD)
        m = moteur_pour(sc, texte="   ")
        self.assertFalse(m.demarrer(0))
        self.assertEqual(m.message, L.MSG_TEXTE_VIDE)
        self.assertEqual(sc.envoye, [])

    def test_detection_en_echec_au_demarrage_n_envoie_rien(self):
        sc = Scenario([], ensuite=RuntimeError("x"))
        m = moteur_pour(sc)
        m.demarrer(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.ERREUR_WORD)
        self.assertEqual(sc.envoye, [])


class TestSuspensionEtReprise(unittest.TestCase):
    def suspendre(self, ensuite_apres=WORD):
        # Word pour la vérification de départ + 3 groupes, puis Chrome.
        sc = Scenario([WORD] * 4 + [CHROME], ensuite=CHROME)
        m = moteur_pour(sc, texte="abcdefghijklmnopqrstuvwxyz" * 3)
        m.demarrer(0)
        m.attendre_fin()
        return sc, m

    def test_suspension_quand_word_perd_le_focus(self):
        sc, m = self.suspendre()
        self.assertEqual(m.etat, Etat.SUSPENDUE)
        self.assertEqual(m.message, L.MSG_SUSPENDU)
        envoye = "".join(sc.envoye)
        self.assertEqual(envoye, m.texte[:len(envoye)])
        self.assertEqual(m.position, len(envoye))
        self.assertTrue(0 < m.position < len(m.texte))

    def test_pas_de_reprise_automatique_quand_word_redevient_actif(self):
        sc, m = self.suspendre()
        avant = list(sc.envoye)
        sc.sequence, sc.ensuite = [], WORD  # Word redevient la fenêtre active
        time.sleep(0.3)
        self.assertEqual(m.etat, Etat.SUSPENDUE)
        self.assertEqual(sc.envoye, avant)

    def test_reprise_refusee_si_word_n_est_pas_actif(self):
        sc, m = self.suspendre()
        avant = list(sc.envoye)
        pos = m.position
        self.assertTrue(m.reprendre(0))
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.SUSPENDUE)
        self.assertEqual(m.message, L.MSG_WORD_REQUIS)
        self.assertEqual(sc.envoye, avant)
        self.assertEqual(m.position, pos)

    def test_reprise_explicite_continue_sans_doublon_ni_perte(self):
        sc, m = self.suspendre()
        sc.sequence, sc.ensuite = [], WORD
        m.reprendre(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.TERMINEE)
        self.assertEqual("".join(sc.envoye), m.texte)

    def test_arret_de_l_envoi_si_la_detection_echoue_en_cours_de_route(self):
        sc = Scenario([WORD] * 3 + [RuntimeError("échec")], ensuite=WORD)
        m = moteur_pour(sc, texte="x" * 200)
        m.demarrer(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.SUSPENDUE)
        self.assertLess(len(sc.envoye), 5)
        self.assertLess(m.position, 200)

    def test_erreur_d_envoi_arrete_et_conserve_le_texte(self):
        def envoyeur_casse(_):
            raise OSError("échec")
        m = MoteurSaisie(lambda: WORD, envoyeur_casse)
        m.configurer("abc", MODE_RAPIDE, 100, 5, 3)
        m.demarrer(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.ERREUR)
        self.assertEqual(m.texte, "abc")


class TestPauseArretUrgence(unittest.TestCase):
    def moteur_lent(self):
        sc = Scenario([], ensuite=WORD)
        m = moteur_pour(sc, texte="a" * 400, cps=100)  # ~ 1 s pour 100 caractères
        return sc, m

    def attendre_etat(self, m, etat, delai=3.0):
        fin = time.monotonic() + delai
        while time.monotonic() < fin and m.etat != etat:
            time.sleep(0.01)
        self.assertEqual(m.etat, etat)

    def test_pause_puis_reprise_a_la_position_enregistree(self):
        sc, m = self.moteur_lent()
        m.demarrer(0)
        time.sleep(0.15)
        m.mettre_en_pause()
        self.attendre_etat(m, Etat.PAUSE)
        pos = m.position
        envoye = len(sc.envoye)
        time.sleep(0.2)
        self.assertEqual(len(sc.envoye), envoye, "Rien ne doit partir pendant la pause")
        self.assertEqual(m.texte, "a" * 400)
        m.reprendre(0)
        time.sleep(0.1)
        self.assertGreaterEqual(m.position, pos)
        m.arreter()
        m.attendre_fin()

    def test_arret_conserve_le_texte_et_arrete_l_envoi(self):
        sc, m = self.moteur_lent()
        m.demarrer(0)
        time.sleep(0.1)
        m.arreter()
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.ARRETEE)
        n = len(sc.envoye)
        time.sleep(0.2)
        self.assertEqual(len(sc.envoye), n)
        self.assertEqual(m.texte, "a" * 400)

    def test_arret_d_urgence(self):
        sc, m = self.moteur_lent()
        m.demarrer(0)
        time.sleep(0.1)
        m.urgence()
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.ARRETEE)
        self.assertEqual(m.message, L.MSG_ARRET_URGENCE)

    def test_interface_reste_reactive_demarrer_retourne_immediatement(self):
        sc, m = self.moteur_lent()
        debut = time.monotonic()
        m.demarrer(0)
        self.assertLess(time.monotonic() - debut, 0.2)
        self.assertTrue(m.en_cours())
        m.arreter()
        m.attendre_fin()

    def test_compte_a_rebours_interruptible(self):
        sc = Scenario([], ensuite=WORD)
        m = moteur_pour(sc)
        m.demarrer(30)
        self.assertEqual(m.etat, Etat.COMPTE_A_REBOURS)
        m.arreter()
        m.attendre_fin(2)
        self.assertEqual(m.etat, Etat.ARRETEE)
        self.assertEqual(sc.envoye, [])


@unittest.skipUnless(sys.platform == "win32", "Test réel : Windows uniquement")
class TestWindowsReel(unittest.TestCase):
    """Lecture seule de la fenêtre active (aucune frappe envoyée)."""

    def test_lecture_fenetre_active_ne_plante_pas_et_n_est_pas_word(self):
        info = securite.obtenir_fenetre_active()  # peut être None sans session de bureau
        if info is not None:
            self.assertFalse(evaluer_fenetre(info)[0])
        self.assertIn(securite.etat_word(), (securite.ETAT_FERME, securite.ETAT_NON_INSTALLE,
                                             securite.ETAT_OUVERT_NON_ACTIF, securite.ETAT_ACTIF))


if __name__ == "__main__":
    unittest.main()
