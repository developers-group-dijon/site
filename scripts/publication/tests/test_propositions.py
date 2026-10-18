"""Tests des fichiers de propositions : python3 -m unittest discover -s scripts/publication"""

import tempfile
import unittest
from pathlib import Path

from commun import propositions


class Empreintes(unittest.TestCase):
    def test_image_et_date_ignorees(self):
        a = '---\ntitle: "A"\ndate: 2026-10-18T10:00:00+02:00\nimage: "propositions/site/proposition-1.png"\n---\nTexte\n'
        b = '---\ntitle: "A"\ndate: 2026-10-19T09:00:00+02:00\nimage: "a.webp"\n---\nTexte\n'
        self.assertEqual(propositions.empreinte_texte(a), propositions.empreinte_texte(b))
        self.assertNotEqual(propositions.empreinte_texte(a), propositions.empreinte_texte(a + "Suite\n"))

    def test_empreintes_d_une_etape(self):
        with tempfile.TemporaryDirectory() as nom:
            dossier = Path(nom)
            for i in (1, 2, 3):
                (dossier / f"carre-{i}.svg").write_text(f"<svg>{i}</svg>")
            (dossier / "texte.txt").write_text("Post")
            empreintes = propositions.empreintes(dossier, "linkedin")
        self.assertEqual(sorted(empreintes), ["1", "2", "3", "texte"])
        self.assertEqual(len(set(empreintes.values())), 4)


class Noms(unittest.TestCase):
    def test_attendus(self):
        self.assertEqual(propositions.attendus("site"),
                         ["proposition-1.svg", "proposition-2.svg", "proposition-3.svg", "index.adoc", "meta.json"])

    def test_slug(self):
        self.assertTrue(propositions.SLUG.fullmatch("tremplin-devfest-2026"))
        for slug in ("", "Tremplin", "a--b", "-a", "a/b"):
            self.assertIsNone(propositions.SLUG.fullmatch(slug))


if __name__ == "__main__":
    unittest.main()
