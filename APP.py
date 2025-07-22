from flask import *
import sqlite3, secrets, os, webbrowser, subprocess, platform

# Configuration d'écran pour Windows
SCREEN_CONFIG = {
    "screen_number": 0,  # 0 = écran principal, 1 = écran secondaire, etc.
    "use_screen_selection": True  # Activer/désactiver la sélection d'écran
}

SCREEN_CONFIG = {
    "use_screen_selection": True,
    "screen_number": 1  # change selon tes besoins
}

def open_browser_on_screen(url):
    system_os = platform.system()

    if system_os == "Windows" and SCREEN_CONFIG["use_screen_selection"]:
        try:
            # Chemin standard pour Microsoft Edge (Windows 10/11)
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            if not os.path.exists(edge_path):
                edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

            if not os.path.exists(edge_path):
                raise FileNotFoundError("Microsoft Edge non trouvé au chemin habituel.")

            # Position écran
            screen_width = 1920
            position_x = SCREEN_CONFIG["screen_number"] * screen_width

            edge_args = [
                edge_path,
                f"--window-position={position_x},0",
                f"--kiosk={url}",  # mode kiosque
                "--disable-infobars",
                "--disable-extensions",
                url
            ]

            subprocess.Popen(edge_args)
            print(f"Edge ouvert en mode kiosque sur l'écran {SCREEN_CONFIG['screen_number']} 🚀")

        except Exception as e:
            print(f"Erreur lors de l'ouverture de Edge 😱 : {e}")
            webbrowser.open(url)

    else:
        webbrowser.open(url)

# Ouvrir automatiquement le navigateur à l'URL locale
# On lance le navigateur web pour afficher l'application Flask dès le démarrage
open_browser_on_screen('http://localhost:5000/')

# Détermination du répertoire de base du projet
# On récupère le chemin absolu du fichier courant pour définir le répertoire de base
base_dir = os.path.dirname(os.path.abspath(__file__))

# Initialisation de l'application Flask en précisant les dossiers pour les templates et les fichiers statiques (styles)
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "Templates"),
    static_folder=os.path.join(base_dir, "Styles"),
    static_url_path='/Styles'
)
# Générer une clé secrète aléatoire pour sécuriser la session utilisateur
def generate_secret_key():
    app.secret_key = secrets.token_hex(16)

generate_secret_key()

# Définition du chemin vers la base de données SQLite
project_root = os.path.dirname(os.path.realpath(__file__))
database = os.path.join(project_root, 'armoire.db')

def get_db_connection():
    """Renvoie une connexion à la base de données SQLite.
       - Crée une connexion à la base SQLite.
       - Configure la connexion pour retourner des objets Row (accès par nom de colonne).
    """
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

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
        
        # Connexion à la base pour récupérer les informations de l'utilisateur
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT prenom, admin FROM users WHERE identifiant = ?', (identifiant,))
            user = cursor.fetchone()

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
    """
    if 'prenom' not in session:
        return redirect('/')
    
    prenom = session['prenom']
    admin = session['admin'] == 1
    return render_template('index.html', prenom=prenom, admin=admin)

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
    Permet l'ajout d'une nouvelle écran.
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
            return render_template('ajouter.html', error=error_message,
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
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM serigraphie WHERE ref_ecran = ?', (ref_ecran,))
            ecran = cursor.fetchone()

            if ecran:
                if ecran['sorti'] == 1:
                    message = "Erreur : cet écran a déjà été prise."
                    n_value = None
                else:
                    cursor.execute('UPDATE serigraphie SET sorti = 1 WHERE ref_ecran = ?', (ref_ecran,))
                    conn.commit()
                    libelle = ecran['libelle']
                    message = f"écran {libelle} prise avec succès."
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
        cursor = conn.cursor()

        if request.method == 'POST':
            ref_ecran = request.form.get('ref_ecran')
            lavee = request.form.get('lavee') == 'oui'

            cursor.execute("SELECT libelle, N FROM serigraphie WHERE ref_ecran = ? AND sorti = 1", (ref_ecran,))
            result = cursor.fetchone()
            if result:
                cursor.execute("UPDATE serigraphie SET sorti = 0, lave = ? WHERE ref_ecran = ?",
                               (1 if lavee else 0, ref_ecran))
                conn.commit()
                emplacement = result['N']
            else:
                error = "La écran sélectionnée n'existe pas ou n'est pas marquée comme sortie."

        cursor.execute("SELECT ref_ecran, libelle, N FROM serigraphie WHERE sorti = 1")
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

# Lancement du serveur Flask (production avec debug désactivé)
if __name__ == '__main__':
    app.run(debug=False)
