from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox
import subprocess
import sys

# Fonction pour actualiser le tableau
def actualiser_tableau():
    # Ici, vous mettrez le code pour actualiser le tableau
    # Par exemple, vous pouvez réexécuter la requête SQL pour obtenir les données les plus récentes
    pass

# Déclaration de la variable globale pour stocker le nom d'utilisateur
global logged_in_username
logged_in_username = sys.argv[1]

# BDD utilisateur
conn = sqlite3.connect('user.db')
cursor = conn.cursor

# Connexion à la base de données 
conn = sqlite3.connect('gestion.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS gestion (
                    last_name TEXT,
                    first_name TEXT,
                    phone_number TEXT,
                    Email TEXT,
                    address TEXT,
                    cause TEXT)''')
conn.commit()

# Fonction pour fermer l'application
def close_app():
    window.destroy()
    subprocess.run(["python", "connexion.py"])

# Créer la fenêtre
window = tk.Tk()
window.title("Gestion des appels clients")

# Paramètres de la fenêtre
window.geometry("1024x576")
window.minsize(400, 300)
window.iconbitmap("images/logo delorme.ico")
window.configure(background='#36393e')

# Créer une 'frame'
frame = tk.Frame(window, bg='#36393e')

# Titre
label_title = Label(frame, text="Liste des appels", font=("Arial", 40), bg="#36393E", fg='White')
label_title.pack(fill=tk.BOTH, expand=True)  # Centrer en haut de la fenêtre

# Message de bienvenue avec le nom d'utilisateur
welcome_message = Label(frame, text=f"Bienvenue {logged_in_username} !", font=("Arial", 20), bg="#36393E", fg='White')
welcome_message.pack()

# Bouton Ajouter
add_button = Button(frame, text="Ajouter", font=("Arial", 20), bg="#000000", fg='White')
add_button.pack()

# Bouton Supprimer
del_button = Button(frame, text="Supprimer", font=("Arial", 20), bg="#000000", fg='White')
del_button.pack()

# Bouton Déconnexion
logout_button = Button(frame, text="Déconnexion", font=("Arial", 20), bg="#000000", fg='White', command=close_app)
logout_button.pack()

# Afficher le tableau (à compléter selon la méthode que vous souhaitez utiliser)

frame.pack(expand=YES)

window.mainloop()
