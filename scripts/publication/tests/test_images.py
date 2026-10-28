"""Tests des images de l'issue dans l'article : python3 -m unittest discover -s scripts/publication"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from commun import images

ARTICLE = """---
title: "Titre"
image: "mon-slug.webp"
---

Intro.

image::image-1.webp[Les intervenants devant le public]

Une icône image:image-2.webp[Logo,20] en ligne, et image::image-1.webp[Encore] une seconde fois.
"""

MAGICK = shutil.which("magick") or shutil.which("convert")


class References(unittest.TestCase):
    def test_macros_bloc_et_en_ligne_sans_doublon(self):
        self.assertEqual(images.references(ARTICLE), ["image-1.webp", "image-2.webp"])

    def test_champ_image_du_front_matter_ignore(self):
        self.assertEqual(images.references('---\nimage: "mon-slug.webp"\n---\n'), [])


class Sources(unittest.TestCase):
    def setUp(self):
        self.entree = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.entree)
        (self.entree / "image-1.jpg").write_bytes(b"jpeg")
        (self.entree / "LISEZMOI.txt").write_text("…")

    def test_image_fournie_trouvee(self):
        self.assertEqual(images.source("image-1.webp", self.entree), self.entree / "image-1.jpg")

    def test_cibles_refusees(self):
        for cible in ("image-3.webp", "image-1.jpg", "../entree/image-1.webp", "https://exemple.fr/a.webp",
                      "LISEZMOI.webp"):
            with self.subTest(cible=cible):
                self.assertIsNone(images.source(cible, self.entree))

    def test_problemes(self):
        self.assertEqual(images.problemes("image::image-1.webp[Photo]\n", self.entree), [])
        erreurs = images.problemes("image::image-1.webp[Photo]\nimage::https://exemple.fr/a.png[X]\n",
                                   self.entree)
        self.assertEqual(len(erreurs), 1)
        self.assertIn("https://exemple.fr/a.png", erreurs[0])


@unittest.skipUnless(MAGICK, "ImageMagick absent")
class Conversion(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dossier)
        self.entree = self.dossier / "entree"
        self.entree.mkdir()
        subprocess.run([MAGICK, "-size", "2000x500", "xc:#c2456a", str(self.entree / "image-1.jpg")], check=True)
        subprocess.run([MAGICK, "-size", "300x200", "xc:#ffd93d", str(self.entree / "image-2.png")], check=True)

    def largeur(self, image: Path) -> int:
        return int(subprocess.run([MAGICK, "identify", "-format", "%w", str(image)] if MAGICK.endswith("magick")
                                  else ["identify", "-format", "%w", str(image)],
                                  capture_output=True, text=True, check=True).stdout)

    def test_placer_convertit_reduit_et_nettoie(self):
        (self.dossier / "image-2.webp").write_bytes(b"ancienne version")
        (self.dossier / "mon-slug.webp").write_bytes(b"vignette")
        places = images.placer("image::image-1.webp[Photo]\n", self.entree, self.dossier)
        self.assertEqual(places, ["image-1.webp"])
        self.assertEqual(self.largeur(self.dossier / "image-1.webp"), images.LARGEUR)
        self.assertFalse((self.dossier / "image-2.webp").exists())  # plus citée
        self.assertTrue((self.dossier / "mon-slug.webp").exists())  # vignette intacte

    def test_petite_image_non_agrandie(self):
        images.placer("image::image-2.webp[Photo]\n", self.entree, self.dossier)
        self.assertEqual(self.largeur(self.dossier / "image-2.webp"), 300)


if __name__ == "__main__":
    unittest.main()
