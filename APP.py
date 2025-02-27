from flask import *
import os, sqlite3, webbrowser, secrets

# Ouvrir automatiquement le navigateur à l'URL locale
webbrowser.open('http://localhost:5000/')

# Détermination du répertoire de base du projet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Configuration de l’application Flask
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "Templates"),
    static_folder=os.path.join(base_dir, "Styles")
)
app.secret_key = secrets.token_hex(16)

# Chemin vers la base de données
project_root = os.path.dirname(os.path.realpath(__file__))
database = os.path.join(project_root, 'armoire.db')

def get_db_connection():
    """Renvoie une connexion à la base de données SQLite."""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Route de connexion.
    - POST : récupère l'identifiant et vérifie dans la base de données.
    - GET : affiche la page de connexion.
    """
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        
        # Connexion à la base de données pour récupérer l'utilisateur
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT prenom, admin FROM users WHERE identifiant = ?', (identifiant,))
            user = cursor.fetchone()

        if user:
            prenom, admin = user
            # Stockage des informations utilisateur en session
            session['prenom'] = prenom
            session['admin'] = admin
            return redirect('/index')
        else:
            # Utilisateur non trouvé
            return render_template('login.html', error="Identifiant incorrect.")

    # Affichage de la page de connexion par défaut (méthode GET)
    return render_template('login.html')

@app.route('/index')
def index():
    """
    Route de la page d'accueil.
    Vérifie la connexion de l'utilisateur et transmet son prénom et statut d'admin à la vue.
    """
    if 'prenom' not in session:
        return redirect('/')
    
    prenom = session['prenom']
    admin = session['admin'] == 1
    return render_template('index.html', prenom=prenom, admin=admin)

@app.route('/logout')
def logout():
    """
    Déconnecte l'utilisateur en vidant la session.
    """
    session.clear()
    return redirect('/')

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """
    Route pour ajouter une nouvelle sérigraphie.
    Vérifie les contraintes sur les champs et insère les données dans la base.
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

        # Vérification des contraintes sur certains champs
        if len(fab) != 2 or len(n) != 3 or (len(n_fab) != 0 and (len(n_fab) != 7 or not n_fab.startswith("F"))):
            error_message = "Erreur : Les données ne respectent pas les contraintes."
            return render_template('ajouter.html', error=error_message,
                                   ref_ecran=ref_ecran, libelle=libelle, pcb=pcb, fab=fab, n_fab=n_fab, type=type_serigraphie, n=n)

        try:
            # Insertion de la nouvelle sérigraphie dans la base de données
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
                # Remplacer le nom de la colonne par le nom de la ligne du formulaire
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

@app.route('/ajouterU', methods=['GET', 'POST'])
def ajouterU():
    """
    Route pour ajouter un nouvel utilisateur.
    Vérifie si l'identifiant est disponible et insère l'utilisateur dans la base.
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
                    # Remplacer le nom de la colonne par le nom du champ du formulaire
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

@app.route('/ecran')
def ecran():
    """
    Route qui affiche le tableau des sérigraphies.
    Récupère toutes les sérigraphies depuis la base et transmet le statut admin.
    """
    if 'prenom' not in session:
        return redirect('/')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ref_ecran, libelle, pcb, fab, n_fab, type, n, sorti, lave FROM serigraphie')
        ecrans = cursor.fetchall()

    admin = session.get('admin', 0) == 1
    return render_template('ecran.html', ecrans=ecrans, admin=admin)

@app.route('/prendre', methods=['GET', 'POST'])
def prendre():
    """
    Route pour prendre une sérigraphie.
    Met à jour l'état de la sérigraphie si elle n'est pas déjà sortie.
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
                    message = "Erreur : cette sérigraphie a déjà été prise."
                    n_value = None
                else:
                    cursor.execute('UPDATE serigraphie SET sorti = 1 WHERE ref_ecran = ?', (ref_ecran,))
                    conn.commit()
                    libelle = ecran['libelle']
                    message = f"Sérigraphie {libelle} prise avec succès."
                    n_value = ecran['n']
            else:
                message = "Erreur : sérigraphie non trouvée."
                n_value = None

        return render_template('prendre.html', message=message, n_value=n_value)

    return render_template('prendre.html', message=None, n_value=None)

@app.route('/modifier', methods=['GET', 'POST'])
def modifier():
    """
    Route pour modifier une sérigraphie.
    Deux modes : recherche d'une référence existante OU mise à jour (avec ou sans changement de référence).
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
                        message = f"Sérigraphie {old_ref_ecran} mise à jour avec succès. Nouvelle référence : {new_ref_ecran}."
                else:
                    cursor.execute('''UPDATE serigraphie 
                                      SET libelle = ?, pcb = ?, fab = ?, n_fab = ?, type = ?, n = ?, sorti = ?, lave = ? 
                                      WHERE ref_ecran = ?''',
                                   (libelle, pcb, fab, n_fab, type_, n, sorti, lave, old_ref_ecran))
                    conn.commit()
                    message = f"Sérigraphie {old_ref_ecran} mise à jour avec succès."
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
                    message = f"Sérigraphie avec la référence {ref_ecran} non trouvée."
                    error = True

    return render_template('modifier.html', message=message, ref_ecran=ref_ecran, libelle=libelle, pcb=pcb,
                           fab=fab, n_fab=n_fab, type_=type_, n=n, sorti=sorti, lave=lave, error=error)
    
@app.route('/supprimer', methods=['GET', 'POST'])
def supprimer():
    """
    Route pour supprimer une sérigraphie.
    En mode vérification (action "check"), la page affiche une demande de confirmation.
    En mode suppression (action "delete"), la référence est supprimée de la base.
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

@app.route('/ranger', methods=['GET', 'POST'])
def ranger():
    """
    Route pour ranger une sérigraphie.
    Met à jour l'attribut 'sorti' et enregistre l'état de lavage.
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
                error = "La sérigraphie sélectionnée n'existe pas ou n'est pas marquée comme sortie."

        cursor.execute("SELECT ref_ecran, libelle, N FROM serigraphie WHERE sorti = 1")
        serigraphies = cursor.fetchall()

    return render_template('ranger.html', serigraphies=serigraphies, emplacement=emplacement, error=error)

@app.route('/close_db')
def close_db():
    """
    Route de fermeture de la connexion à la base.
    Affiche un message de confirmation sur la page d'accueil.
    """
    return render_template('index.html', prenom=session.get('prenom'), admin=session.get('admin')==1,
                           success="La connexion à la base de données a été fermée.")
    
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

# Lancement du serveur Flask (production avec debug désactivé)
if __name__ == '__main__':
    app.run(debug=False)
