"""Tests de la reconstruction de l'état : python3 -m unittest discover -s scripts/publication"""

import unittest

from commun import etat

MEMBRES = {"alice", "bob"}
BOTS = {"dgd-publication"}


def propositions(auteur: str, etape: str, version: int, **empreintes) -> dict:
    empreintes = {"1": "a", "2": "b", "3": "c", "texte": "t", **empreintes}
    return {"author": {"login": auteur},
            "body": etat.marqueur({"etape": etape, "version": version, "empreintes": empreintes}) + "\n## Propositions"}


def commentaire(auteur: str, corps: str) -> dict:
    return {"author": {"login": auteur}, "body": corps}


def rejouer(*commentaires: dict):
    horodates = [{**c, "createdAt": f"2026-10-18T10:{i:02d}:00Z"} for i, c in enumerate(commentaires)]
    return etat.rejouer(horodates, MEMBRES, BOTS)


class Rejouer(unittest.TestCase):
    def test_validation(self):
        suivi, _ = rejouer(propositions("dgd-publication[bot]", "site", 1),
                           commentaire("Alice", "/visuel-site 2\n/texte-site ok"))
        self.assertEqual((suivi["site"].visuel, suivi["site"].texte_ok, suivi["site"].valide), (2, True, True))

    def test_commandes_avant_propositions_ignorees(self):
        suivi, _ = rejouer(commentaire("alice", "/visuel-site 2"), propositions("alice", "site", 1))
        self.assertIsNone(suivi["site"].visuel)

    def test_personnes_non_membres_ignorees(self):
        suivi, _ = rejouer(propositions("dgd-publication", "site", 1), commentaire("carole", "/texte-site ok"),
                           propositions("carole", "site", 7))
        self.assertEqual((suivi["site"].texte_ok, suivi["site"].version), (False, 1))

    def test_un_bot_ne_valide_rien(self):
        suivi, _ = rejouer(propositions("dgd-publication", "site", 1), commentaire("dgd-publication", "/texte-site ok"))
        self.assertFalse(suivi["site"].texte_ok)

    def test_validation_conservee_si_inchangee(self):
        suivi, _ = rejouer(propositions("alice", "site", 1),
                           commentaire("bob", "/visuel-site 2\n/texte-site ok\n/modifier-site visuel 3 en rose"),
                           propositions("alice", "site", 2, **{"3": "z"}))
        e = suivi["site"]
        self.assertEqual((e.version, e.visuel, e.texte_ok, e.consignes), (2, 2, True, []))

    def test_validation_perdue_si_modifiee(self):
        suivi, _ = rejouer(propositions("alice", "site", 1), commentaire("bob", "/visuel-site 2\n/texte-site ok"),
                           propositions("alice", "site", 2, **{"2": "z", "texte": "u"}))
        self.assertEqual((suivi["site"].visuel, suivi["site"].texte_ok), (None, False))

    def test_consignes_en_attente(self):
        suivi, _ = rejouer(propositions("alice", "linkedin", 1), commentaire("bob", "/modifier-linkedin plus court\net sans emoji"))
        self.assertEqual(suivi["linkedin"].consignes, ["plus court\net sans emoji"])

    def test_syntaxe_invalide_ignoree(self):
        suivi, _ = rejouer(propositions("alice", "site", 1), commentaire("bob", "/visuel-site 4\n/texte-site oui"))
        self.assertEqual((suivi["site"].visuel, suivi["site"].texte_ok), (None, False))

    def test_publication(self):
        pr = {"etape": "pr", "pr": 12, "branche": "evenement/42-test", "dossier": "2026-10-18-test"}
        _, publication = rejouer(commentaire("dgd-publication", etat.marqueur(pr)))
        self.assertEqual(publication, {"pr": 12, "branche": "evenement/42-test", "dossier": "2026-10-18-test"})


if __name__ == "__main__":
    unittest.main()
