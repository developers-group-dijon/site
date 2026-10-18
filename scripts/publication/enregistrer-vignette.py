#!/usr/bin/env python3
"""Enregistre dans l'article la vignette et le texte validés pour le site.

Usage : enregistrer-vignette.py ISSUE

À lancer quand /visuel-site N et /texte-site ok sont acquis, sur la copie de
travail de la branche (preparer-issue.py). Rend la proposition N en
<slug>.webp dans le dossier de l'article, y fait pointer le champ « image »,
met « date » à l'heure actuelle, puis commite et pousse la branche.

Affiche le commit poussé.
"""

import sys

from commun import article, depot, etat, propositions, visuels


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    numero = int(sys.argv[1])
    issue = etat.lire(numero)
    publication, visuel = issue["publication"], issue["site"]["visuel"]
    if not publication or not issue["site"]["valide"]:
        sys.exit("le visuel et le texte du site ne sont pas validés")

    copie = depot.copie(numero)
    attendu = depot.git("rev-parse", "HEAD", cwd=copie)
    dossier = copie / "content/posts" / publication["dossier"]
    slug = propositions.meta(dossier / "propositions/site")["slug"]
    visuels.rendre(dossier / "propositions/site" / propositions.visuel("site", visuel), dossier / f"{slug}.webp")
    index = dossier / "index.adoc"
    adoc = article.remplacer_champ(index.read_text(encoding="utf-8"), "image", f'"{slug}.webp"')
    index.write_text(article.remplacer_champ(adoc, "date", article.maintenant()), encoding="utf-8")

    depot.commiter(copie, f"Vignette {visuel} et texte de l'article validés\n\nIssue #{numero}.\n",
                   str(dossier.relative_to(copie)))
    print(depot.pousser(copie, publication["branche"], attendu))


if __name__ == "__main__":
    main()
