"""Commandes de validation écrites en commentaire d'une issue de publication.

Une commande par ligne, en début de ligne : /visuel-site 2, /texte-linkedin ok,
/modifier-site titre plus court… La consigne de /modifier-… peut continuer
sur les lignes suivantes, jusqu'à la commande suivante.
"""

import re
from dataclasses import dataclass

COMMANDE = re.compile(r"^/(visuel|texte|modifier)-(site|linkedin)(?:[ \t]+(.*))?$")
# Début de ligne qui ressemble à une commande sans en être une (« /visuel-site2 »…).
RESSEMBLANCE = re.compile(r"(?m)^\s*/(visuel|texte|modifier)")

AIDE = """Commandes disponibles, une par ligne, en début de commentaire :

| Commande | Effet |
|---|---|
| `/visuel-site N` | Choisit la vignette N (1, 2 ou 3) |
| `/texte-site ok` | Valide le texte de l'article |
| `/modifier-site …` | Demande de nouvelles propositions pour le site, selon la consigne qui suit |
| `/visuel-linkedin N` | Choisit le visuel LinkedIn N (1, 2 ou 3) |
| `/texte-linkedin ok` | Valide le texte du post LinkedIn |
| `/modifier-linkedin …` | Demande de nouvelles propositions LinkedIn, selon la consigne qui suit |

Une étape passe à la suivante quand son visuel **et** son texte sont validés. Une nouvelle commande `/visuel-…` remplace la précédente tant que l'étape n'est pas close."""

# Pourquoi une commande ne s'applique pas, selon l'étape en cours (commun.etapes).
HORS_ETAPE = {
    "attente": "les propositions pour le site ne sont pas encore publiées.",
    "site": "l'étape LinkedIn commencera une fois le visuel et le texte du site validés.",
    "linkedin": "l'étape site est close, la vignette et le texte sont enregistrés dans la Pull Request. "
                "Pour une retouche de l'article, commentez la Pull Request.",
    "prete": "les validations sont terminées et la Pull Request est prête. "
             "Pour une retouche, commentez la Pull Request.",
    "publiee": "la publication est terminée, plus aucune commande n'est prise en compte.",
}


@dataclass
class Commande:
    verbe: str  # visuel, texte ou modifier
    etape: str  # site ou linkedin
    argument: str  # numéro, « ok » ou consigne
    ligne: str  # ligne d'origine, pour les messages


def lire(corps: str) -> list[Commande]:
    commandes: list[Commande] = []
    for ligne in corps.replace("\r\n", "\n").split("\n"):
        trouve = COMMANDE.match(ligne.strip())
        if trouve:
            verbe, etape, argument = trouve.groups()
            commandes.append(Commande(verbe, etape, (argument or "").strip(), ligne.strip()))
        elif commandes and commandes[-1].verbe == "modifier":
            commandes[-1].argument = (commandes[-1].argument + "\n" + ligne).strip()
    return commandes


def ressemble(corps: str) -> bool:
    """Vrai si une ligne commence comme une commande, reconnue ou non."""
    return RESSEMBLANCE.search(corps) is not None


def erreur(commande: Commande, etape_en_cours: str) -> str | None:
    """Pourquoi la commande est ignorée, ou None si elle est valide."""
    c = commande
    if c.verbe == "visuel" and c.argument not in ("1", "2", "3"):
        return f"`{c.ligne}` : indiquez le numéro de la proposition (1, 2 ou 3)."
    if c.verbe == "texte" and c.argument.lower() != "ok":
        return f"`{c.ligne}` : la seule valeur possible est `ok`."
    if c.verbe == "modifier" and not c.argument:
        return (f"`{c.ligne}` : ajoutez la consigne après la commande, "
                f"par exemple `/modifier-{c.etape} titre plus court, fond rose`.")
    if c.etape != etape_en_cours:
        return f"`{c.ligne}` : {HORS_ETAPE[etape_en_cours]}"
    return None
