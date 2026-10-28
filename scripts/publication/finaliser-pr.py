#!/usr/bin/env python3
"""Finalise la Pull Request d'une publication une fois LinkedIn validé.

Usage : finaliser-pr.py ISSUE

À lancer quand /visuel-linkedin N et /texte-linkedin ok sont acquis, sur la
copie de travail de la branche (preparer-issue.py). Réécrit la branche à
partir de la base à jour, en deux commits sans les propositions :

1. « Annonce : <titre> » : index.adoc, la vignette <slug>.webp et les images
   de l'issue citées dans l'article ;
2. « LinkedIn : visuel et texte du post » : linkedin.png et linkedin.txt.

Construit le site si Hugo est installé (la CI le fait de toute façon), pousse
la branche, passe la Pull Request en « prête » et l'annonce dans l'issue.
La Pull Request est alors fusionnable en fast-forward.

Affiche le commit poussé.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from commun import depot, etat, github, images, propositions, visuels

LINKEDIN_VISUEL = "linkedin.png"
LINKEDIN_TEXTE = "linkedin.txt"


def verifier_site(copie: Path) -> None:
    if not shutil.which("hugo"):
        print("Hugo absent : la CI vérifiera la construction du site", file=sys.stderr)
        return
    with tempfile.TemporaryDirectory() as public:
        for commande in (["hugo", "build", "--minify", "--quiet", "--destination", public],
                         ["scripts/verifier-site.sh", public]):
            res = subprocess.run(commande, cwd=copie, text=True, capture_output=True)
            if res.returncode != 0:
                print(f"⚠ construction locale du site en échec, la CI le signalera aussi :\n{res.stderr}",
                      file=sys.stderr)
                return


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    numero = int(sys.argv[1])
    issue = etat.lire(numero)
    publication, visuel = issue["publication"], issue["linkedin"]["visuel"]
    if not publication or not issue["linkedin"]["valide"]:
        sys.exit("le visuel et le texte LinkedIn ne sont pas validés")

    copie = depot.copie(numero)
    attendu = depot.git("rev-parse", "HEAD", cwd=copie)
    relatif = f"content/posts/{publication['dossier']}"
    dossier = copie / relatif
    meta = propositions.meta(dossier / "propositions/site")
    slug = meta["slug"]
    adoc = (dossier / "index.adoc").read_text(encoding="utf-8")
    annonce = ["index.adoc", f"{slug}.webp", *images.placer(adoc, dossier / "propositions/entree", dossier)]

    with tempfile.TemporaryDirectory() as nom:
        garde = Path(nom)
        for fichier in annonce:
            shutil.copyfile(dossier / fichier, garde / fichier)
        visuels.rendre(dossier / "propositions/linkedin" / propositions.visuel("linkedin", visuel),
                       garde / LINKEDIN_VISUEL)
        shutil.copyfile(dossier / "propositions/linkedin/texte.txt", garde / LINKEDIN_TEXTE)

        # Repartir de la base à jour : la Pull Request sera fusionnable en fast-forward.
        depot.git("reset", "--quiet", "--hard", depot.BASE, cwd=copie)
        depot.git("clean", "--quiet", "-fdx", "--", relatif, cwd=copie)
        if dossier.exists():
            sys.exit(f"{relatif} existe déjà sur {depot.BASE} : à régler à la main")
        dossier.mkdir(parents=True)
        for fichier in annonce:
            shutil.copyfile(garde / fichier, dossier / fichier)
        depot.commiter(copie, f"Annonce : {meta.get('titre') or issue['titre']}\n\n"
                              f"Rédigée à partir de l'issue #{numero}.\n\n"
                              # Ferme l'issue quand le commit arrive sur main, même
                              # par un merge fast-forward poussé à la main.
                              f"Closes #{numero}\n", relatif)
        for fichier in (LINKEDIN_VISUEL, LINKEDIN_TEXTE):
            shutil.copyfile(garde / fichier, dossier / fichier)
        depot.commiter(copie, f"LinkedIn : visuel et texte du post\n\nValidés dans l'issue #{numero}.\n", relatif)

    verifier_site(copie)
    sha = depot.pousser(copie, publication["branche"], attendu)
    github.ecrire("pr", "ready", str(publication["pr"]))
    github.commenter(numero, f"Visuel {visuel} et texte LinkedIn validés. La Pull Request #{publication['pr']} "
                             "est réécrite en deux commits (article, puis LinkedIn), sans les propositions, "
                             "et prête à être relue et mergée.\n")
    print(sha)


if __name__ == "__main__":
    main()
