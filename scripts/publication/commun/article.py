"""Front matter d'un article Asciidoc (content/posts/…/index.adoc)."""

import datetime as dt
import re


def remplacer_champ(adoc: str, champ: str, valeur: str) -> str:
    """Remplace la valeur d'un champ du front matter, ou l'ajoute en tête."""
    motif = re.compile(rf"(?m)^{champ}:.*$")
    if motif.search(adoc):
        return motif.sub(lambda _: f"{champ}: {valeur}", adoc, count=1)
    return re.sub(r"\A---\n", lambda _: f"---\n{champ}: {valeur}\n", adoc, count=1)


def lire_champ(adoc: str, champ: str) -> str:
    """Valeur d'un champ du front matter, sans guillemets ("" si absent)."""
    trouve = re.search(rf"(?m)^{champ}:\s*\"?([^\"\n]*?)\"?\s*$", adoc)
    return trouve.group(1) if trouve else ""


def maintenant() -> str:
    """Date et heure locales au format du front matter."""
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
