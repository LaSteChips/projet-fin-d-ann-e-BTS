from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

# Connexion à la base de données utilisateur
def get_db_connection_user():
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn

# Connexion à la base de données gestion
def get_db_connection_gestion():
    conn = sqlite3.connect('gestion.db')
    conn.row_factory = sqlite3.Row
    return conn

# Création des tables utilisateurs
with get_db_connection_user() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT)''')
    conn.commit()

# Création des tables gestion
with get_db_connection_gestion() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS appels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom TEXT,
                        prenom TEXT,
                        telephone TEXT,
                        email TEXT,
                        adresse TEXT,
                        raison TEXT)''')
    conn.commit()

# Backup des appels
with get_db_connection_gestion() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS appels_backup (
                        id INTEGER,
                        nom TEXT,
                        prenom TEXT,
                        telephone TEXT,
                        email TEXT,
                        adresse TEXT,
                        raison TEXT)''')
    conn.commit()

# Route de connexion
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with get_db_connection_user() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['username'] = username
                return redirect('/app')

            return jsonify({'error': 'Identifiants incorrects'}), 400
    return render_template('login.html.j2')

# Connexion à la base de données backup
def get_db_connection_backup():
    conn = sqlite3.connect('backup.db')
    conn.row_factory = sqlite3.Row
    return conn

# Création de la table backup
with get_db_connection_backup() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS appels_backup (
                        id INTEGER,
                        nom TEXT,
                        prenom TEXT,
                        telephone TEXT,
                        email TEXT,
                        adresse TEXT,
                        raison TEXT)''')
    conn.commit()

# Route d'enregistrement
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée reçue ou format incorrect'}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Nom d\'utilisateur et mot de passe sont requis'}), 400

        with get_db_connection_user() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
            if cursor.fetchone():
                return jsonify({'error': 'Ce nom d\'utilisateur existe déjà.'}), 400

            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()

        return jsonify({'success': 'Utilisateur enregistré avec succès !'}), 200
    return render_template('register.html.j2')

# Route de déconnexion
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Route de suppression de compte
@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username_to_delete = data.get('username')
            admin_password = data.get('admin_password')
        else:
            username_to_delete = request.form['username']
            admin_password = request.form['admin_password']

        with get_db_connection_user() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM user WHERE id = 1')
            admin_user = cursor.fetchone()

            if not admin_user or not check_password_hash(admin_user['password'], admin_password):
                return jsonify({'error': 'Mot de passe administrateur incorrect'}), 403

            cursor.execute('SELECT * FROM user WHERE username = ?', (username_to_delete,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': 'Utilisateur introuvable'}), 404

            cursor.execute('DELETE FROM user WHERE username = ?', (username_to_delete,))
            conn.commit()

        return jsonify({'success': 'Utilisateur supprimé avec succès'}), 200

    return render_template('deleteAccount.html.j2')

# Route pour afficher les appels dans backup.db
@app.route('/backup', methods=['GET'])
def backup_page():
    with get_db_connection_backup() as conn:
        appels_backup = conn.execute("SELECT * FROM appels_backup").fetchall()
    return render_template('backup.html.j2', appels=appels_backup)

# Backup des appels supprimés (Old Backup)
with get_db_connection_gestion() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS appels_old_backup (
                        id INTEGER,
                        nom TEXT,
                        prenom TEXT,
                        telephone TEXT,
                        email TEXT,
                        adresse TEXT,
                        raison TEXT)''')
    conn.commit()

# Route pour afficher les appels dans old_backup.db
@app.route('/old_backup', methods=['GET'])
def view_old_backup():
    with get_db_connection_gestion() as conn:
        old_backup_calls = conn.execute("SELECT * FROM appels_old_backup").fetchall()
    return render_template('old_backup.html.j2', appels=old_backup_calls)

# Route pour supprimer un appel définitivement (dans old_backup.db)
@app.route('/delete_old_backup/<int:id>', methods=['POST'])
def delete_old_backup(id):
    with get_db_connection_gestion() as conn:
        appel = conn.execute("SELECT * FROM appels_backup WHERE id = ?", (id,)).fetchone()
        if appel:
            # Déplacer vers old_backup
            with get_db_connection_gestion() as archive_conn:
                archive_conn.execute('''INSERT INTO appels_old_backup (id, nom, prenom, telephone, email, adresse, raison) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (appel['id'], appel['nom'], appel['prenom'], appel['telephone'],
                                     appel['email'], appel['adresse'], appel['raison']))
                archive_conn.commit()

            # Supprimer de backup.db
            conn.execute("DELETE FROM appels_backup WHERE id = ?", (id,))
            conn.commit()
    return redirect(url_for('view_old_backup'))

# Route pour supprimer un appel de backup
@app.route('/delete_from_backup/<int:id>', methods=['POST'])
def delete_from_backup(id):
    with get_db_connection_backup() as conn:
        # Supprimer l'appel de la table appels_backup
        conn.execute("DELETE FROM appels_backup WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for('backup_page'))  # Rediriger vers la page de backup après suppression


# Route pour récupérer un appel dans gestion.db
@app.route('/recover_old_backup/<int:id>', methods=['POST'])
def recover_old_backup(id):
    with get_db_connection_gestion() as conn:
        appel = conn.execute("SELECT * FROM appels_old_backup WHERE id = ?", (id,)).fetchone()
        if appel:
            # Remettre dans gestion.db
            with get_db_connection_gestion() as gestion_conn:
                gestion_conn.execute('''INSERT INTO appels (id, nom, prenom, telephone, email, adresse, raison) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (appel['id'], appel['nom'], appel['prenom'], appel['telephone'],
                                     appel['email'], appel['adresse'], appel['raison']))
                gestion_conn.commit()

            # Supprimer de old_backup.db
            conn.execute("DELETE FROM appels_old_backup WHERE id = ?", (id,))
            conn.commit()
    return redirect(url_for('view_old_backup'))

# Route pour afficher les appels
@app.route('/app', methods=['GET', 'POST'])
def get_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.form
        if all(data.get(k) for k in ['nom', 'prenom', 'telephone', 'email', 'adresse', 'raison']):
            with get_db_connection_gestion() as conn:
                conn.execute('''INSERT INTO appels (nom, prenom, telephone, email, adresse, raison) 
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             (data['nom'], data['prenom'], data['telephone'], data['email'], data['adresse'], data['raison']))
                conn.commit()
        return redirect(url_for('get_page'))

    with get_db_connection_gestion() as conn:
        appels = conn.execute("SELECT * FROM appels").fetchall()
    return render_template('app.html.j2', appels=appels)

# Route pour supprimer un appel
@app.route('/delete_appel/<int:id>', methods=['POST'])
def delete_appel_post(id):
    with get_db_connection_gestion() as gestion_conn:
        appel = gestion_conn.execute("SELECT * FROM appels WHERE id = ?", (id,)).fetchone()
        if appel:
            # Backup dans backup.db
            with get_db_connection_backup() as backup_conn:
                backup_conn.execute('''INSERT INTO appels_backup 
                    (id, nom, prenom, telephone, email, adresse, raison) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (appel['id'], appel['nom'], appel['prenom'], appel['telephone'],
                     appel['email'], appel['adresse'], appel['raison']))
                backup_conn.commit()

            # Suppression dans gestion.db
            gestion_conn.execute("DELETE FROM appels WHERE id = ?", (id,))
            gestion_conn.commit()
    return redirect(url_for('get_page'))

# Route pour mettre à jour un appel
@app.route('/update_appel/<int:id>', methods=['POST'])
def update_appel(id):
    data = request.json
    with get_db_connection_gestion() as conn:
        conn.execute('''UPDATE appels 
                        SET nom = ?, prenom = ?, telephone = ?, email = ?, adresse = ?, raison = ? 
                        WHERE id = ?''',
                     (data['nom'], data['prenom'], data['telephone'], data['email'], data['adresse'], data['raison'], id))
        conn.commit()
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
