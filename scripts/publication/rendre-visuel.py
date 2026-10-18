#!/usr/bin/env python3
"""Rend un visuel SVG en PNG ou en WebP avec les polices de la charte.

Usage : rendre-visuel.py ENTREE.svg SORTIE.png|SORTIE.webp

Prérequis : resvg (https://github.com/linebender/resvg) ; pour une sortie
WebP, cwebp (paquet « webp ») ou ImageMagick. Affiche le fichier produit.
"""

import sys
from pathlib import Path

from commun import visuels


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    svg, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    visuels.rendre(svg, sortie)
    print(sortie)


if __name__ == "__main__":
    main()
