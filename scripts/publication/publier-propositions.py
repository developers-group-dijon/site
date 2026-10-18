#!/usr/bin/env python3
"""Publie les propositions d'une étape : sur la branche, puis dans l'issue.

Usage : publier-propositions.py ISSUE ETAPE

Les propositions doivent être contrôlées (controler-propositions.py). Au
premier passage, crée la branche de la publication (evenement/N-slug ou
article/N-slug) et son dossier content/posts/AAAA-MM-JJ-slug/.

1. Copie les propositions dans le dossier de la publication, sous
   propositions/ ; pour le site, le texte proposé devient l'article, avec la
   proposition 1 comme vignette provisoire (aperçu sur le site de test).
2. Commite et pousse la branche.
3. Au premier passage, ouvre la Pull Request en brouillon.
4. Commente l'issue : visuels (liens figés sur le commit), texte, questions
   et commandes de validation, avec le marqueur lu par commun/etat.py.

Affiche le commit poussé.
"""

import datetime as dt
import shutil
import sys

from commun import article, depot, etat, github, propositions


def creer_branche(issue: dict, copie, slug: str) -> dict:
    prefixe = "evenement" if issue["type"] == "evenement" else "article"
    publication = {"pr": None, "branche": f"{prefixe}/{issue['numero']}-{slug}",
                   "dossier": f"{dt.date.today().isoformat()}-{slug}"}
    depot.git("switch", "--quiet", "--no-track", "-C", publication["branche"], depot.BASE, cwd=copie)
    return publication


def ranger(etape: str, sortie, dossier_article, travail) -> None:
    cible = dossier_article / "propositions"
    for sous in ("ressources", "entree"):
        if (travail / sous).is_dir() and not (cible / sous).exists():
            shutil.copytree(travail / sous, cible / sous)
    shutil.rmtree(cible / etape, ignore_errors=True)
    shutil.copytree(sortie, cible / etape, ignore=shutil.ignore_patterns("index.adoc", "_*"))
    if etape == "site":
        adoc = (sortie / "index.adoc").read_text(encoding="utf-8")
        adoc = article.remplacer_champ(adoc, "image", '"propositions/site/proposition-1.png"')
        (dossier_article / "index.adoc").write_text(adoc, encoding="utf-8")


def ouvrir_pr(issue: dict, publication: dict, meta: dict) -> int:
    dossier = f"content/posts/{publication['dossier']}"
    existante = github.gh_json("pr", "list", "--head", publication["branche"], "--state", "open",
                               "--json", "number")
    if existante:
        return existante[0]["number"]
    corps = (
        etat.marqueur({"issue": issue["numero"], "dossier": publication["dossier"]}) + "\n"
        f"Publication préparée à partir de l'issue #{issue['numero']}.\n\n"
        f"- Article : `{dossier}/index.adoc`\n"
        f"- Adresse après publication : {propositions.url_article(meta['slug'])}\n\n"
        "Tant que la Pull Request est en **brouillon**, les propositions (visuels et textes) "
        f"sont dans `{dossier}/propositions/` et se valident dans l'issue. "
        "Une fois LinkedIn validé, l'historique est réécrit en deux commits (article, puis "
        "LinkedIn), les propositions sont retirées et la Pull Request passe en « prête ».\n\n"
        "Pensez à vérifier la date de publication souhaitée dans l'issue avant de merger.\n"
    )
    url = github.ecrire("pr", "create", "--draft", "--base", depot.BRANCHE_BASE, "--head", publication["branche"],
                        "--title", meta.get("titre") or issue["titre"], "--label", "publication",
                        "--body-file", "-", entree=corps)
    return int(url.rstrip("/").rsplit("/", 1)[-1]) if url else 0


def commentaire(issue: dict, etape: str, version: int, publication: dict, sortie, sha: str,
                empreintes: dict, nom_depot: str) -> str:
    avant = issue[etape]
    meta = propositions.meta(sortie)
    nom = "le site" if etape == "site" else "LinkedIn"
    marqueurs = [{"etape": etape, "version": version, "empreintes": empreintes}]
    if etape == "site" and version == 1:
        marqueurs.insert(0, {"etape": "pr", **publication})
    lignes = [etat.marqueur(m) for m in marqueurs] + [f"## Propositions pour {nom} — version {version}", ""]
    if etape == "site" and version == 1:
        lignes += [f"Pull Request en brouillon : #{publication['pr']} (branche `{publication['branche']}`).", ""]
    if etape == "linkedin" and version == 1:
        lignes += [f"Vignette {issue['site']['visuel']} et texte de l'article validés "
                   "et enregistrés dans la Pull Request.", ""]
    if meta.get("notes"):
        lignes += [meta["notes"], ""]
    for i in propositions.NUMEROS:
        png = f"content/posts/{publication['dossier']}/propositions/{etape}/{propositions.visuel(etape, i)}"
        png = png.removesuffix(".svg") + ".png"
        # Lien figé sur le commit : chaque version garde ses images.
        url = f"https://raw.githubusercontent.com/{nom_depot}/{sha}/{png}"
        garde = " — *inchangé, toujours retenu*" if (
            avant["visuel"] == i and avant["empreintes"].get(str(i)) == empreintes[str(i)]) else ""
        lignes += [f"### Visuel {i}{garde}", "", f"![Visuel {i}]({url})", ""]
    texte = (sortie / propositions.TEXTE[etape]).read_text(encoding="utf-8").rstrip()
    garde = " — *inchangé, toujours validé*" if (
        avant["texte_ok"] and avant["empreintes"].get("texte") == empreintes["texte"]) else ""
    lignes += [f"### Texte{garde}", "", f"````{'asciidoc' if etape == 'site' else 'text'}", texte, "````", ""]
    if meta.get("questions"):
        lignes += ["### À confirmer", "", *[f"- {q}" for q in meta["questions"]], ""]
    suite = ("la vignette est enregistrée dans l'article et les propositions LinkedIn sont préparées"
             if etape == "site" else "le visuel et le texte sont ajoutés à la Pull Request, qui sera prête à merger")
    lignes += [
        "### Pour valider", "",
        "Répondez en commentaire, une commande par ligne :", "",
        f"- `/visuel-{etape} N` pour choisir le visuel N ;",
        f"- `/texte-{etape} ok` pour valider le texte ;",
        f"- `/modifier-{etape} votre consigne` pour une nouvelle version "
        "(« titre plus court », « visuel 2 avec fond rose »…).", "",
        f"Quand le visuel et le texte sont validés, {suite}.",
    ]
    return "\n".join(lignes) + "\n"


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in propositions.VISUEL:
        sys.exit(__doc__)
    numero, etape = int(sys.argv[1]), sys.argv[2]
    issue = etat.lire(numero)
    copie, travail = depot.copie(numero), depot.propositions(numero)
    sortie = travail / etape
    version = issue[etape]["version"] + 1

    publication = issue["publication"]
    premiere = publication is None
    if premiere:
        if etape != "site":
            sys.exit("la première proposition est celle du site")
        publication = creer_branche(issue, copie, propositions.meta(sortie)["slug"])
    attendu = depot.sha_distant(publication["branche"])
    dossier_article = copie / "content/posts" / publication["dossier"]
    ranger(etape, sortie, dossier_article, travail)
    nom = "le site" if etape == "site" else "LinkedIn"
    depot.commiter(copie, f"Propositions pour {nom}, version {version}\n\nIssue #{numero}.\n",
                   str(dossier_article.relative_to(copie)))
    sha = depot.pousser(copie, publication["branche"], attendu)

    if premiere:
        publication["pr"] = ouvrir_pr(issue, publication, propositions.meta(sortie))
    empreintes = propositions.empreintes(sortie, etape)
    github.commenter(numero, commentaire(issue, etape, version, publication, sortie, sha, empreintes,
                                         github.nom_depot()))
    print(sha)


if __name__ == "__main__":
    main()
