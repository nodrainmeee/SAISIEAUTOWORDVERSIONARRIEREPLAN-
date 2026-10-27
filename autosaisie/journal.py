"""Journal technique local, facultatif. Ne contient jamais le texte saisi."""

import os
import time

_actif = False


def activer(actif: bool) -> None:
    global _actif
    _actif = bool(actif)


def est_actif() -> bool:
    return _actif


def chemin_journal() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    dossier = os.path.join(base, "AutoSaisieWord")
    os.makedirs(dossier, exist_ok=True)
    return os.path.join(dossier, "journal.log")


def ecrire(code: str) -> None:
    """Écrit un code technique court (jamais de contenu de document)."""
    if not _actif:
        return
    try:
        with open(chemin_journal(), "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + code + "\n")
    except OSError:
        pass
