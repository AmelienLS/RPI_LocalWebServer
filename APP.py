import configparser
import csv
import io
import json
import os
import platform
import secrets
import shlex
import sqlite3
import subprocess
import webbrowser
import zipfile
from datetime import datetime, date
from io import BytesIO

import openpyxl
from pathlib import Path
from dotenv import load_dotenv

from flask import Flask, redirect, render_template, request, send_file, send_from_directory, session

# Chargement des variables d'environnement depuis .env (si présent, sans écraser les vars déjà définies)
load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

# Répertoires de base
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "Templates"
STATIC_DIR = BASE_DIR / "Styles"
INSTANCE_DIR = Path(os.environ.get("APP_INSTANCE_DIR", BASE_DIR / "instance"))
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

# Fichier de configuration local (non versionné)
CONFIG_PATH = INSTANCE_DIR / "config.ini"


def _load_db_path_from_config() -> "Path | None":
    """Lit le chemin de la DB depuis config.ini, retourne None si absent ou invalide."""
    if not CONFIG_PATH.exists():
        return None
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    raw = cfg.get("database", "path", fallback=None)
    return Path(raw) if raw else None


def _save_db_path_to_config(path: Path) -> None:
    """Sauvegarde le chemin de la DB dans config.ini."""
    cfg = configparser.ConfigParser()
    cfg["database"] = {"path": str(path)}
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        cfg.write(f)


# Priorité : variable d'environnement > config.ini > valeur par défaut
_env_db = os.environ.get("DATABASE_PATH")
if _env_db:
    DATABASE_PATH = Path(_env_db)
else:
    _cfg_db = _load_db_path_from_config()
    DATABASE_PATH = _cfg_db if _cfg_db is not None else INSTANCE_DIR / "armoire.db"

# Configuration d'ouverture automatique du navigateur (désactivée par défaut)
AUTO_OPEN_BROWSER = os.environ.get("APP_AUTO_OPEN_BROWSER", "0").lower() in {"1", "true", "yes", "on"}
BROWSER_CMD = os.environ.get("APP_BROWSER_CMD")

# Initialisation de l'application Flask en précisant les dossiers pour les templates et les fichiers statiques (styles)
app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path='/Styles'
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))


@app.before_request
def _check_db_configured():
    """Redirige vers /setup si la base de données est introuvable."""
    exempt_paths = {"/setup", "/shutdown", "/setup/init_db"}
    if request.path in exempt_paths:
        return
    if request.path.startswith(("/Styles/", "/Images/", "/Functions/")):
        return
    if not DATABASE_PATH.exists():
        return redirect("/setup")


def maybe_open_browser(url: str) -> None:
    """Ouvre le navigateur local si l'option est activée."""
    if not AUTO_OPEN_BROWSER:
        return

    try:
        if BROWSER_CMD:
            args = shlex.split(BROWSER_CMD) + [url]
            subprocess.Popen(args)
        else:
            webbrowser.open(url)
    except Exception as exc:  # pragma: no cover - dépendant d'OS
        print(f"Impossible d'ouvrir un navigateur automatiquement: {exc}")

def database_ready() -> bool:
    return DATABASE_PATH.exists()


def get_db_connection():
    """Renvoie une connexion à la base de données SQLite.
       - Crée une connexion à la base SQLite.
       - Configure la connexion pour retourner des objets Row (accès par nom de colonne).
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_log_tables(connection: sqlite3.Connection) -> None:
    """Garantit la présence de la table de logs, utile pour les anciennes bases."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS sortie_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_ecran INTEGER NOT NULL,
            libelle TEXT NOT NULL,
            personne TEXT NOT NULL,
            personne_rangement TEXT,
            sortie_ts TEXT NOT NULL,
            rangement_ts TEXT,
            lavee INTEGER,
            FOREIGN KEY (ref_ecran) REFERENCES serigraphie (ref_ecran)
        )
        """
    )
    # Migration : ajout de personne_rangement pour les bases créées avant cette version
    existing_cols = {row[1] for row in connection.execute("PRAGMA table_info(sortie_logs)")}
    if "personne_rangement" not in existing_cols:
        connection.execute("ALTER TABLE sortie_logs ADD COLUMN personne_rangement TEXT")
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_sortie_logs_ref ON sortie_logs (ref_ecran, rangement_ts)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_sortie_logs_date ON sortie_logs (sortie_ts)"
    )


def _current_timestamp() -> datetime:
    """Point d'entrée centralisé pour l'heure courante (facile à surcharger dans les tests)."""
    return datetime.now()


def _get_logs_dir() -> Path:
    """Retourne (et crée si besoin) le dossier où stocker les CSV journaliers."""
    log_dir = Path(os.environ.get("APP_LOGS_DIR", INSTANCE_DIR / "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _log_file_path(log_date: date) -> Path:
    return _get_logs_dir() / log_date.strftime("%d-%m-%Y.csv")


def _sync_daily_log(connection: sqlite3.Connection, log_date: date) -> None:
    """Regénère le fichier CSV du jour donné à partir de la table de logs."""
    log_date_iso = log_date.isoformat()
    cursor = connection.execute(
        """
        SELECT ref_ecran, libelle, personne, personne_rangement, sortie_ts, rangement_ts, lavee
        FROM sortie_logs
        WHERE date(sortie_ts) = ?
        ORDER BY datetime(sortie_ts) ASC, id ASC
        """,
        (log_date_iso,),
    )
    rows = cursor.fetchall()
    log_path = _log_file_path(log_date)

    if not rows:
        if log_path.exists():
            log_path.unlink()
        return

    with log_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            ["ref_ecran", "libelle", "personne", "personne_rangement", "heure_sortie", "heure_rangement", "lave"]
        )
        for row in rows:
            sortie_dt = datetime.fromisoformat(row["sortie_ts"])
            sortie_text = sortie_dt.strftime("%H:%M:%S")
            rangement_text = ""
            if row["rangement_ts"]:
                rangement_dt = datetime.fromisoformat(row["rangement_ts"])
                rangement_text = rangement_dt.strftime("%H:%M:%S")
                if rangement_dt.date() != log_date:
                    rangement_text += f" ({rangement_dt.strftime('%d-%m-%Y')})"
            lave_text = ""
            if row["lavee"] is not None:
                lave_text = "Oui" if row["lavee"] == 1 else "Non"
            writer.writerow(
                [
                    row["ref_ecran"],
                    row["libelle"],
                    row["personne"],
                    row["personne_rangement"] or "",
                    sortie_text,
                    rangement_text,
                    lave_text,
                ]
            )


def _build_logs_archive(delete_files: bool = False) -> BytesIO:
    """Construit une archive ZIP contenant tous les journaux CSV puis, optionnellement, les supprime."""
    logs_dir = _get_logs_dir()
    archive_stream = BytesIO()
    csv_files = sorted(logs_dir.glob("*.csv"))
    with zipfile.ZipFile(archive_stream, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        if not csv_files:
            archive.writestr(
                "README.txt",
                "Aucun journal disponible pour le moment.\n"
                "Les fichiers seront générés lorsqu'un écran sera pris/rangé.",
            )
        else:
            for csv_path in csv_files:
                archive.write(csv_path, arcname=csv_path.name)

    if delete_files and csv_files:
        for csv_path in csv_files:
            try:
                csv_path.unlink()
            except FileNotFoundError:
                continue

    archive_stream.seek(0)
    return archive_stream


_SERI_COLUMNS = ['ref_ecran', 'libelle', 'pcb', 'fab', 'n_fab', 'type', 'n']


def _parse_import_file(file_storage):
    """Parse un fichier CSV ou XLSX et retourne une liste de dicts représentant les lignes serigraphie.

    Le mapping se fait par position de colonne (ordre : ref_ecran, libelle, pcb, fab, n_fab, type, n).
    La première ligne est toujours ignorée (en-tête).
    Lève ValueError si le format est invalide ou si le fichier est vide.
    """
    filename = file_storage.filename.lower()

    if filename.endswith('.csv'):
        stream = io.TextIOWrapper(file_storage.stream, encoding='utf-8-sig')
        reader = csv.reader(stream)
        next(reader, None)  # ignorer la ligne d'en-tête
        rows = []
        for vals in reader:
            rows.append({_SERI_COLUMNS[i]: str(vals[i]).strip() if i < len(vals) else ''
                         for i in range(len(_SERI_COLUMNS))})
    elif filename.endswith('.xlsx'):
        wb = openpyxl.load_workbook(file_storage.stream, read_only=True, data_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows()
        next(rows_iter, None)  # ignorer la ligne d'en-tête
        rows = []
        for row in rows_iter:
            vals = [str(c.value or '').strip() for c in row]
            rows.append({_SERI_COLUMNS[i]: vals[i] if i < len(vals) else ''
                         for i in range(len(_SERI_COLUMNS))})
        wb.close()
    else:
        raise ValueError("Format non supporté. Utilisez .csv ou .xlsx")

    if not rows:
        raise ValueError("Le fichier est vide.")

    return rows


# Route de configuration de la base de données
@app.route('/setup', methods=['GET'])
def setup_get():
    """Affiche le formulaire de configuration du chemin de la base de données."""
    return render_template('setup.html', current_path=str(DATABASE_PATH), error=None)


@app.route('/setup/init_db', methods=['POST'])
def setup_init_db():
    """Crée une nouvelle base de données SQLite à partir de schema.sql."""
    global DATABASE_PATH
    if not SCHEMA_PATH.exists():
        return render_template('setup.html', current_path=str(DATABASE_PATH),
                               error="Fichier schema.sql introuvable dans database/.")
    try:
        schema_sql = SCHEMA_PATH.read_text(encoding='utf-8')
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.executescript(schema_sql)
        _save_db_path_to_config(DATABASE_PATH)
        return redirect('/')
    except Exception as e:
        return render_template('setup.html', current_path=str(DATABASE_PATH),
                               error=f"Erreur lors de la création : {e}")


@app.route('/setup', methods=['POST'])
def setup_post():
    """Enregistre le chemin de la base de données fourni par l'utilisateur."""
    global DATABASE_PATH
    path = request.form.get('path', '').strip()
    candidate = Path(path)
    if not candidate.is_file():
        return render_template('setup.html', current_path=path, error="Fichier introuvable à ce chemin.")
    _save_db_path_to_config(candidate)
    DATABASE_PATH = candidate
    return redirect('/')


# Route de connexion
@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Traite la connexion de l'utilisateur.
    - Méthode POST : récupère l'identifiant, vérifie son existence dans la BD et démarre la session.
    - Méthode GET  : affiche le formulaire de connexion.
    """
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        
        try:
            # Connexion à la base pour récupérer les informations de l'utilisateur
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT prenom, admin FROM users WHERE identifiant = ?', (identifiant,))
                user = cursor.fetchone()
        except sqlite3.OperationalError as exc:
            return render_template('login.html', error=f"Erreur base de données : {exc}")

        if user:
            prenom, admin = user
            # Stocke le prénom et le statut admin dans la session pour une utilisation ultérieure
            session['prenom'] = prenom
            session['admin'] = admin
            return redirect('/index')
        else:
            # Si l'utilisateur n'est pas trouvé, on renvoie une erreur sur le formulaire de connexion
            return render_template('login.html', error="Identifiant incorrect.")

    # Afficher le formulaire de connexion en cas de requête GET
    return render_template('login.html')

# Route de la page d'accueil
@app.route('/index')
def index():
    """
    Affiche la page d'accueil.
    - Vérifie que l'utilisateur est connecté (présence du prénom dans la session).
    - Passe à la vue le prénom et le statut admin pour l'affichage conditionnel.
    - Récupère la liste des écrans rentrés mais non lavés (sorti=0, lave=0).
    """
    if 'prenom' not in session:
        return redirect('/')

    prenom = session['prenom']
    admin = session['admin'] == 1
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ref_ecran, libelle, n FROM serigraphie WHERE sorti = 0 AND lave = 0 ORDER BY n'
        )
        a_laver = cursor.fetchall()
    return render_template('index.html', prenom=prenom, admin=admin, a_laver=a_laver)


# Route pour marquer un écran comme lavé depuis l'accueil
@app.route('/laver', methods=['POST'])
def laver():
    """
    Marque un écran comme lavé.
    - Met à jour serigraphie.lave = 1.
    - Met a jour la derniere entree sortie_logs concernee (lavee 0 -> 1).
    - Synchronise le CSV journalier correspondant.
    """
    if 'prenom' not in session:
        return redirect('/')

    ref_ecran = request.form.get('ref_ecran')
    with get_db_connection() as conn:
        _ensure_log_tables(conn)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM serigraphie WHERE ref_ecran = ? AND sorti = 0 AND lave = 0',
            (ref_ecran,),
        )
        if cursor.fetchone():
            cursor.execute('UPDATE serigraphie SET lave = 1 WHERE ref_ecran = ?', (ref_ecran,))
            log_row = cursor.execute(
                """
                SELECT id, sortie_ts FROM sortie_logs
                WHERE ref_ecran = ? AND rangement_ts IS NOT NULL AND lavee = 0
                ORDER BY rangement_ts DESC
                LIMIT 1
                """,
                (ref_ecran,),
            ).fetchone()
            if log_row:
                cursor.execute(
                    'UPDATE sortie_logs SET lavee = 1, personne_rangement = ? WHERE id = ?',
                    (session.get('prenom', 'Inconnu'), log_row['id']),
                )
                conn.commit()
                _sync_daily_log(conn, datetime.fromisoformat(log_row['sortie_ts']).date())
            else:
                conn.commit()
    return redirect('/index')


# Route de déconnexion
@app.route('/logout')
def logout():
    """
    Déconnecte l'utilisateur.
    - Vide la session et redirige vers la page de connexion.
    """
    session.clear()
    return redirect('/')

# Route pour ajouter un écran
@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """
    Permet l'ajout d'un nouvel écran.
    - Vérifie que l'utilisateur est un administrateur.
    - Valide les contraintes sur les champs et insère la donnée dans la BD.
    - Gère les erreurs d'unicité au niveau de la base de données.
    """
    if 'admin' not in session or not session['admin']:
        return redirect('/index') 
    if request.method == 'POST':
        data = request.form
        ref_ecran = data['ref_ecran']
        libelle = data['libelle']
        pcb = data['pcb']
        fab = data['fab']
        n_fab = data['n_fab']
        type_serigraphie = data['type']
        n = data['n']

        # Vérification des contraintes sur certains champs (ex. longueur et format)
        if len(fab) != 2 or len(n) != 3 or (len(n_fab) != 0 and (len(n_fab) != 7 or not n_fab.startswith("F"))):
            error_message = "Erreur : Les données ne respectent pas les contraintes."
            return render_template('ajouter.html', error=error_message,
                                   ref_ecran=ref_ecran, libelle=libelle, pcb=pcb, fab=fab, n_fab=n_fab, type=type_serigraphie, n=n)

        try:
            # Insertion dans la base de données
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (ref_ecran, libelle, pcb, fab, n_fab, type_serigraphie, n))
                conn.commit()
            return render_template('ajouter.html', success="Données ajoutées avec succès.")
        except sqlite3.IntegrityError as e:
            error_str = str(e)
            if "UNIQUE constraint failed:" in error_str:
                constraint = error_str.split("UNIQUE constraint failed: ")[1]
                # Adaptation du message d'erreur en fonction du champ concerné
                if "ref_ecran" in constraint:
                    field_name = "Réf Écran"
                    ref_ecran = ""
                else:
                    field_name = "Emplacement"
                    n = ""
                error_message = f'Erreur: {field_name} déjà utilisée.'
            return render_template('ajouter.html', error=error_message, # type: ignore
                                   ref_ecran=ref_ecran, libelle=libelle, pcb=pcb, fab=fab, n_fab=n_fab, type=type_serigraphie, n=n)

    return render_template('ajouter.html')

# Route pour ajouter un utilisateur
@app.route('/ajouterU', methods=['GET', 'POST'])
def ajouterU():
    """
    Permet à un administrateur d'ajouter un nouvel utilisateur.
    - Vérifie l'unicité de l'identifiant.
    - Insère dans la base en gérant les potentielles erreurs d'intégrité.
    """
    if 'admin' not in session or not session['admin']:
        return redirect('/index')   

    # Définit une valeur par défaut pour éviter la variable possiblement non liée
    error = None

    if request.method == 'POST':
        identifiant = request.form['identifiant']
        prenom = request.form['prenom']
        nom = request.form['nom']
        admin = 1 if 'admin' in request.form else 0

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT identifiant FROM users WHERE identifiant = ?', (identifiant,))
            existing_user = cursor.fetchone()

            if existing_user:
                error = "L'identifiant existe déjà. Veuillez en choisir un autre."
                return render_template('ajouterU.html', error=error,
                                       identifiant=identifiant, prenom=prenom, nom=nom)

            try:
                cursor.execute('INSERT INTO users (identifiant, prenom, nom, admin) VALUES (?, ?, ?, ?)',
                               (identifiant, prenom, nom, admin))
                conn.commit()
            except sqlite3.IntegrityError as e:
                error_str = str(e)
                if "UNIQUE constraint failed:" in error_str:
                    constraint = error_str.split("UNIQUE constraint failed: ")[1]
                    if "identifiant" in constraint:
                        field_name = "Identifiant"
                        identifiant = ""
                    else:
                        field_name = constraint
                    error = f'Erreur: {field_name} déjà utilisé.'
                else:
                    # Cas générique si le message d'erreur n'est pas celui attendu
                    error = f"Erreur lors de l'ajout de l'utilisateur : {error_str}"
                return render_template('ajouterU.html', error=error,
                                       identifiant=identifiant, prenom=prenom, nom=nom)

        return render_template('ajouterU.html', success="Utilisateur ajouté avec succès !")

    return render_template('ajouterU.html')

# Route affichant le tableau des écrans
@app.route('/ecran')
def ecran():
    """
    Affiche la liste complète des écrans.
    Récupère les données depuis la base et transmet le statut admin pour un affichage conditionnel.
    """
    if 'prenom' not in session:
        return redirect('/')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ref_ecran, libelle, pcb, fab, n_fab, type, n, sorti, lave FROM serigraphie')
        ecrans = cursor.fetchall()

    admin = session.get('admin', 0) == 1
    return render_template('ecran.html', ecrans=ecrans, admin=admin)


@app.route("/export_logs", methods=["GET"])
def export_logs():
    """
    Permet à un administrateur d'exporter tous les journaux quotidiens sous forme d'archive ZIP.
    Le navigateur invite ensuite à choisir l'emplacement d'enregistrement.
    """
    if 'prenom' not in session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    archive_stream = _build_logs_archive(delete_files=False)
    filename = f"screen_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return send_file(
        archive_stream,
        mimetype="application/zip",
        as_attachment=True,
        download_name=filename,
    )


@app.route('/export_serigraphie')
def export_serigraphie():
    """Exporte la table serigraphie au format XLSX. Admin uniquement."""
    if 'prenom' not in session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ref_ecran, libelle, pcb, fab, n_fab, type, n FROM serigraphie ORDER BY ref_ecran')
        rows = cursor.fetchall()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(_SERI_COLUMNS)
    for row in rows:
        ws.append([row[c] for c in _SERI_COLUMNS])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"serigraphie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename,
    )


@app.route('/import_serigraphie', methods=['POST'])
def import_serigraphie():
    """Importe des écrans depuis un fichier CSV ou XLSX. Admin uniquement.

    - Insère les nouvelles lignes directement.
    - Si des conflits (ref_ecran déjà existant) sont détectés, rend la page de résolution.
    """
    if 'prenom' not in session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    file = request.files.get('import_file')
    if not file or file.filename == '':
        return render_template('ajouter.html', error="Aucun fichier sélectionné.")

    try:
        rows = _parse_import_file(file)
    except ValueError as e:
        return render_template('ajouter.html', error=str(e))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        existing = {str(r['ref_ecran']) for r in cursor.execute('SELECT ref_ecran FROM serigraphie').fetchall()}

    new_rows = [r for r in rows if str(r.get('ref_ecran', '')).strip() not in existing]
    conflict_rows = [r for r in rows if str(r.get('ref_ecran', '')).strip() in existing]

    inserted = 0
    if new_rows:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for r in new_rows:
                try:
                    cursor.execute(
                        'INSERT OR IGNORE INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n) VALUES (?,?,?,?,?,?,?)',
                        (r.get('ref_ecran', ''), r.get('libelle', ''), r.get('pcb', ''),
                         r.get('fab', ''), r.get('n_fab', ''), r.get('type', ''), r.get('n', ''))
                    )
                    inserted += cursor.rowcount
                except sqlite3.Error:
                    pass
            conn.commit()

    if conflict_rows:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            db_rows = {}
            for r in conflict_rows:
                ref = str(r.get('ref_ecran', '')).strip()
                row = cursor.execute(
                    'SELECT ref_ecran, libelle, pcb, fab, n_fab, type, n FROM serigraphie WHERE ref_ecran = ?', (ref,)
                ).fetchone()
                if row:
                    db_rows[ref] = dict(row)

        conflicts = [
            {'incoming': r, 'existing': db_rows.get(str(r.get('ref_ecran', '')).strip(), {})}
            for r in conflict_rows
        ]
        return render_template('import_conflicts.html',
                               conflicts=conflicts,
                               inserted=inserted,
                               conflicts_json=json.dumps([c['incoming'] for c in conflicts]))

    success_msg = f"{inserted} écran(s) ajouté(s) avec succès."
    return render_template('ajouter.html', success=success_msg)


@app.route('/import_serigraphie/confirm', methods=['POST'])
def import_serigraphie_confirm():
    """Applique les choix de résolution des conflits d'import. Admin uniquement."""
    if 'prenom' not in session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    conflicts_json = request.form.get('conflicts_json', '[]')
    overwrite_all = request.form.get('overwrite_all') == '1'

    try:
        conflict_rows = json.loads(conflicts_json)
    except (json.JSONDecodeError, ValueError):
        return render_template('ajouter.html', error="Données de conflit invalides.")

    to_overwrite = []
    if overwrite_all:
        to_overwrite = conflict_rows
    else:
        selected = set(request.form.getlist('overwrite'))
        to_overwrite = [r for r in conflict_rows if str(r.get('ref_ecran', '')) in selected]

    updated = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for r in to_overwrite:
            cursor.execute(
                'UPDATE serigraphie SET libelle=?, pcb=?, fab=?, n_fab=?, type=?, n=? WHERE ref_ecran=?',
                (r.get('libelle', ''), r.get('pcb', ''), r.get('fab', ''),
                 r.get('n_fab', ''), r.get('type', ''), r.get('n', ''), r.get('ref_ecran', ''))
            )
            updated += cursor.rowcount
        conn.commit()

    kept = len(conflict_rows) - updated
    parts = []
    if updated:
        parts.append(f"{updated} écran(s) écrasé(s)")
    if kept:
        parts.append(f"{kept} conflit(s) conservé(s)")
    return render_template('ajouter.html', success=", ".join(parts) + ".")


@app.route('/stats')
def stats():
    """
    Affiche les statistiques d'utilisation des écrans.
    - Admin uniquement.
    - Nombre de passages par écran (tri décroissant) et par personne.
    """
    if 'prenom' not in session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    with get_db_connection() as conn:
        _ensure_log_tables(conn)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.ref_ecran, s.libelle, s.fab, s.type, COUNT(sl.id) AS total_passages
            FROM serigraphie s
            INNER JOIN sortie_logs sl ON s.ref_ecran = sl.ref_ecran
            GROUP BY s.ref_ecran, s.libelle, s.fab, s.type
            ORDER BY total_passages DESC
        ''')
        ecrans_stats = cursor.fetchall()

        cursor.execute('''
            SELECT personne, COUNT(*) AS total_passages
            FROM sortie_logs
            GROUP BY personne
            ORDER BY total_passages DESC
        ''')
        personnes_stats = cursor.fetchall()

        total_passages = sum(row['total_passages'] for row in ecrans_stats)

    return render_template(
        'stats.html',
        ecrans_stats=ecrans_stats,
        personnes_stats=personnes_stats,
        total_passages=total_passages,
    )


@app.route("/reset_stats", methods=["POST"])
def reset_stats():
    """
    Remet à zéro les statistiques en vidant la table sortie_logs.
    - Admin uniquement.
    """
    if 'prenom' not in session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    with get_db_connection() as conn:
        _ensure_log_tables(conn)
        conn.execute('DELETE FROM sortie_logs')
        conn.commit()

    return redirect('/stats')


@app.route("/purge_logs", methods=["POST"])
def purge_logs():
    """
    Exporte tous les journaux puis supprime les fichiers CSV pour repartir sur un dossier vide.
    """
    if 'prenom' not in  session:
        return redirect('/')
    if not session.get('admin'):
        return redirect('/index')

    archive_stream = _build_logs_archive(delete_files=True)
    filename = f"screen_logs_cleared_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return send_file(
        archive_stream,
        mimetype="application/zip",
        as_attachment=True,
        download_name=filename,
    )

# Route pour prendre un écran (marquer comme sorti)
@app.route('/prendre', methods=['GET', 'POST'])
def prendre():
    """
    Permet de prendre (emprunter) un écran.
    - Vérifie que l'écran n'est pas déjà marqué comme sortie.
    - Met à jour l'état de l'écran et renvoie un message de confirmation.
    """
    if 'prenom' not in session:
        return redirect('/')

    if request.method == 'POST':
        ref_ecran = request.form['ref_ecran']

        with get_db_connection() as conn:
            _ensure_log_tables(conn)
            cursor = conn.cursor()

            # Essai exact d'abord, puis recherche par suffixe
            cursor.execute('SELECT * FROM serigraphie WHERE ref_ecran = ?', (ref_ecran,))
            ecran = cursor.fetchone()

            if not ecran:
                # Recherche par suffixe : l'utilisateur peut taper les derniers caractères
                cursor.execute(
                    'SELECT * FROM serigraphie WHERE ref_ecran LIKE ?',
                    ('%' + ref_ecran,),
                )
                resultats = cursor.fetchall()
                if len(resultats) == 1:
                    ecran = resultats[0]
                elif len(resultats) > 1:
                    refs = ", ".join(str(r['ref_ecran']) for r in resultats)
                    message = f"Plusieurs écrans correspondent : {refs}. Précisez votre recherche."
                    return render_template('prendre.html', message=message, n_value=None)

            if ecran:
                if ecran['sorti'] == 1:
                    message = "Erreur : cet écran a déjà été pris."
                    n_value = ecran['n']
                else:
                    cursor.execute('UPDATE serigraphie SET sorti = 1 WHERE ref_ecran = ?', (ecran['ref_ecran'],))
                    sortie_dt = _current_timestamp()
                    cursor.execute(
                        """
                        INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts)
                        VALUES (?, ?, ?, ?)
                        """,
                        (ecran['ref_ecran'], ecran['libelle'], session.get('prenom', 'Inconnu'), sortie_dt.isoformat()),
                    )
                    conn.commit()
                    _sync_daily_log(conn, sortie_dt.date())
                    libelle = ecran['libelle']
                    message = f"écran {libelle} pris avec succès."
                    n_value = ecran['n']
            else:
                message = "Erreur : écran non trouvée."
                n_value = None

        return render_template('prendre.html', message=message, n_value=n_value)

    return render_template('prendre.html', message=None, n_value=None)

# Route pour modifier un écran
@app.route('/modifier', methods=['GET', 'POST'])
def modifier():
    """
    Permet la modification d'un écran existante.
    - Mode recherche : l'utilisateur entre une référence pour précharger les données.
    - Mode modification : les données peuvent être mises à jour, avec ou sans changement de référence.
    - Vérifie l'unicité de la nouvelle référence en cas de modification.
    """
    if 'admin' not in session or not session['admin']:
        return redirect('/index') 

    message = None
    error = False
    ref_ecran = None
    libelle = None
    pcb = None
    fab = None
    n_fab = None
    type_ = None
    n = None
    sorti = None
    lave = None

    if request.method == 'POST':
        old_ref_ecran = request.form.get('old_ref_ecran')
        new_ref_ecran = request.form.get('new_ref_ecran')
        libelle = request.form.get('libelle')
        pcb = request.form.get('pcb')
        fab = request.form.get('fab')
        n_fab = request.form.get('n_fab')
        type_ = request.form.get('type')
        n = request.form.get('n')
        sorti = request.form.get('sorti')
        lave = request.form.get('lave')

        with get_db_connection() as conn:
            cursor = conn.cursor()

            if old_ref_ecran:
                if new_ref_ecran and old_ref_ecran != new_ref_ecran:
                    cursor.execute('SELECT 1 FROM serigraphie WHERE ref_ecran = ?', (new_ref_ecran,))
                    if cursor.fetchone():
                        message = f"La référence {new_ref_ecran} existe déjà. Veuillez choisir une autre référence."
                        error = True
                    else:
                        cursor.execute('''UPDATE serigraphie 
                                          SET ref_ecran = ?, libelle = ?, pcb = ?, fab = ?, n_fab = ?, type = ?, n = ?, sorti = ?, lave = ? 
                                          WHERE ref_ecran = ?''',
                                       (new_ref_ecran, libelle, pcb, fab, n_fab, type_, n, sorti, lave, old_ref_ecran))
                        conn.commit()
                        message = f"écran {old_ref_ecran} mise à jour avec succès. Nouvelle référence : {new_ref_ecran}."
                else:
                    cursor.execute('''UPDATE serigraphie 
                                      SET libelle = ?, pcb = ?, fab = ?, n_fab = ?, type = ?, n = ?, sorti = ?, lave = ? 
                                      WHERE ref_ecran = ?''',
                                   (libelle, pcb, fab, n_fab, type_, n, sorti, lave, old_ref_ecran))
                    conn.commit()
                    message = f"écran {old_ref_ecran} mise à jour avec succès."
            else:
                ref_ecran = request.form.get('ref_ecran')
                cursor.execute('SELECT * FROM serigraphie WHERE ref_ecran = ?', (ref_ecran,))
                ecran = cursor.fetchone()

                if ecran:
                    ref_ecran = ecran['ref_ecran']
                    libelle = ecran['libelle']
                    pcb = ecran['pcb']
                    fab = ecran['fab']
                    n_fab = ecran['n_fab']
                    type_ = ecran['type']
                    n = ecran['n']
                    sorti = ecran['sorti']
                    lave = ecran['lave']
                else:
                    message = f"écran avec la référence {ref_ecran} non trouvée."
                    error = True

    return render_template('modifier.html', message=message, ref_ecran=ref_ecran, libelle=libelle, pcb=pcb,
                           fab=fab, n_fab=n_fab, type_=type_, n=n, sorti=sorti, lave=lave, error=error)
    
# Route pour supprimer un écran
@app.route('/supprimer', methods=['GET', 'POST'])
def supprimer():
    """
    Permet la suppression d'un écran.
    - Mode "check" : demande de confirmation en affichant les détails de la écran.
    - Mode "delete" : suppression effective de l'écran dans la BD.
    """
    if 'admin' not in session or not session['admin']:
        return redirect('/index') 
    if request.method == 'POST':
        ref_ecran = request.form.get('ref_ecran', '').strip()
        action = request.form.get('action')

        with get_db_connection() as conn:
            cursor = conn.cursor()

            if action == "check":
                cursor.execute("SELECT libelle FROM serigraphie WHERE ref_ecran = ?", (ref_ecran,))
                row = cursor.fetchone()

                if row:
                    return render_template('supprimer.html', ref_ecran=ref_ecran, exists=True, libelle=row[0])
                else:
                    return render_template('supprimer.html', ref_ecran=ref_ecran, exists=False)

            elif action == "delete":
                cursor.execute("DELETE FROM serigraphie WHERE ref_ecran = ?", (ref_ecran,))
                conn.commit()
                return render_template('supprimer.html', success=f"La référence écran '{ref_ecran}' a été supprimée avec succès.")
    return render_template('supprimer.html')

# Route pour ranger un écran
@app.route('/ranger', methods=['GET', 'POST'])
def ranger():
    """
    Permet de ranger un écran.
    - Met à jour l'attribut 'sorti' et enregistre l'état de lavage.
    """
    if 'prenom' not in session:
        return redirect('/')

    error = None
    emplacement = None

    with get_db_connection() as conn:
        _ensure_log_tables(conn)
        cursor = conn.cursor()

        if request.method == 'POST':
            ref_ecran = request.form.get('ref_ecran')
            lavee = request.form.get('lavee') == 'oui'

            cursor.execute("SELECT libelle, n FROM serigraphie WHERE ref_ecran = ? AND sorti = 1", (ref_ecran,))
            result = cursor.fetchone()
            if result:
                cursor.execute("UPDATE serigraphie SET sorti = 0, lave = ? WHERE ref_ecran = ?",
                               (1 if lavee else 0, ref_ecran))
                log_row = cursor.execute(
                    """
                    SELECT id, sortie_ts FROM sortie_logs
                    WHERE ref_ecran = ? AND rangement_ts IS NULL
                    ORDER BY sortie_ts DESC
                    LIMIT 1
                    """,
                    (ref_ecran,),
                ).fetchone()
                log_date = None
                if log_row:
                    rangement_dt = _current_timestamp()
                    cursor.execute(
                        "UPDATE sortie_logs SET rangement_ts = ?, lavee = ?, personne_rangement = ? WHERE id = ?",
                        (rangement_dt.isoformat(), 1 if lavee else 0, session.get('prenom', 'Inconnu'), log_row["id"]),
                    )
                    log_date = datetime.fromisoformat(log_row["sortie_ts"]).date()
                conn.commit()
                if log_date:
                    _sync_daily_log(conn, log_date)
                emplacement = result['n']
            else:
                error = "La écran sélectionnée n'existe pas ou n'est pas marquée comme sortie."

        cursor.execute("SELECT ref_ecran, libelle, n FROM serigraphie WHERE sorti = 1")
        serigraphies = cursor.fetchall()

    return render_template('ranger.html', serigraphies=serigraphies, emplacement=emplacement, error=error)

# Route de fermeture de la connexion à la base
@app.route('/close_db')
def close_db():
    """
    Ferme la connexion à la base de données.
    - Affiche un message de confirmation sur la page d'accueil.
    """
    return render_template('index.html', prenom=session.get('prenom'), admin=session.get('admin')==1,
                           success="La connexion à la base de données a été fermée.")
    
@app.route("/shutdown", methods=["POST"])
def shutdown():
    """
    Éteint le système (Raspberry/Linux) ou ferme le serveur WSGI (Windows).
    """
    system_os = platform.system()

    try:
        if system_os == "Windows":
            # Ferme le serveur WSGI Waitress sur Windows
            os._exit(0)  # arrêt immédiat du processus Python
            return "<h1>Serveur Windows arrêté.</h1>"

        elif system_os in ["Linux", "Darwin"]:  # Darwin inclus pour MacOS, au cas où
            # Commande d'arrêt sur Linux
            subprocess.run(["/usr/bin/sudo", "shutdown", "-h", "now"])
            return "<h1>Arrêt du système en cours...</h1>"

        else:
            return f"<h1>OS '{system_os}' non supporté pour l'arrêt.</h1>"

    except Exception as e:
        return f"<h1>Erreur :</h1><p>{e}</p>"
    
# Cette route permet de servir les fichiers JavaScript présents dans le dossier "Functions".
# Lorsqu'une requête est faite à /Functions/nom_du_fichier, le fichier correspondant est envoyé.
@app.route('/Functions/<path:filename>')
def send_functions(filename):
    # Récupère le chemin absolu du répertoire actuel (où se trouve APP.py)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # Construit le chemin vers le dossier "Functions" en se basant sur le répertoire racine du projet
    functions_dir = os.path.join(base_dir, 'Functions')
    # Envoie le fichier demandé depuis le dossier "Functions"
    return send_from_directory(functions_dir, filename)

# Cette route permet de servir les fichiers images présents dans le dossier "Images".
# Elle est nécessaire pour que les icônes utilisées dans les templates soient
# correctement récupérées par le navigateur.
@app.route('/Images/<path:filename>')
def send_images(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(base_dir, 'Images')
    return send_from_directory(images_dir, filename)

# Lancement du serveur Flask (production avec debug désactivé par défaut)
if __name__ == '__main__':
    host = os.environ.get("APP_HOST", "127.0.0.1")
    port = int(os.environ.get("APP_PORT", "5000"))
    browser_url = os.environ.get("APP_BROWSER_URL", f"http://127.0.0.1:{port}/")
    maybe_open_browser(browser_url)
    debug_enabled = os.environ.get("FLASK_DEBUG", "0").lower() in {"1", "true", "yes", "on"}
    app.run(host=host, port=port, debug=debug_enabled)