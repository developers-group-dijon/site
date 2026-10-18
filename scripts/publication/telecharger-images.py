#!/usr/bin/env python3
"""Télécharge les images jointes au texte d'une issue.

Usage : telecharger-images.py ISSUE DOSSIER

Enregistre dans DOSSIER les images glissées dans l'issue (PNG, JPEG, GIF ou
WebP, 15 Mo au plus, 10 au plus) sous les noms image-1.png, image-2.jpg…,
avec LISEZMOI.txt qui fait la correspondance avec leur adresse. Une image
inaccessible est signalée et ignorée.

Affiche le nom des fichiers enregistrés.
"""

import re
import sys
import urllib.request
from pathlib import Path

from commun import github

PIECES_JOINTES = re.compile(
    r"https://(?:github\.com/user-attachments/(?:assets|files)/[\w-]+(?:/[^\s)\"'<>]*)?"
    r"|(?:private-)?user-images\.githubusercontent\.com/[^\s)\"'<>]+)"
)
TAILLE_MAX = 15 * 1024 * 1024
EXTENSIONS = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp"}


def telecharger(url: str) -> tuple[str, bytes]:
    requete = urllib.request.Request(url, headers={"User-Agent": "dgd-publication"})
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        return reponse.headers.get_content_type(), reponse.read(TAILLE_MAX + 1)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    issue, dossier = int(sys.argv[1]), Path(sys.argv[2])
    corps = github.lire_issue(issue, "body")["body"] or ""
    dossier.mkdir(parents=True, exist_ok=True)

    correspondances = []
    for i, url in enumerate(list(dict.fromkeys(PIECES_JOINTES.findall(corps)))[:10], 1):
        try:
            type_mime, donnees = telecharger(url)
        except Exception as exc:  # une image inaccessible n'empêche pas la suite
            print(f"image non téléchargée ({url}) : {exc}", file=sys.stderr)
            continue
        if type_mime not in EXTENSIONS or len(donnees) > TAILLE_MAX:
            print(f"pièce jointe ignorée ({type_mime}, {len(donnees)} octets) : {url}", file=sys.stderr)
            continue
        nom = f"image-{i}.{EXTENSIONS[type_mime]}"
        (dossier / nom).write_bytes(donnees)
        correspondances.append(f"{url} → {nom}")
        print(nom)
    (dossier / "LISEZMOI.txt").write_text(
        "Images fournies dans l'issue :\n" + ("\n".join(correspondances) or "(aucune)") + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
