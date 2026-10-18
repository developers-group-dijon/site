"""Tests des membres et des étapes : python3 -m unittest discover -s scripts/publication"""

import tempfile
import unittest
from pathlib import Path

from commun import etapes, membres


class Membres(unittest.TestCase):
    def test_lecture(self):
        with tempfile.TemporaryDirectory() as dossier:
            fichier = Path(dossier) / "membres.txt"
            fichier.write_text("# commentaire\n\nAlice  # présidente\n  bob\n", encoding="utf-8")
            self.assertEqual(membres.lire(fichier), {"alice", "bob"})
            self.assertTrue(membres.est_membre("@ALICE", fichier))
            self.assertFalse(membres.est_membre("carole", fichier))

    def test_identifiant(self):
        self.assertEqual(membres.identifiant(" Dgd-Publication[bot] "), "dgd-publication")

    def test_fichier_du_depot(self):
        self.assertTrue(membres.lire())


class Etapes(unittest.TestCase):
    def test_etape_la_plus_avancee(self):
        self.assertEqual(etapes.etape_en_cours({"publication"}), "attente")
        self.assertEqual(etapes.etape_en_cours({"publication:site"}), "site")
        self.assertEqual(etapes.etape_en_cours({"publication:site", "publication:linkedin"}), "linkedin")
        self.assertEqual(etapes.etape_en_cours({"publication:prete", "publication:publiee"}), "publiee")

    def test_labels_des_etapes_definis(self):
        for etape in etapes.ETAPES:
            self.assertIn(f"publication:{etape}", etapes.LABELS)


if __name__ == "__main__":
    unittest.main()
