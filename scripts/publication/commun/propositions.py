"""Fichiers d'une proposition, tels que Claude les produit pour une étape.

    site/       proposition-1.svg … proposition-3.svg, index.adoc, meta.json
    linkedin/   carre-1.svg … carre-3.svg, texte.txt, meta.json

meta.json : {"slug" et "titre" (site seulement), "questions": [...], "notes": "..."}.
Les fichiers qui commencent par « _ » sont des brouillons de Claude, jamais publiés.
"""

import hashlib
import json
import re
from pathlib import Path

SITE = "https://www.developers-group-dijon.fr"
VISUEL = {"site": "proposition", "linkedin": "carre"}
TEXTE = {"site": "index.adoc", "linkedin": "texte.txt"}
NUMEROS = (1, 2, 3)
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def visuel(etape: str, numero: int) -> str:
    return f"{VISUEL[etape]}-{numero}.svg"


def attendus(etape: str) -> list[str]:
    return [visuel(etape, i) for i in NUMEROS] + [TEXTE[etape], "meta.json"]


def url_article(slug: str) -> str:
    return f"{SITE}/{slug}/"


def meta(dossier: Path) -> dict:
    return json.loads((dossier / "meta.json").read_text(encoding="utf-8"))


def empreinte(contenu: bytes) -> str:
    return hashlib.sha256(contenu).hexdigest()[:16]


def empreinte_texte(texte: str) -> str:
    """Sans les champs « image » et « date » du front matter, que les scripts
    réécrivent eux-mêmes : ils ne doivent pas invalider une validation."""
    return empreinte(re.sub(r"(?m)^(image|date):.*\n", "", texte).encode())


def empreintes(dossier: Path, etape: str) -> dict:
    """Empreintes des trois visuels et du texte : "1", "2", "3", "texte"."""
    resultat = {str(i): empreinte((dossier / visuel(etape, i)).read_bytes()) for i in NUMEROS}
    resultat["texte"] = empreinte_texte((dossier / TEXTE[etape]).read_text(encoding="utf-8"))
    return resultat
