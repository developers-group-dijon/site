"""Tests du contrôle des SVG : python3 -m unittest discover -s scripts/publication"""

import unittest
from pathlib import Path

from commun import visuels

EXEMPLES = Path(__file__).resolve().parent.parent / "exemples"


class Controle(unittest.TestCase):
    def test_gabarits_acceptes(self):
        for svg in EXEMPLES.glob("*.svg"):
            with self.subTest(svg=svg.name):
                self.assertIsNone(visuels.controler(svg.read_text(encoding="utf-8")))

    def test_elements_interdits(self):
        for contenu in ('<script>alert(1)</script>', '<foreignObject><p/></foreignObject>',
                        '<rect onload="x()"/>', '<image href="https://exemple.fr/a.png"/>',
                        '<image href="http://www.w3.org.exemple.fr/a.png"/>'):
            with self.subTest(contenu=contenu):
                self.assertIsNotNone(visuels.controler(f"<svg>{contenu}</svg>"))

    def test_espace_de_noms_accepte(self):
        self.assertIsNone(visuels.controler('<svg xmlns="http://www.w3.org/2000/svg"/>'))


if __name__ == "__main__":
    unittest.main()
