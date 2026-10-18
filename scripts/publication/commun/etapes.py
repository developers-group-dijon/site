"""Labels des issues de publication et étape qu'ils indiquent.

Une demande de publication passe par ces étapes, chacune marquée par un label :

    attente → site → linkedin → prete → publiee

« publication:a-traiter » signale en plus qu'une action attend le traitement
(nouvelle demande ou commande valide), « publication:refusee » qu'une demande
vient d'une personne absente de la liste des membres.
"""

A_TRAITER = "publication:a-traiter"
REFUSEE = "publication:refusee"

# Nom : (couleur, description). Créés par creer-labels.py.
LABELS = {
    "publication": ("c2456a", "Demande de publication sur le site (formulaires d'issue)"),
    "type:evenement": ("9a1a41", "Publication : annonce d'un événement"),
    "type:news": ("ffb7c1", "Publication : actualité"),
    A_TRAITER: ("ffd93d", "Une action attend le traitement de la publication"),
    REFUSEE: ("717171", "Demande d'une personne absente de la liste des membres"),
    "publication:site": ("fff5f7", "PR en brouillon ; propositions pour le site en cours de validation"),
    "publication:linkedin": ("fff5f7", "PR en brouillon ; propositions LinkedIn en cours de validation"),
    "publication:prete": ("2da44e", "PR prête à être relue et mergée"),
    "publication:publiee": ("212121", "Publiée sur le site ; texte LinkedIn fourni"),
}

# De la plus avancée à la moins avancée : la première trouvée l'emporte.
ETAPES = ("publiee", "prete", "linkedin", "site")


def etape_en_cours(labels: set[str]) -> str:
    """« attente » tant que les propositions pour le site ne sont pas publiées."""
    for etape in ETAPES:
        if f"publication:{etape}" in labels:
            return etape
    return "attente"
