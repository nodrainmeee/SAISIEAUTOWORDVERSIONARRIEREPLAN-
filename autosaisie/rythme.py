"""Découpage du texte en groupes et calcul des délais (modes rapide et humain)."""

import random

MODE_RAPIDE = "rapide"
MODE_HUMAIN = "humain"

TOUCHES_SPECIALES = "\n\t"
FIN_DE_PHRASE = ".!?…"
PONCTUATION_LEGERE = ",;:"


def prochain_groupe(texte: str, position: int, taille: int) -> str:
    """Retourne le prochain groupe de caractères (jamais vide si position valide).

    Un retour à la ligne ou une tabulation est toujours envoyé seul.
    """
    taille = max(1, int(taille))
    if texte[position] in TOUCHES_SPECIALES:
        return texte[position]
    fin = position
    while fin < len(texte) and fin - position < taille and texte[fin] not in TOUCHES_SPECIALES:
        fin += 1
    return texte[position:fin]


def delai_apres(groupe: str, mode: str, cps: float, intensite: float,
                alea: random.Random) -> float:
    """Durée (en secondes) à attendre après l'envoi d'un groupe."""
    cps = max(1.0, float(cps))
    base = len(groupe) / cps
    if mode != MODE_HUMAIN:
        return base

    facteur = max(0.0, min(10.0, float(intensite))) / 5.0  # 1.0 = intensité moyenne
    delai = base * alea.uniform(0.6, 1.5)
    dernier = groupe[-1]
    if dernier == " " and alea.random() < 0.15 * facteur:
        delai += alea.uniform(0.15, 0.5) * facteur
    elif dernier in PONCTUATION_LEGERE:
        delai += alea.uniform(0.05, 0.25) * facteur
    elif dernier in FIN_DE_PHRASE:
        delai += alea.uniform(0.2, 0.7) * facteur
    elif dernier == "\n":
        delai += alea.uniform(0.4, 1.4) * facteur
    if alea.random() < 0.01 * facteur:  # courte hésitation aléatoire
        delai += alea.uniform(0.4, 1.2) * facteur
    return delai
