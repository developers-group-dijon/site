# Règles de rédaction

Ces règles s'appliquent à tout texte rédigé ou modifié pour le site : articles (`content/posts/`), pages, résumés (`summary`), textes de `hugo.toml` et libellés des gabarits.

## 1. Partenaires cités : au moins un lien

Lorsqu'un texte cite un partenaire, au moins une de ses mentions (de préférence la première) est un lien vers son site.

- La liste de référence est `data/partenaires.yaml` : utiliser l'URL du champ `url`.
- Sont aussi concernés les sponsors, lieux d'accueil, écoles, entreprises et associations qui soutiennent un événement, même s'ils ne sont pas dans ce fichier. Utiliser alors leur site officiel. Si l'URL n'est pas certaine, la demander au lieu de l'inventer.
- Un partenaire sans `url` dans le fichier (par exemple Google Developer Groups) : demander l'adresse à utiliser, ou proposer de compléter `data/partenaires.yaml`.
- Syntaxe Asciidoc : `https://atolcd.com[Atol CD]`.
- Il suffit d'un lien par partenaire et par article ; les mentions suivantes peuvent rester en texte simple.

## 2. Écriture inclusive

Le texte s'adresse à toutes et à tous.

**Par défaut, la double forme**, écrite en toutes lettres :

- « les développeurs et les développeuses », « les participantes et les participants », « chacune et chacun », « toutes et tous » ;
- quand la phrase le permet, un seul déterminant suffit : « les développeuses et développeurs ».

**Les termes épicènes ou collectifs** sont aussi bienvenus, notamment pour éviter de répéter une double forme : « les personnes inscrites », « le public », « l'équipe », « les membres », « les bénévoles », « les speakers ».

**Le point médian** (« développeur·euse·s », « inscrit·e·s ») est réservé aux endroits où la place manque :

- titres (`title`, titres de section, titre de la page d'accueil) ;
- boutons et libellés de liens courts (`role=button`) ;
- éléments d'interface contraints (menu, bandeau, carte).

Hors de ces cas, il n'est pas utilisé : ni dans le corps d'un article, ni dans un `summary`, ni dans une meta description.

**À éviter** : le masculin seul pour désigner un groupe mixte (« les développeurs », « les participants »), les parenthèses (« inscrit(e)s ») et les tirets (« inscrit-e-s »).

**Cas particuliers** :

- une citation entre guillemets reste telle quelle ;
- une personne précise est désignée selon le genre qu'elle utilise elle-même (dans une biographie de speaker, reprendre ses mots) ;
- les noms propres et marques restent inchangés (« Developers Group Dijon »).
