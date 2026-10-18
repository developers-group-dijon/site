#!/usr/bin/env python3
"""Contrôle les commandes d'un commentaire d'issue de publication.

Usage : verifier-commandes.py ISSUE AUTEUR COMMENTAIRE_ID < commentaire

Le texte du commentaire est lu sur l'entrée standard. Si au moins une
commande est valide (auteur membre, syntaxe correcte, étape en cours),
pose « publication:a-traiter » et réagit 👍 au commentaire. Répond en
commentaire pour chaque commande ignorée. Un commentaire sans commande
est laissé tel quel.

Affiche « a-traiter » si le label est posé, rien sinon.
"""

import sys

from commun import commandes, etapes, github, membres


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    issue, auteur, commentaire_id = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    corps = sys.stdin.read()

    labels = github.labels(issue)
    if etapes.REFUSEE in labels:
        return
    lues = commandes.lire(corps)
    if not lues:
        if commandes.ressemble(corps):
            github.commenter(issue, f"@{auteur}, commande non reconnue.\n\n{commandes.AIDE}")
        return
    if not membres.est_membre(auteur):
        github.commenter(issue, f"@{auteur}, commande ignorée : la validation des publications est "
                                "réservée aux membres de l'association (liste dans "
                                "`scripts/publication/membres.txt`).")
        return

    etape = etapes.etape_en_cours(labels)
    erreurs = [e for e in (commandes.erreur(c, etape) for c in lues) if e]
    if len(erreurs) < len(lues):
        github.ajouter_label(issue, etapes.A_TRAITER)
        github.approuver(commentaire_id)
        print("a-traiter")
    if erreurs:
        debut = "certaines commandes sont ignorées" if len(erreurs) < len(lues) else "commande ignorée"
        github.commenter(issue, f"@{auteur}, {debut} :\n\n" + "\n".join(f"- {e}" for e in erreurs))


if __name__ == "__main__":
    main()
