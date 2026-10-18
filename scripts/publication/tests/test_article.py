"""Tests du front matter : python3 -m unittest discover -s scripts/publication"""

import unittest

from commun import article

ADOC = '---\ntitle: "Tremplin"\nslug: "tremplin"\nimage: "a.webp"\n---\n\nimage: dans le texte\n'


class FrontMatter(unittest.TestCase):
    def test_remplacer(self):
        resultat = article.remplacer_champ(ADOC, "image", '"b.webp"')
        self.assertEqual(resultat, ADOC.replace('image: "a.webp"', 'image: "b.webp"'))

    def test_ajouter(self):
        resultat = article.remplacer_champ(ADOC, "date", "2026-10-18T10:00:00+02:00")
        self.assertTrue(resultat.startswith("---\ndate: 2026-10-18T10:00:00+02:00\ntitle"))

    def test_lire(self):
        self.assertEqual(article.lire_champ(ADOC, "slug"), "tremplin")
        self.assertEqual(article.lire_champ("---\nslug: sans-guillemets\n---\n", "slug"), "sans-guillemets")
        self.assertEqual(article.lire_champ(ADOC, "auteur"), "")


if __name__ == "__main__":
    unittest.main()
