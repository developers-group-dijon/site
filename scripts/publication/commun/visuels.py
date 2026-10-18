"""Rendu et contrôle des visuels SVG de publication.

Le rendu passe par resvg avec les seules polices de polices/ : il est
identique sur toutes les machines. Une sortie WebP est convertie ensuite
par cwebp, ou par ImageMagick à défaut.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

POLICES = Path(__file__).resolve().parent.parent / "polices"

# Script, contenu HTML, gestionnaire d'événement ou ressource distante.
INTERDIT = re.compile(r"<script|<foreignObject|\bon[a-z]+\s*=|https?://(?!www\.w3\.org/)", re.I)


def outils_manquants() -> list[str]:
    manquants = [] if shutil.which("resvg") else ["resvg"]
    if not any(shutil.which(o) for o in ("cwebp", "magick", "convert")):
        manquants.append("cwebp (ou ImageMagick)")
    return manquants


def controler(svg: str) -> str | None:
    """Ce qui rend le SVG dangereux à publier, ou None s'il est sûr."""
    trouve = INTERDIT.search(svg)
    return f"élément interdit « {trouve.group(0)} »" if trouve else None


def lancer(*cmd: str) -> None:
    res = subprocess.run(cmd, text=True, capture_output=True)
    if res.returncode != 0:
        sys.exit(f"échec de {cmd[0]} : {(res.stderr or res.stdout).strip()}")


def rendre(svg: Path, sortie: Path) -> None:
    """Rend svg en sortie (.png ou .webp). Les images liées dans le SVG sont
    cherchées relativement à son dossier."""
    if svg.suffix != ".svg" or not svg.is_file():
        sys.exit(f"fichier SVG introuvable : {svg}")
    if sortie.suffix not in (".png", ".webp"):
        sys.exit(f"la sortie doit être un fichier .png ou .webp : {sortie}")
    if manquants := outils_manquants():
        sys.exit("outils introuvables : " + ", ".join(manquants))
    if sortie.suffix == ".png":
        rendre_png(svg, sortie)
        return
    with tempfile.TemporaryDirectory() as dossier:
        png = Path(dossier) / "rendu.png"
        rendre_png(svg, png)
        if shutil.which("cwebp"):
            lancer("cwebp", "-quiet", "-q", "85", str(png), "-o", str(sortie))
        else:
            lancer(shutil.which("magick") or "convert", str(png), "-quality", "85", str(sortie))


def rendre_png(svg: Path, png: Path) -> None:
    # Aucune police système : seules celles de la charte existent au rendu.
    lancer("resvg", "--skip-system-fonts", "--use-fonts-dir", str(POLICES),
           "--sans-serif-family", "Noto Sans", "--monospace-family", "Bitcount Grid Single",
           str(svg), str(png))
