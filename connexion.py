from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess

# Connexion à la base de données
conn = sqlite3.connect('user.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT)''')
conn.commit()

# Déclaration de la variable globale pour stocker le nom d'utilisateur
global logged_in_username
logged_in_username = ""

# Fonction pour ouvrir app.py si la connexion est réussie
def open_app():
    global logged_in_username  # Utilisation de la variable globale
    logged_in_username = entry_username.get()  # Stockage du nom d'utilisateur connecté
    window.destroy()    
    subprocess.run(["python", "app.py", "--username", logged_in_username])  # Passez le nom d'utilisateur comme argument à app_modified.py


# Fonction pour vérifier l'utilisateur
def check_user():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute('''SELECT * FROM user WHERE username = ? AND password = ?''', (username, password))
    user_found = cursor.fetchone()

    if user_found:
        open_app()
    else:
        messagebox.showerror("Erreur de connexion", "Identifiants incorrects")

# Fonction pour enregistrer l'utilisateur
def save_user():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute('''SELECT * FROM user WHERE username = ?''', (username,))
    user_exist = cursor.fetchone()

    if user_exist:
        messagebox.showerror("Erreur d'enregistrement", "Ce nom d'utilisateur existe déjà.")
    else:
        cursor.execute('''INSERT INTO user (username, password) VALUES (?, ?)''', (username, password))
        conn.commit()
        messagebox.showinfo("Enregistrement réussi", "Utilisateur enregistré avec succès !")

# Fonction pour supprimer un utilisateur
def delete_user():
    # Vérifier si un utilisateur est sélectionné
    selected_user = tree.selection()
    if selected_user:
        user_id = tree.item(selected_user, "values")[0]
        # Créer une fenêtre pour la demande de mot de passe
        admin_pass_window = tk.Toplevel()
        admin_pass_window.title("Confirmation de suppression")
        admin_pass_window.geometry("300x100")
        admin_pass_window.iconbitmap("images/logo delorme.ico")
        admin_pass_window.configure(background='#36393e')

        # Label et Entry pour le mot de passe administrateur
        label_password = tk.Label(admin_pass_window, text="Mot de passe administrateur:", fg='white', bg='#36393e')
        label_password.pack(pady=5)
        entry_admin_password = tk.Entry(admin_pass_window, show="*")
        entry_admin_password.pack(pady=5)

        # Bouton de validation
        btn_ok = tk.Button(admin_pass_window, text="Valider", command=lambda: confirm_delete(user_id, entry_admin_password.get(), admin_pass_window))
        btn_ok.pack(pady=5)
    else:
        messagebox.showerror("Erreur de suppression", "Veuillez sélectionner un utilisateur à supprimer.")

# Fonction pour confirmer la suppression de l'utilisateur
def confirm_delete(user_id, admin_password, admin_pass_window):
    # Récupération du mot de passe de l'utilisateur ayant l'ID "1"
    cursor.execute('''SELECT password FROM user WHERE id = 1''')
    correct_password = cursor.fetchone()

    # Vérification du mot de passe administrateur
    if admin_password == correct_password[0]:
        # Suppression de l'utilisateur spécifique de la base de données
        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()
        messagebox.showinfo("Suppression réussie", "L'utilisateur a été supprimé avec succès.")
        admin_pass_window.destroy()
        # Rafraîchir la liste des utilisateurs après suppression
        show_users()
    else:
        messagebox.showerror("Erreur : mot de passe incorrect", "Le mot de passe administrateur est incorrect.")

# Fonction pour afficher la liste des utilisateurs
def show_users():
    # Vérifier si la fenêtre existe déjà
    if hasattr(show_users, 'user_list_window') and show_users.user_list_window.winfo_exists():
        show_users.user_list_window.destroy()

    # Créer la fenêtre Tkinter
    show_users.user_list_window = tk.Toplevel()
    show_users.user_list_window.title("Liste des utilisateurs")
    show_users.user_list_window.geometry("400x300")
    show_users.user_list_window.iconbitmap("images/logo delorme.ico")
    show_users.user_list_window.configure(background='#36393e')

    # Créer le Treeview
    global tree
    tree = ttk.Treeview(show_users.user_list_window, columns=("ID", "Nom d'utilisateur", "Supprimer"), show="headings")
    tree.pack(expand=True, fill='both')

    # Ajouter des colonnes pour l'ID et le nom d'utilisateur
    tree.heading("ID", text="ID")
    tree.heading("Nom d'utilisateur", text="Nom d'utilisateur")
    tree.heading("Supprimer", text="Supprimer")

    # Récupérer les utilisateurs depuis la base de données
    cursor.execute("SELECT * FROM user")
    utilisateurs = cursor.fetchall()

    # Afficher les utilisateurs dans le Treeview
    for utilisateur in utilisateurs:
        tree.insert("", "end", values=(utilisateur[0], utilisateur[1], ""))
    
    # Bouton "Supprimer l'utilisateur"
    btn_delete = tk.Button(show_users.user_list_window, text="Supprimer l'utilisateur", command=delete_user)
    btn_delete.pack(pady=5)

# Création de la fenêtre principale
window = Tk()
window.title("Page de connexion")

# Paramètres de la fenêtre
window.geometry("480x150")
window.minsize(400, 150)
window.maxsize(400, 150)
window.iconbitmap("images/logo delorme.ico")
window.configure(background='#36393e')

# Création d'une 'frame'
frame = tk.Frame(window, bg='#36393e')
frame.pack(padx=20, pady=20)

# Paramètres utilisateur
label_username = tk.Label(frame, text="Nom d'Utilisateur:", bg='#36393e', fg='white', font=('Arial', 10))
label_username.grid(row=0, column=0, padx=5, pady=5)
entry_username = tk.Entry(frame)
entry_username.grid(row=0, column=1, padx=5, pady=5)

# Paramètres de mot de passe
label_password = tk.Label(frame, text="Mot de passe:", bg='#36393e',fg='white', font=('Arial', 10))
label_password.grid(row=1, column=0, padx=5, pady=5)
entry_password = tk.Entry(frame, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

# Bouton "S'enregistrer"
btn_register = tk.Button(frame, text="S' Enregistrer", command=save_user)
btn_register.grid(row=2, column=0, padx=5, pady=5)

# Bouton "Se connecter"
btn_connection = tk.Button(frame, text="Se Connecter", command=check_user)
btn_connection.grid(row=2, column=1, padx=5, pady=5)

# Bouton "Liste d'utilisateurs"
btn_show_users = tk.Button(frame, text="Liste d'utilisateurs", command=show_users)
btn_show_users.grid(row=2, column=2, padx=5, pady=5)

window.mainloop()