from flask import *
import os
import sqlite3
import webbrowser
import secrets

#ouverture automatique du navigateur
webbrowser.open('http://localhost:5000/')

# Chemin relatif basé sur le fichier APP.py
base_dir = os.path.dirname(os.path.abspath(__file__))

# Ajout des fichiers styles et templates au chemin relatif
app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "Templates"),
    static_folder=os.path.join(base_dir, "Styles")
)
# Générer une clé secrète unique à chaque démarrage
app.secret_key = secrets.token_hex(16)

# Fonction pour obtenir une connexion SQLite.
# armoire.db doit rester dans le meme repertoire que app.py
project_root = os.path.dirname(os.path.realpath(__file__))
database = os.path.join(project_root, 'armoire.db')

def get_db_connection():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        
        # Connexion à la base de données
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT prenom, admin FROM users WHERE identifiant = ?', (identifiant,))
            user = cursor.fetchone()

        if user:
            # Utilisateur trouvé, sauvegarde dans la session
            prenom, admin = user
            session['prenom'] = prenom
            session['admin'] = admin
            return redirect('/index')
        else:
            # Utilisateur non trouvé
            return render_template('login.html', error="Identifiant incorrect.")

    # Afficher la page de connexion par défaut
    return render_template('login.html')

@app.route('/index')
def index():
    # Vérifie si l'utilisateur est connecté
    if 'prenom' not in session:
        return redirect('/')  # Redirige vers la page de connexion si non connecté
    
    prenom = session['prenom']
    admin = session['admin']
    return render_template('index.html', prenom=prenom, admin=admin == 1)

# clear la session 
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
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

        # Validation des contraintes
        if len(fab) != 2 or len(n) != 3 or (len(n_fab) != 0 and (len(n_fab) != 7 or not n_fab.startswith("F"))):
            error_message = "Erreur : Les données ne respectent pas les contraintes."
            return render_template('ajouter.html', error=error_message)

        # Insertion dans la base de données
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ref_ecran, libelle, pcb, fab, n_fab, type_serigraphie, n))
            conn.commit()

        return render_template('ajouter.html', success="Données ajoutées avec succès.")

    return render_template('ajouter.html')

@app.route('/ajouterU', methods=['GET', 'POST'])
def ajouterU():
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
                return render_template('ajouterU.html', error=error)

            try:
                cursor.execute('INSERT INTO users (identifiant, prenom, nom, admin) VALUES (?, ?, ?, ?)',
                               (identifiant, prenom, nom, admin))
                conn.commit()
            except sqlite3.IntegrityError as e:
                error = "Erreur d'insertion dans la base de données : " + str(e)
                return render_template('ajouterU.html', error=error)

        return render_template('ajouterU.html', success="Utilisateur ajouté avec succès !")

    return render_template('ajouterU.html')

@app.route('/ecran')
def ecran():
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
     # Remplacer flash par un message de confirmation dans index
     return render_template('index.html', prenom=session.get('prenom'), admin=session.get('admin')==1,
                            success="La connexion à la base de données a été fermée.")

# Démarrage du serveur Flask.
if __name__ == '__main__':
    app.run(debug=False)