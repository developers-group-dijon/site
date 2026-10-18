#!/usr/bin/env python3
"""Affiche en JSON l'état d'une issue de publication.

Usage : etat-issue.py ISSUE

État reconstruit à partir des labels et des commentaires (voir commun/etat.py) :
étape en cours, branche et Pull Request de la publication, et pour chaque
étape (site, linkedin) la version proposée, le visuel retenu, la validation
du texte et les consignes de modification en attente.
"""

import json
import sys

from commun import etat


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(json.dumps(etat.lire(int(sys.argv[1])), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
