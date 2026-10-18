"""Tests des commandes de validation : python3 -m unittest discover -s scripts/publication"""

import unittest

from commun import commandes


def erreurs(corps: str, etape: str) -> list[str | None]:
    return [commandes.erreur(c, etape) for c in commandes.lire(corps)]


class Lecture(unittest.TestCase):
    def test_une_commande_par_ligne(self):
        lues = commandes.lire("Merci !\n/visuel-site 2\r\n  /texte-site OK  \n")
        self.assertEqual([(c.verbe, c.etape, c.argument) for c in lues],
                         [("visuel", "site", "2"), ("texte", "site", "OK")])

    def test_consigne_sur_plusieurs_lignes(self):
        lues = commandes.lire("/modifier-site titre plus court\nfond rose\n/visuel-site 1")
        self.assertEqual(lues[0].argument, "titre plus court\nfond rose")
        self.assertEqual(lues[1].verbe, "visuel")

    def test_commande_au_milieu_d_une_ligne_ignoree(self):
        self.assertEqual(commandes.lire("je propose /visuel-site 2"), [])

    def test_ressemblance(self):
        self.assertTrue(commandes.ressemble("/visuel-site2"))
        self.assertTrue(commandes.ressemble("ok\n/texte-blog ok"))
        self.assertFalse(commandes.ressemble("rien à signaler"))


class Controle(unittest.TestCase):
    def test_commandes_valides(self):
        self.assertEqual(erreurs("/visuel-site 3\n/texte-site ok\n/modifier-site plus court", "site"),
                         [None, None, None])

    def test_syntaxe(self):
        for corps in ("/visuel-site 4", "/visuel-site", "/texte-site oui", "/modifier-site"):
            with self.subTest(corps=corps):
                self.assertIsNotNone(erreurs(corps, "site")[0])

    def test_consigne_sur_la_ligne_suivante_acceptee(self):
        self.assertEqual(erreurs("/modifier-linkedin\nplus court", "linkedin"), [None])

    def test_etape(self):
        self.assertIn("pas encore publiées", erreurs("/visuel-site 1", "attente")[0])
        self.assertIn("LinkedIn commencera", erreurs("/visuel-linkedin 1", "site")[0])
        self.assertIn("est close", erreurs("/texte-site ok", "linkedin")[0])
        self.assertIsNotNone(erreurs("/texte-linkedin ok", "publiee")[0])

    def test_syntaxe_avant_etape(self):
        self.assertIn("1, 2 ou 3", erreurs("/visuel-linkedin 9", "site")[0])


if __name__ == "__main__":
    unittest.main()
