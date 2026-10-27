"""Saisie « en arrière-plan » : le texte est inséré directement dans le document Word
par l'automatisation COM (comme une macro), sans simuler le clavier.

Word peut donc être réduit ou masqué. Le texte ne peut aller que dans Word.
Les bibliothèques Windows sont importées à la demande : ce module reste importable
(et testable) sur n'importe quel système.
"""

from typing import Callable, Optional, Tuple

from . import libelles as L

SANS_PROTECTION = -1  # wdNoProtection
HRESULT_APPEL_REJETE = (-2147418111, -2147417846)  # Word occupé (boîte de dialogue, etc.)


def _fabrique_application_word():
    import win32com.client  # pywin32
    return win32com.client.GetActiveObject("Word.Application")


def _initialiser_com() -> bool:
    try:
        import pythoncom
        pythoncom.CoInitialize()
        return True
    except ImportError:
        return False


def _liberer_com() -> None:
    try:
        import pythoncom
        pythoncom.CoUninitialize()
    except ImportError:
        pass


class CibleWord:
    """Écrit dans le document Word choisi au démarrage, à partir du curseur de départ.

    La position d'insertion est mémorisée : une reprise continue exactement où la
    saisie s'était arrêtée, sans doublon ni perte.
    """

    message_demarrage = L.MSG_ARRIERE_REQUIS
    message_suspension = L.MSG_ARRIERE_SUSPENDU

    def __init__(self, fabrique_application: Optional[Callable[[], object]] = None,
                 initialiser_com: Callable[[], bool] = _initialiser_com,
                 liberer_com: Callable[[], None] = _liberer_com):
        self._fabrique = fabrique_application or _fabrique_application_word
        self._init_com = initialiser_com
        self._lib_com = liberer_com
        self._com_actif = False
        self.nom_document: Optional[str] = None
        self.position: Optional[int] = None
        self._app = None
        self._doc = None

    # --- Cycle de vie (appelé dans le fil de saisie : COM est lié au fil) ---

    def ouvrir(self, reprise: bool) -> Tuple[bool, str]:
        self._com_actif = bool(self._init_com())
        try:
            self._app = self._fabrique()
            if reprise and self.nom_document is not None:
                self._doc = self._trouver_document(self.nom_document)
                if self._doc is None:
                    return False, "document_introuvable"
            else:
                self._doc = self._app.ActiveDocument
                self.nom_document = str(self._doc.FullName)
                self.position = int(self._app.Selection.Start)
            return self._controles()
        except Exception as exc:
            return False, self._code_erreur(exc)

    def verifier(self) -> Tuple[bool, str]:
        try:
            return self._controles()
        except Exception as exc:
            return False, self._code_erreur(exc)

    def envoyer(self, texte: str) -> None:
        zone = self._doc.Range(self.position, self.position)
        zone.InsertAfter(texte.replace("\n", "\r"))  # \r = nouveau paragraphe dans Word
        self.position = int(zone.End)

    def fermer(self) -> None:
        self._app = None
        self._doc = None
        if self._com_actif:
            self._lib_com()
            self._com_actif = False

    # --- Interne ---

    def _trouver_document(self, nom: str):
        for document in self._app.Documents:
            if str(document.FullName) == nom:
                return document
        return None

    def _controles(self) -> Tuple[bool, str]:
        doc = self._doc
        if doc is None or self._app is None:
            return False, "document_introuvable"
        if self._trouver_document(self.nom_document) is None:
            return False, "document_introuvable"
        if int(doc.ProtectionType) != SANS_PROTECTION or bool(doc.ReadOnly):
            return False, "document_protege"
        if self.position is None or self.position > int(doc.Content.End) - 1:
            return False, "document_modifie"
        return True, "ok"

    @staticmethod
    def _code_erreur(exc: Exception) -> str:
        hresult = getattr(exc, "hresult", None)
        if hresult in HRESULT_APPEL_REJETE:
            return "word_occupe"
        return "word_indisponible"
