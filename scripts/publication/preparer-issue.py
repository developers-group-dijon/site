#!/usr/bin/env python3
"""Prépare le dossier de travail d'une issue de publication.

Usage : preparer-issue.py ISSUE

Crée .publication/issue-ISSUE/ (voir commun/depot.py) :
- depot/ : copie de travail sur la branche de la publication, ou sur la base
  avant la première proposition ;
- propositions/ : reprend les propositions de la branche (la version en cours
  sert de point de départ), ou à neuf les logos de ressources/.

Les images jointes à l'issue sont téléchargées à part (telecharger-images.py).
Affiche le chemin du dossier de travail.
"""

import shutil
import sys
from pathlib import Path

from commun import depot, etat

RESSOURCES = Path(__file__).resolve().parent / "ressources"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    issue = int(sys.argv[1])
    publication = etat.lire(issue)["publication"]

    copie = depot.preparer_copie(issue, publication["branche"] if publication else None)
    propositions = depot.propositions(issue)
    shutil.rmtree(propositions, ignore_errors=True)
    if publication:
        article = copie / "content/posts" / publication["dossier"]
        shutil.copytree(article / "propositions", propositions)
        # Le texte proposé pour le site est l'article lui-même.
        (propositions / "site").mkdir(exist_ok=True)
        shutil.copyfile(article / "index.adoc", propositions / "site/index.adoc")
    else:
        propositions.mkdir(parents=True)
        shutil.copytree(RESSOURCES, propositions / "ressources")
    print(depot.dossier(issue))


if __name__ == "__main__":
    main()
