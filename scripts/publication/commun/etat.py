"""État d'une issue de publication, reconstruit à partir de ses commentaires.

Rien n'est stocké ailleurs que dans l'issue. Chaque commentaire de
propositions porte un marqueur invisible avec la version et les empreintes
des fichiers proposés :

    <!-- publication {"etape":"site","version":2,"empreintes":{"1":"…","texte":"…"}} -->

Le premier porte aussi la branche et la Pull Request de la publication :

    <!-- publication {"etape":"pr","pr":12,"branche":"evenement/42-slug","dossier":"2026-10-18-slug"} -->

Les commandes des membres (/visuel-site 2…) s'appliquent à la dernière
version proposée. Une validation reste acquise après une nouvelle version
si l'élément validé n'a pas changé (même empreinte).
"""

import json
import os
import re
from dataclasses import dataclass, field

from commun import commandes, etapes, github, membres

MARQUEUR = re.compile(r"<!-- publication (\{.*?\}) -->")
# Bot de la GitHub App dans Actions (ex. « dgd-publication[bot] ») : ses
# commentaires de propositions sont reconnus sans qu'il soit membre.
BOT = os.environ.get("PUBLICATION_BOT", "")


def marqueur(donnees: dict) -> str:
    return f"<!-- publication {json.dumps(donnees, separators=(',', ':'))} -->"


@dataclass
class Etape:
    version: int = 0  # 0 : rien de proposé
    empreintes: dict = field(default_factory=dict)  # "1", "2", "3", "texte" → empreinte
    visuel: int | None = None  # visuel retenu
    texte_ok: bool = False
    consignes: list[str] = field(default_factory=list)  # /modifier-… depuis la dernière version

    @property
    def valide(self) -> bool:
        return self.version > 0 and self.visuel is not None and self.texte_ok

    def nouvelle_version(self, version: int, empreintes: dict) -> None:
        if self.visuel is not None and empreintes.get(str(self.visuel)) != self.empreintes.get(str(self.visuel)):
            self.visuel = None
        if self.texte_ok and empreintes.get("texte") != self.empreintes.get("texte"):
            self.texte_ok = False
        self.version, self.empreintes, self.consignes = version, empreintes, []

    def appliquer(self, commande: commandes.Commande) -> None:
        if self.version == 0 or commandes.erreur_syntaxe(commande):
            return
        if commande.verbe == "visuel":
            self.visuel = int(commande.argument)
        elif commande.verbe == "texte":
            self.texte_ok = True
        else:
            self.consignes.append(commande.argument)


def rejouer(commentaires: list[dict], auteurs_membres: set[str], bots: set[str]) -> tuple[dict, dict | None]:
    """Rejoue les commentaires dans l'ordre : propositions (marqueurs écrits par
    un membre ou un bot reconnu) et commandes des membres. Les autres sont ignorés.

    Renvoie les étapes ({"site": Etape, "linkedin": Etape}) et la publication
    ({"pr", "branche", "dossier"}, ou None avant la première proposition)."""
    suivi = {"site": Etape(), "linkedin": Etape()}
    publication = None
    for c in sorted(commentaires, key=lambda c: c.get("createdAt", "")):
        auteur = membres.identifiant((c.get("author") or {}).get("login") or "")
        est_membre = auteur in auteurs_membres
        if not est_membre and auteur not in bots:
            continue
        corps = c.get("body") or ""
        marqueurs = MARQUEUR.findall(corps)
        for brut in marqueurs:
            try:
                donnees = json.loads(brut)
            except json.JSONDecodeError:
                continue
            etape = donnees.pop("etape", None)
            if etape in suivi:
                suivi[etape].nouvelle_version(int(donnees.get("version", 0)), donnees.get("empreintes", {}))
            elif etape == "pr":
                publication = donnees
        if marqueurs or not est_membre:
            continue  # un commentaire de propositions ne valide rien
        for commande in commandes.lire(corps):
            suivi[commande.etape].appliquer(commande)
    return suivi, publication


def lire(numero: int) -> dict:
    """État complet de l'issue, sous une forme sérialisable en JSON."""
    issue = github.lire_issue(numero, "number,title,body,author,labels,comments,state")
    labels = {label["name"] for label in issue["labels"]}
    bots = {membres.identifiant(BOT)} if BOT else set()
    suivi, publication = rejouer(issue["comments"], membres.lire(), bots)
    return {
        "numero": issue["number"],
        "titre": issue["title"],
        "corps": issue["body"] or "",
        "auteur": issue["author"]["login"],
        "ouverte": issue["state"] == "OPEN",
        "type": "evenement" if "type:evenement" in labels else "news" if "type:news" in labels else None,
        "labels": sorted(labels),
        "etape": etapes.etape_en_cours(labels),
        "publication": publication,
        **{nom: {**vars(e), "valide": e.valide} for nom, e in suivi.items()},
    }
