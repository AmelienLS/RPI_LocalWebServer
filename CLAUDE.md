# Instructions pour l'agent Claude

## Mise à jour du CHANGELOG

**À chaque modification du code source**, tu dois mettre à jour `CHANGELOG.md`.

### Ce qui doit être inscrit

Toute modification touchant au **code source** du projet :
- Fichiers Python (`.py`)
- Fichiers JavaScript (`.js`)
- Fichiers HTML/CSS/templates
- Schéma de base de données (`schema.sql`)
- Scripts de déploiement (`.sh`, `.bat`)
- Fichiers de tests

### Ce qui ne doit PAS être inscrit

Les changements d'environnement ou de configuration externe :
- `.vscode/settings.json`
- `.gitignore`, `.env`
- `requirements.txt` seul (sauf s'il accompagne une vraie feature)
- `README.md` seul
- Configuration IDE, outils de développement

### Format d'une entrée

Chaque entrée suit ce format en haut du fichier, sous le titre `# Journal des modifications` :

```markdown
## [X.Y.Z] - YYYY-MM-DD
> Commit : `<nom du commit>`
### Ajouté
- Description de ce qui a été ajouté.
### Modifié
- Description de ce qui a été modifié.
### Corrigé
- Description de ce qui a été corrigé.
```

N'inclure que les sections (Ajouté / Modifié / Corrigé) pertinentes pour le changement.

### Numéro de version

Incrémenter le numéro de version selon ces règles :
- **PATCH** (Z) : correction de bug, refactor mineur, ajout de test
- **MINOR** (Y) : nouvelle fonctionnalité rétrocompatible, reset Z à 0
- **MAJOR** (X) : changement cassant l'interface ou l'architecture, reset Y et Z à 0

La version actuelle est celle du dernier bloc `## [X.Y.Z]` dans `CHANGELOG.md`.


## Convention de nommage des commits

Les messages de commit doivent suivre le format **Conventional Commits** :

```
<type>(<scope>): <description courte>
```

- La description est en **anglais**, à l'**impératif présent**, sans majuscule initiale, sans point final.
- Le scope est optionnel mais recommandé quand le changement est localisé.

### Types autorisés

| Type       | Quand l'utiliser |
|------------|-----------------|
| `feat`     | Nouvelle fonctionnalité |
| `fix`      | Correction de bug |
| `refactor` | Refactoring sans changement de comportement |
| `test`     | Ajout ou modification de tests |
| `docs`     | Documentation uniquement |
| `chore`    | Tâches de maintenance (scripts, config de build) |
| `perf`     | Amélioration de performance |

### Exemples

```
feat(auth): add session expiry after inactivity
fix(db): handle missing database file on startup
refactor(routes): extract common login guard into helper
test(ecran): add coverage for duplicate reference case
chore(linux): add graceful shutdown script
docs(changelog): update 3.1.0 release notes
```


## Mise à jour des tests

**À chaque mise à jour mineure ou majeure**, tu dois créer de nouveaux tests dans le dossier `tests/` couvrant les nouvelles fonctionnalités introduites.

**Dans tous les cas**, si le comportement existant du projet est modifié, tu dois mettre à jour les tests existants pour refléter ces changements.

### Règles à suivre

- **MINOR ou MAJOR** : créer des tests pour chaque nouvelle fonctionnalité ajoutée.
- **Modification du comportement** : adapter les tests existants impactés par le changement.
- Les tests doivent être placés dans `tests/` et suivre les conventions déjà en place dans ce dossier.
- Ne jamais laisser des tests en échec après une modification : si un test échoue suite à un changement voulu, le mettre à jour plutôt que de le supprimer.