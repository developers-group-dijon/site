"""Dépôt git et dossier de travail d'une issue de publication.

    .publication/issue-42/
      depot/            copie de travail (git worktree) : branche de la publication, ou base
      propositions/     dossier de travail de Claude, hors du dépôt
        ressources/     logos de l'association
        entree/         images jointes à l'issue
        site/           proposition-1..3.svg, index.adoc, meta.json
        linkedin/       carre-1..3.svg, texte.txt, meta.json

.publication/ est ignoré par git et peut être supprimé à tout moment :
tout ce qui compte est sur GitHub.

La base des branches de publication est origin/main, ou PUBLICATION_BASE
(par exemple origin/feat/… pour essayer l'outillage avant son merge).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
TRAVAIL = RACINE / ".publication"
BASE = os.environ.get("PUBLICATION_BASE", "origin/main")


def git(*args: str, cwd: Path = RACINE, verifier: bool = True) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if verifier and res.returncode != 0:
        sys.exit(f"échec de « git {' '.join(args[:3])} » : {(res.stderr or res.stdout).strip()}")
    return res.stdout.strip()


def dossier(issue: int) -> Path:
    return TRAVAIL / f"issue-{issue}"


def copie(issue: int) -> Path:
    return dossier(issue) / "depot"


def propositions(issue: int) -> Path:
    return dossier(issue) / "propositions"


def preparer_copie(issue: int, branche: str | None) -> Path:
    """Copie de travail propre : sur la branche de la publication si elle
    existe, sinon sur la base. Claude y trouve CLAUDE.md, les règles et
    les skills du dépôt."""
    chemin = copie(issue)
    if chemin.exists():
        git("worktree", "remove", "--force", str(chemin), verifier=False)
        shutil.rmtree(chemin, ignore_errors=True)
    git("worktree", "prune")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    git("fetch", "--quiet", "origin")
    depart = BASE
    if branche:
        git("fetch", "--quiet", "origin", f"+refs/heads/{branche}:refs/remotes/origin/{branche}")
        depart = f"origin/{branche}"
    git("worktree", "add", "--quiet", "--detach", str(chemin), depart)
    if branche:
        git("switch", "--quiet", "--no-track", "-C", branche, depart, cwd=chemin)
    return chemin


def sha_distant(branche: str) -> str:
    """Dernier commit de la branche sur GitHub, ou "" si elle n'existe pas."""
    sortie = git("ls-remote", "--heads", "origin", branche)
    return sortie.split()[0] if sortie else ""


def pousser(chemin: Path, branche: str, attendu: str) -> str:
    """Pousse HEAD sur la branche si personne ne l'a modifiée depuis `attendu`
    ("" : la branche ne doit pas exister). Renvoie le commit poussé."""
    git("push", "--quiet", f"--force-with-lease=refs/heads/{branche}:{attendu}", "origin",
        f"HEAD:refs/heads/{branche}", cwd=chemin)
    return git("rev-parse", "HEAD", cwd=chemin)


def commiter(chemin: Path, message: str, *fichiers: str) -> None:
    git("add", "-A", *fichiers, cwd=chemin)
    res = subprocess.run(["git", "commit", "--quiet", "-F", "-"], cwd=chemin, input=message, text=True,
                         capture_output=True)
    if res.returncode != 0:
        sys.exit(f"échec du commit : {(res.stderr or res.stdout).strip()}")
