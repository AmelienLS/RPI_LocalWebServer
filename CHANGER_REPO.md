# Procédure : changement de propriétaire ou de nom du dépôt GitHub

## Fichiers à modifier

### 1. `Setups Linux/config.env` — **Linux (scripts `.sh`)**

C'est le **seul fichier à modifier** pour tous les scripts Linux.

```env
REPO_URL="https://github.com/NOUVEAU_OWNER/NOUVEAU_NOM.git"
REPO_DOC_URL="https://github.com/NOUVEAU_OWNER/NOUVEAU_NOM"
```

Tous les scripts Linux (`demarrage_release.sh`, `demarrage_branche.sh`, `installer_service_rpi.sh`, et les scripts Legacy) sourcent ce fichier automatiquement.

---

### 2. `Setups Windows/config.bat` — **Windows (scripts `.bat`)**

```bat
set "REPO_URL=https://github.com/NOUVEAU_OWNER/NOUVEAU_NOM.git"
```

Tous les scripts Windows référencent déjà ce fichier.

---

### 3. `README.md` — **Documentation**

Mettre à jour manuellement les deux occurrences :

- La commande `git clone` (ligne ~251)
- Le one-liner `curl` d'installation rapide (ligne ~296)

---

### 4. Remote git sur les machines déjà déployées

Sur chaque Raspberry Pi (ou autre machine) ayant cloné le dépôt, exécuter :

```bash
git remote set-url origin https://github.com/NOUVEAU_OWNER/NOUVEAU_NOM.git
```

Vérifier avec :

```bash
git remote -v
```

---

## Résumé

| Contexte | Fichier à modifier |
|---|---|
| Scripts Linux | `Setups Linux/config.env` |
| Scripts Windows | `Setups Windows/config.bat` |
| Documentation | `README.md` (manuel) |
| Machines déployées | `git remote set-url origin <nouvelle URL>` |
