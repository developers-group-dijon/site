#!/usr/bin/env python3
"""Contrôle les propositions d'une étape et fait leurs rendus PNG.

Usage : controler-propositions.py ETAPE DOSSIER

DOSSIER contient les fichiers produits par Claude pour ETAPE (site ou
linkedin, voir commun/propositions.py). Supprime les brouillons (« _* »),
vérifie que les fichiers attendus sont là, que meta.json est lisible (avec un
slug valide pour le site), que chaque SVG est sûr et que l'article ne cite
que des images fournies dans l'issue (../entree/, voir commun/images.py),
puis rend chaque visuel en PNG à côté de son SVG.

Affiche les rendus produits ; s'arrête avec un message au premier problème.
"""

import json
import sys
from pathlib import Path

from commun import images, propositions, visuels


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in propositions.VISUEL:
        sys.exit(__doc__)
    etape, dossier = sys.argv[1], Path(sys.argv[2])

    for brouillon in dossier.glob("_*"):
        brouillon.unlink()
    if manquants := [f for f in propositions.attendus(etape) if not (dossier / f).exists()]:
        sys.exit(f"fichiers absents dans {dossier} : {', '.join(manquants)}")
    try:
        meta = propositions.meta(dossier)
    except json.JSONDecodeError as exc:
        sys.exit(f"meta.json illisible : {exc}")
    if etape == "site" and not propositions.SLUG.fullmatch(meta.get("slug") or ""):
        sys.exit(f"slug invalide dans meta.json : {meta.get('slug')!r}")
    if etape == "site":
        adoc = (dossier / propositions.TEXTE["site"]).read_text(encoding="utf-8")
        if erreurs := images.problemes(adoc, dossier.parent / "entree"):
            sys.exit("index.adoc : " + " ; ".join(erreurs))

    svgs = [dossier / propositions.visuel(etape, i) for i in propositions.NUMEROS]
    for svg in svgs:
        if probleme := visuels.controler(svg.read_text(encoding="utf-8")):
            sys.exit(f"{svg.name} : {probleme}")
    for svg in svgs:
        visuels.rendre(svg, svg.with_suffix(".png"))
        print(svg.with_suffix(".png"))


if __name__ == "__main__":
    main()
