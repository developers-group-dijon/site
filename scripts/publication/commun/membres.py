"""Membres de l'association autorisés à publier (scripts/publication/membres.txt)."""

from pathlib import Path

FICHIER = Path(__file__).resolve().parent.parent / "membres.txt"


def identifiant(login: str) -> str:
    """Identifiant GitHub normalisé : minuscules, sans « @ » ni suffixe « [bot] »
    (l'API GraphQL renvoie les bots sans, l'API REST avec)."""
    login = login.strip().lstrip("@").lower()
    return login.removesuffix("[bot]")


def lire(fichier: Path = FICHIER) -> set[str]:
    """Identifiants du fichier, sans les commentaires ni les lignes vides."""
    lignes = fichier.read_text(encoding="utf-8").splitlines()
    return {identifiant(ligne.split("#")[0]) for ligne in lignes if ligne.split("#")[0].strip()}


def est_membre(login: str, fichier: Path = FICHIER) -> bool:
    return identifiant(login) in lire(fichier)
