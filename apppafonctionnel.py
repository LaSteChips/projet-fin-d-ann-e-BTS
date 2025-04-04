from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

# --- Connexions aux bases de données ---
def get_db_connection_user():
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection_gestion():
    conn = sqlite3.connect('gestion.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection_backup():
    conn = sqlite3.connect('backup.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection_old_backup():
    conn = sqlite3.connect('old_backup.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialisation des tables ---
with get_db_connection_user() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT)''')
    conn.commit()

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

with get_db_connection_old_backup() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS appels_old_backup (
                        id INTEGER,
                        nom TEXT,
                        prenom TEXT,
                        telephone TEXT,
                        email TEXT,
                        adresse TEXT,
                        raison TEXT)''')
    conn.commit()

# ===========================
# === Modules de compte ===
# ===========================

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

@app.route('/')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ===============================
# === Modules de l’application ===
# ===============================

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

@app.route('/delete_appel/<int:id>', methods=['POST'])
def delete_appel_post(id):
    with get_db_connection_gestion() as gestion_conn:
        appel = gestion_conn.execute("SELECT * FROM appels WHERE id = ?", (id,)).fetchone()
        if appel:
            with get_db_connection_backup() as backup_conn:
                backup_conn.execute('''INSERT INTO appels_backup 
                    (id, nom, prenom, telephone, email, adresse, raison) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (appel['id'], appel['nom'], appel['prenom'], appel['telephone'],
                     appel['email'], appel['adresse'], appel['raison']))
                backup_conn.commit()
            gestion_conn.execute("DELETE FROM appels WHERE id = ?", (id,))
            gestion_conn.commit()
    return redirect(url_for('get_page'))

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

# ===============================
# === Modules de backup ===
# ===============================

@app.route('/backup', methods=['GET'])
def backup_page():
    with get_db_connection_backup() as conn:
        appels_backup = conn.execute("SELECT * FROM appels_backup").fetchall()
    return render_template('backup.html.j2', appels=appels_backup)

@app.route('/delete_from_backup/<int:id>', methods=['POST'])
def delete_from_backup(id):
    with get_db_connection_backup() as conn:
        conn.execute("DELETE FROM appels_backup WHERE id = ?", (id,))
        conn.commit()
    return redirect(url_for('backup_page'))

# ===============================
# === Modules old_backup ===
# ===============================

@app.route('/old_backup', methods=['GET'])
def view_old_backup():
    with get_db_connection_old_backup() as conn:
        old_backup_calls = conn.execute("SELECT * FROM appels_old_backup").fetchall()
    return render_template('old_backup.html.j2', appels=old_backup_calls)

@app.route('/delete_old_backup/<int:id>', methods=['POST'])
def delete_old_backup(id):
    with get_db_connection_gestion() as conn:
        appel = conn.execute("SELECT * FROM appels_backup WHERE id = ?", (id,)).fetchone()
        if appel:
            with get_db_connection_old_backup() as archive_conn:
                archive_conn.execute('''INSERT INTO appels_old_backup (id, nom, prenom, telephone, email, adresse, raison) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (appel['id'], appel['nom'], appel['prenom'], appel['telephone'],
                                     appel['email'], appel['adresse'], appel['raison']))
                archive_conn.commit()
            conn.execute("DELETE FROM appels_backup WHERE id = ?", (id,))
            conn.commit()
    return redirect(url_for('view_old_backup'))

@app.route('/recover_old_backup/<int:id>', methods=['POST'])
def recover_old_backup(id):
    with get_db_connection_old_backup() as conn:
        appel = conn.execute("SELECT * FROM appels_old_backup WHERE id = ?", (id,)).fetchone()
        if appel:
            with get_db_connection_gestion() as gestion_conn:
                gestion_conn.execute('''INSERT INTO appels (id, nom, prenom, telephone, email, adresse, raison) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (appel['id'], appel['nom'], appel['prenom'], appel['telephone'],
                                     appel['email'], appel['adresse'], appel['raison']))
                gestion_conn.commit()
            conn.execute("DELETE FROM appels_old_backup WHERE id = ?", (id,))
            conn.commit()
    return redirect(url_for('view_old_backup'))

# Lancement de l'app
if __name__ == '__main__':
    app.run(debug=True)
