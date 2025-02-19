from flask import *
import os
import sqlite3
import webbrowser

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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT prenom, admin FROM users WHERE identifiant = ?', (identifiant,))
        user = cursor.fetchone()
        # SUPER IMPORTANT toujours fermer sa connection, 
        # Sinon plus possible de récupérer des données.
        conn.close()

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
    # Aucune idéee de pourquoi post et pas get mais ca marche
    if request.method == 'POST':
        # Récupération des données suivantes depuis le form HTML.
        data = request.form
        ref_ecran = data['ref_ecran']
        libelle = data['libelle']
        pcb = data['pcb']
        fab = data['fab']
        n_fab = data['n_fab']
        type_serigraphie = data['type']
        n = data['n']

        # Validation des contraintes. A modifier si les contraintes changent.
        if len(fab) != 2 or len(n) != 3 or (len(n_fab) != 0 and (len(n_fab) != 7 or not n_fab.startswith("F"))):
            error_message = "Erreur : Les données ne respectent pas les contraintes."
            return render_template('ajouter.html', error=error_message)

        # Insertion dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ref_ecran, libelle, pcb, fab, n_fab, type_serigraphie, n))
        conn.commit()
        conn.close()

        return render_template('ajouter.html', success="Données ajoutées avec succès.")

    return render_template('ajouter.html')

@app.route('/ajouterU', methods=['GET', 'POST'])
def ajouterU():
    if 'admin' not in session or not session['admin']:
        return redirect('/index')  # Si l'utilisateur n'est pas admin, redirige vers /index
    # Autre maniere de récupérer les données d'ubn form.
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        prenom = request.form['prenom']
        nom = request.form['nom']
        admin = 1 if 'admin' in request.form else 0

        # Vérifier si l'identifiant existe déjà dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT identifiant FROM users WHERE identifiant = ?', (identifiant,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Si l'identifiant existe déjà, afficher un message d'erreur
            conn.close()
            error = "L'identifiant existe déjà. Veuillez en choisir un autre."
            return render_template('ajouterU.html', error=error)

        # Si l'identifiant est unique, ajouter l'utilisateur à la base de données
        try:
            cursor.execute('INSERT INTO users (identifiant, prenom, nom, admin) VALUES (?, ?, ?, ?)',
                           (identifiant, prenom, nom, admin))
            conn.commit()
            # Message de succès
            flash('Utilisateur ajouté avec succès !', 'success')
        except sqlite3.IntegrityError as e:
            # Si une erreur se produit malgré la vérification, la gestion de l'erreur se fait ici.
            #Pour du debug en dev uniquement, je le laisse au cas ou.
            conn.close()
            error = "Erreur d'insertion dans la base de données : " + str(e)
            return render_template('ajouterU.html', error=error)

        conn.close()
        return redirect('/ajouterU')

    return render_template('ajouterU.html')

@app.route('/ecran')
def ecran():
    if 'prenom' not in session:
        return redirect('/')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ref_ecran, libelle, pcb, fab, n_fab, type, n, sorti, lave FROM serigraphie')
    ecrans = cursor.fetchall()
    conn.close()
    admin = session.get('admin', 0) == 1
    # Affichage de la page avec les ecrans et renvoie de l'info admin.
    return render_template('ecran.html', ecrans=ecrans, admin=admin)


@app.route('/prendre', methods=['GET', 'POST'])
def prendre():
    if 'prenom' not in session:
        return redirect('/')

    if request.method == 'POST':
        ref_ecran = request.form['ref_ecran']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Cherche la sérigraphie par ref_ecran
        cursor.execute('SELECT * FROM serigraphie WHERE ref_ecran = ?', (ref_ecran,))
        ecran = cursor.fetchone()

        if ecran:
            # Si trouvé, vérifier si pris est déjà 1
            if ecran['sorti'] == 1:
                message = "Erreur : cette sérigraphie a déjà été prise."
                n_value = None  # Pas de valeur à afficher
            else:
                # Mettre pris à 1
                cursor.execute('UPDATE serigraphie SET sorti = 1 WHERE ref_ecran = ?', (ref_ecran,))
                conn.commit()
                libelle = ecran['libelle']  # Récupérer le libellé de la sérigraphie
                message = f"Sérigraphie {libelle} prise avec succès."
                n_value = ecran['n']  # Récupérer la valeur de 'n' à afficher
        else:
            message = "Erreur : sérigraphie non trouvée."
            n_value = None
        
        conn.close()
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
        # Récupérer les champs du formulaire
        old_ref_ecran = request.form.get('old_ref_ecran')  # Référence actuelle (avant modification)
        new_ref_ecran = request.form.get('new_ref_ecran')  # Nouvelle référence (si modification)
        libelle = request.form.get('libelle')
        pcb = request.form.get('pcb')
        fab = request.form.get('fab')
        n_fab = request.form.get('n_fab')
        type_ = request.form.get('type')
        n = request.form.get('n')
        sorti = request.form.get('sorti')
        lave = request.form.get('lave')

        # Connexion à la base de données
        conn = get_db_connection()
        cursor = conn.cursor()

        if old_ref_ecran:  # Mise à jour des données
            # Vérifier si la nouvelle référence existe déjà dans la base
            if new_ref_ecran and old_ref_ecran != new_ref_ecran:
                cursor.execute('SELECT 1 FROM serigraphie WHERE ref_ecran = ?', (new_ref_ecran,))
                if cursor.fetchone():
                    message = f"La référence {new_ref_ecran} existe déjà. Veuillez choisir une autre référence."
                    error = True
                else:
                    # Mise à jour avec la nouvelle référence
                    cursor.execute('''UPDATE serigraphie 
                                      SET ref_ecran = ?, libelle = ?, pcb = ?, fab = ?, n_fab = ?, type = ?, n = ?, sorti = ?, lave = ? 
                                      WHERE ref_ecran = ?''',
                                   (new_ref_ecran, libelle, pcb, fab, n_fab, type_, n, sorti, lave, old_ref_ecran))
                    conn.commit()
                    message = f"Sérigraphie {old_ref_ecran} mise à jour avec succès. Nouvelle référence : {new_ref_ecran}."
            else:
                # Mise à jour sans changement de référence
                cursor.execute('''UPDATE serigraphie 
                                  SET libelle = ?, pcb = ?, fab = ?, n_fab = ?, type = ?, n = ?, sorti = ?, lave = ? 
                                  WHERE ref_ecran = ?''',
                               (libelle, pcb, fab, n_fab, type_, n, sorti, lave, old_ref_ecran))
                conn.commit()
                message = f"Sérigraphie {old_ref_ecran} mise à jour avec succès."

        else:  # Recherche par référence (première étape)
            ref_ecran = request.form.get('ref_ecran')
            cursor.execute('SELECT * FROM serigraphie WHERE ref_ecran = ?', (ref_ecran,))
            ecran = cursor.fetchone()

            if ecran:
                # Charger les données de la sérigraphie pour modification
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

        conn.close()

    return render_template('modifier.html', message=message, ref_ecran=ref_ecran, libelle=libelle, pcb=pcb,
                           fab=fab, n_fab=n_fab, type_=type_, n=n, sorti=sorti, lave=lave, error=error)
    
@app.route('/supprimer', methods=['GET', 'POST'])
def supprimer():
    if 'admin' not in session or not session['admin']:
        return redirect('/index') 
    
    if request.method == 'POST':
        ref_ecran = request.form.get('ref_ecran', '').strip()
        action = request.form.get('action')

        if action == "check":
            # Vérifie si la référence existe dans la base de données
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT libelle FROM serigraphie WHERE ref_ecran = ?", (ref_ecran,))
            row = cursor.fetchone()
            conn.close()

            # Rendu de la page avec le résultat
            if row:
                return render_template(
                    'supprimer.html',
                    ref_ecran=ref_ecran,
                    exists=True,
                    libelle=row[0]
                )
            else:
                return render_template(
                    'supprimer.html',
                    ref_ecran=ref_ecran,
                    exists=False
                )

        elif action == "delete":
            # Supprime la référence si elle existe
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM serigraphie WHERE ref_ecran = ?", (ref_ecran,))
            conn.commit()
            conn.close()

            flash(f"La référence écran '{ref_ecran}' a été supprimée avec succès.", 'success')
            return redirect('/supprimer')

    # Rendu initial de la page
    return render_template('supprimer.html')

@app.route('/ranger', methods=['GET', 'POST'])
def ranger():
    if 'prenom' not in session:
        return redirect('/')
    
    emplacement = None
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        ref_ecran = request.form.get('ref_ecran')
        lavee = request.form.get('lavee') == 'oui'

        # Vérifie si la sérigraphie existe et a été sortie
        cursor.execute("SELECT libelle, N FROM serigraphie WHERE ref_ecran = ? AND sorti = 1", (ref_ecran,))
        result = cursor.fetchone()
        if result:
            # Mise à jour des informations
            cursor.execute("""
                UPDATE serigraphie 
                SET sorti = 0, lave = ? 
                WHERE ref_ecran = ?
            """, (1 if lavee else 0, ref_ecran))
            conn.commit()
            emplacement = result['N']  # Récupérer l'emplacement
        else:
            flash("La sérigraphie sélectionnée n'existe pas ou n'est pas marquée comme sortie.", "error")

    cursor.execute("SELECT ref_ecran, libelle, N FROM serigraphie WHERE sorti = 1")
    serigraphies = cursor.fetchall()
    conn.close()
    return render_template('ranger.html', serigraphies=serigraphies, emplacement=emplacement)

@app.route('/close_db')
def close_db():
     flash("La connexion à la base de données a été fermée.", "info")
     return redirect('/index')   

# Démarrage du serveur Flask.
# Mettre debug a True si jamais il le faut.
if __name__ == '__main__':
    app.run(debug=False)

