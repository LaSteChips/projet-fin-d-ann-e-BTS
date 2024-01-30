from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox
import subprocess
from tabulate import tabulate
import ttkthemes as ttk

# BDD
conn = sqlite3.connect('user.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT)''')
conn.commit()

# ouvre app.py si la connexion est réussie
def open_app():
    window.destroy()    
    subprocess.run(["python", "app.py"])

# vérifier qui se connecte
def check_user():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute('''SELECT * FROM user WHERE username = ? AND password = ?''', (username, password))
    user_found = cursor.fetchone()

    if user_found:
        open_app()
    else:
        messagebox.showerror("Erreur de connexion", "Identifiants incorrects")

# enregistrement de l' utilisateur
def save_user():
    username = entry_username.get()
    password = entry_password.get()

    # vérifier si l'utilisateur existe déjà
    cursor.execute('''SELECT * FROM user WHERE username = ?''', (username,))
    user_exist = cursor.fetchone()

    if user_exist:
        messagebox.showerror("Erreur d'enregistrement", "Ce nom d'utilisateur existe déjà.")
    else:
        # enregistrer l'utilisateur dans la BDD
        cursor.execute('''INSERT INTO user (username, password) VALUES (?, ?)''', (username, password))
        conn.commit()
        messagebox.showinfo("Enregistrement réussi", "Utilisateur enregistré avec succès !")

def show_users():
    # Connexion à la base de données SQLite
    connexion = sqlite3.connect("user.db")
    curseur = connexion.cursor()

    # Récupération des utilisateurs depuis la base de données
    curseur.execute("SELECT * FROM user")
    utilisateurs = curseur.fetchall()

    # Fermeture de la connexion à la base de données
    connexion.close()

    # Création de la fenêtre Tkinter
    window = tk.Tk()
    window.title("Liste des utilisateurs")

    # paramètre de la fenêtre
    window.geometry("200x100")
    window.minsize(200, 100)
    window.iconbitmap("images/logo delorme.ico")
    window.configure(background='#36393e')

    # Création d'une zone de texte pour afficher les utilisateurs
    text_zone = tk.Text(window, fg='white', font='Arial')
    text_zone.pack()
    text_zone.configure(background='#36393e')

    # Affichage des utilisateurs dans la zone de texte
    for utilisateur in utilisateurs:
        text_zone.insert(tk.END, f"ID: {utilisateur[0]}, Nom: {utilisateur[1]}\n")

# créer la fenêtre d'application
window = Tk()
window.title("Page de connexion")

# paramètre de la fenêtre
window.geometry("480x140")
window.minsize(400, 140)
window.maxsize(400, 140)
window.iconbitmap("images/logo delorme.ico")
window.configure(background='#36393e')

# créer une 'frame'
frame = tk.Frame(window, bg='#36393e')
frame.pack(padx=20, pady=20)

# paramètre utilisateur
label_username = tk.Label(frame, text="Nom d'Utilisateur:")
label_username.grid(row=0, column=0, padx=5, pady=5)
entry_username = tk.Entry(frame)
entry_username.grid(row=0, column=1, padx=5, pady=5)

# paramètres de mot de passe
label_password = tk.Label(frame, text="Mot de passe:")
label_password.grid(row=1, column=0, padx=5, pady=5)
entry_password = tk.Entry(frame, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

# bouton "d'enregistrer"
btn_register = tk.Button(frame, text="S' Enregistrer", command=save_user)
btn_register.grid(row=2, column=0, padx=5, pady=5)

# bouton "se connecter"
btn_connection = tk.Button(frame, text="Se Connecter", command=check_user)
btn_connection.grid(row=2, column=1, padx=5, pady=5)

# bouton "liste d'utilisateurs"
btn_connection = tk.Button(frame, text="Liste d'utilisateurs", command=show_users)
btn_connection.grid(row=2, column=2, padx=5, pady=5)

window.mainloop()