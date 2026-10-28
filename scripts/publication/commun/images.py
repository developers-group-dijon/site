"""Images de l'issue insérées dans le corps de l'article.

Claude cite une image fournie `../entree/image-2.jpg` sous la forme
`image::image-2.webp[texte alternatif]` : même nom, extension .webp. Les
scripts la convertissent alors en WebP dans le dossier de l'article,
redressée selon l'orientation de l'appareil photo, réduite à LARGEUR pixels
de large au plus et sans métadonnées (position GPS comprise).

La conversion passe par ImageMagick ; à défaut, cwebp convertit sans
redresser ni réduire l'image (avec un avertissement).
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

LARGEUR = 1200
QUALITE = "82"
SOURCES = (".jpg", ".jpeg", ".png", ".gif", ".webp")
# image::cible[…] (bloc) ou image:cible[…] (en ligne). Le champ « image: "…" »
# du front matter n'est pas concerné : un espace suit les deux-points.
REFERENCE = re.compile(r"(?<![\w/])image::?([^\s\[\]]+)\[")


def references(adoc: str) -> list[str]:
    """Cibles des macros image de l'article, dans l'ordre, sans doublon."""
    return list(dict.fromkeys(REFERENCE.findall(adoc)))


def source(cible: str, entree: Path) -> Path | None:
    """Image fournie dans l'issue qui correspond à une cible « image-N.webp »."""
    nom = Path(cible)
    if nom.suffix != ".webp" or nom.name != cible:
        return None
    for extension in SOURCES:
        candidat = entree / f"{nom.stem}{extension}"
        if candidat.is_file():
            return candidat
    return None


def problemes(adoc: str, entree: Path) -> list[str]:
    """Images citées par l'article qui ne correspondent à aucune image fournie."""
    return [f"« {cible} » : l'article ne peut citer que les images fournies dans l'issue, "
            "sous la forme image::image-N.webp[texte alternatif]"
            for cible in references(adoc) if source(cible, entree) is None]


def convertir(image: Path, sortie: Path) -> None:
    magick = shutil.which("magick") or shutil.which("convert")
    if magick:
        # [0] : première image d'un GIF animé.
        commande = [magick, f"{image}[0]", "-auto-orient", "-resize", f"{LARGEUR}x>", "-strip",
                    "-quality", QUALITE, str(sortie)]
    elif shutil.which("cwebp") and image.suffix != ".gif":
        print(f"⚠ ImageMagick absent : {image.name} n'est ni redressée ni réduite", file=sys.stderr)
        commande = ["cwebp", "-quiet", "-q", QUALITE, "-metadata", "none", str(image), "-o", str(sortie)]
    else:
        sys.exit(f"impossible de convertir {image.name} : installer ImageMagick")
    res = subprocess.run(commande, text=True, capture_output=True)
    if res.returncode != 0:
        sys.exit(f"échec de la conversion de {image.name} : {(res.stderr or res.stdout).strip()}")


def placer(adoc: str, entree: Path, dossier: Path) -> list[str]:
    """Convertit dans `dossier` les images fournies que cite l'article, et
    supprime celles d'une version précédente qui ne sont plus citées.
    Renvoie les noms des images placées."""
    citees = [c for c in references(adoc) if source(c, entree)]
    for ancienne in dossier.glob("*.webp"):
        if ancienne.name not in citees and source(ancienne.name, entree):
            ancienne.unlink()
    for cible in citees:
        convertir(source(cible, entree), dossier / cible)
    return citees
