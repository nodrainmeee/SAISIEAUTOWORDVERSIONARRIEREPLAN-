"""Importation et traitement du texte (.txt et .docx)."""

import os

from . import libelles as L


class ErreurImportation(Exception):
    """Erreur d'importation avec un message déjà compréhensible (français)."""


def normaliser_fins_de_ligne(texte: str) -> str:
    """Convertit les fins de ligne Windows/Mac en '\\n'. Ne change rien d'autre."""
    return texte.replace("\r\n", "\n").replace("\r", "\n")


def decoder_octets(donnees: bytes) -> str:
    """Détecte l'encodage le plus probable et décode en préservant les accents."""
    if donnees.startswith(b"\xef\xbb\xbf"):
        return donnees.decode("utf-8-sig")
    if donnees.startswith((b"\xff\xfe", b"\xfe\xff")):
        return donnees.decode("utf-16")
    try:
        return donnees.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        return donnees.decode("cp1252")
    except UnicodeDecodeError:
        return donnees.decode("latin-1")


def lire_txt(chemin: str) -> str:
    try:
        with open(chemin, "rb") as f:
            donnees = f.read()
        return normaliser_fins_de_ligne(decoder_octets(donnees))
    except (OSError, UnicodeError) as exc:
        raise ErreurImportation(L.MSG_FICHIER_ILLISIBLE) from exc


def lire_docx(chemin: str) -> str:
    """Extrait paragraphes et tableaux d'un .docx, dans l'ordre du document."""
    try:
        import docx  # python-docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise ErreurImportation(L.MSG_DEPENDANCE_MANQUANTE) from exc

    try:
        document = docx.Document(chemin)
        lignes = []
        for element in document.element.body.iterchildren():
            balise = element.tag.rsplit("}", 1)[-1]
            if balise == "p":
                lignes.append(Paragraph(element, document).text)
            elif balise == "tbl":
                table = Table(element, document)
                for rangee in table.rows:
                    cellules = []
                    precedente = None
                    for cellule in rangee.cells:
                        # Les cellules fusionnées se répètent : on les ignore.
                        if cellule._tc is precedente:
                            continue
                        precedente = cellule._tc
                        cellules.append(cellule.text.replace("\n", " "))
                    lignes.append("\t".join(cellules))
        return normaliser_fins_de_ligne("\n".join(lignes))
    except ErreurImportation:
        raise
    except Exception as exc:  # fichier corrompu, non .docx, etc.
        raise ErreurImportation(L.MSG_FICHIER_ILLISIBLE) from exc


def importer_fichier(chemin: str) -> str:
    extension = os.path.splitext(chemin)[1].lower()
    if extension == ".txt":
        return lire_txt(chemin)
    if extension == ".docx":
        return lire_docx(chemin)
    raise ErreurImportation(L.MSG_FICHIER_ILLISIBLE)


def texte_est_vide(texte: str) -> bool:
    return not texte or not texte.strip()
