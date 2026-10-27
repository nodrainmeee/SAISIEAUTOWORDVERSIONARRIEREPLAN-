"""Tests du mode arrière-plan (COM) avec un faux Word : aucune application réelle utilisée."""

import time
import unittest

from autosaisie import libelles as L
from autosaisie.rythme import MODE_RAPIDE
from autosaisie.saisie import Etat, MoteurSaisie
from autosaisie.word_com import CibleWord


class FauxErreurCom(Exception):
    def __init__(self, hresult):
        self.hresult = hresult


class FausseZone:
    def __init__(self, doc, debut):
        self.doc, self.debut, self.End = doc, debut, debut

    def InsertAfter(self, texte):
        t = self.doc.texte
        self.doc.texte = t[:self.debut] + texte + t[self.debut:]
        self.End = self.debut + len(texte)


class FauxDocument:
    def __init__(self, nom="C:\\Docs\\test.docx", texte="Début.\r"):
        self.FullName, self.texte = nom, texte
        self.ProtectionType, self.ReadOnly = -1, False

    @property
    def Content(self):
        class _C:
            pass
        c = _C()
        c.End = len(self.texte) + 0
        return c

    def Range(self, a, b):
        return FausseZone(self, a)


class FausseSelection:
    Start = 6


class FausseApplication:
    def __init__(self, doc):
        self.ActiveDocument = doc
        self.Documents = [doc]
        self.Selection = FausseSelection()
        self.erreur = None  # exception levée par les accès (Word occupé, fermé…)

    def __getattribute__(self, nom):
        if nom in ("ActiveDocument", "Documents") and object.__getattribute__(self, "erreur"):
            raise object.__getattribute__(self, "erreur")
        return object.__getattribute__(self, nom)


def moteur_arriere_plan(app, texte, fenetre=None, cps=5000):
    cible = CibleWord(lambda: app, lambda: True, lambda: None)
    m = MoteurSaisie(lambda: fenetre, lambda t: self_fail(t),
                     fabrique_arriere_plan=lambda: cible)
    m.configurer(texte, MODE_RAPIDE, cps, 5, 3, arriere_plan=True)
    return m, cible


def self_fail(_):
    raise AssertionError("Le clavier ne doit pas être utilisé en mode arrière-plan")


class TestArrierePlan(unittest.TestCase):
    def test_saisie_continue_meme_si_une_autre_fenetre_est_active(self):
        from tests.test_securite_word import CHROME
        doc = FauxDocument()
        m, _ = moteur_arriere_plan(FausseApplication(doc), "Été : ça\nmarche.", fenetre=CHROME)
        m.demarrer(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.TERMINEE)
        self.assertEqual(doc.texte, "Début.Été : ça\rmarche.\r")  # inséré au curseur de départ (6)

    def test_refus_si_aucun_document(self):
        app = FausseApplication(FauxDocument())
        app.erreur = FauxErreurCom(-2147352567)
        m, _ = moteur_arriere_plan(app, "abc")
        m.demarrer(0)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.ERREUR_WORD)
        self.assertEqual(m.message, L.MSG_ARRIERE_REQUIS)
        self.assertEqual(m.position, 0)

    def test_refus_document_protege_ou_lecture_seule(self):
        for attribut, valeur in (("ProtectionType", 2), ("ReadOnly", True)):
            doc = FauxDocument()
            setattr(doc, attribut, valeur)
            m, _ = moteur_arriere_plan(FausseApplication(doc), "abc")
            m.demarrer(0)
            m.attendre_fin()
            self.assertEqual(m.etat, Etat.ERREUR_WORD)
            self.assertEqual(doc.texte, "Début.\r")

    def test_suspension_si_word_devient_occupe_puis_reprise_explicite_sans_doublon(self):
        doc = FauxDocument()
        app = FausseApplication(doc)
        m, cible = moteur_arriere_plan(app, "abcdefghij" * 20, cps=200)
        m.demarrer(0)
        time.sleep(0.15)
        app.erreur = FauxErreurCom(-2147418111)  # Word occupé (boîte de dialogue)
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.SUSPENDUE)
        self.assertEqual(m.message, L.MSG_ARRIERE_SUSPENDU)
        figee = doc.texte
        pos = m.position
        self.assertTrue(0 < pos < 200)
        app.erreur = None  # Word répond de nouveau : aucune reprise automatique
        time.sleep(0.3)
        self.assertEqual(m.etat, Etat.SUSPENDUE)
        self.assertEqual(doc.texte, figee)
        self.assertTrue(m.reprendre(0))
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.TERMINEE)
        self.assertEqual(doc.texte, "Début." + "abcdefghij" * 20 + "\r")

    def test_suspension_si_le_document_a_ete_raccourci(self):
        doc = FauxDocument()
        app = FausseApplication(doc)
        m, _ = moteur_arriere_plan(app, "x" * 400, cps=200)
        m.demarrer(0)
        time.sleep(0.1)
        doc.texte = ""  # l'utilisateur a supprimé le contenu du document
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.SUSPENDUE)

    def test_arret_conserve_le_texte_source(self):
        doc = FauxDocument()
        m, _ = moteur_arriere_plan(FausseApplication(doc), "z" * 400, cps=100)
        m.demarrer(0)
        time.sleep(0.1)
        m.arreter()
        m.attendre_fin()
        self.assertEqual(m.etat, Etat.ARRETEE)
        self.assertEqual(m.texte, "z" * 400)


if __name__ == "__main__":
    unittest.main()
