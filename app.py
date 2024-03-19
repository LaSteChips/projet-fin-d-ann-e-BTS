import tkinter as tk
from tkinter import ttk, messagebox
import sys
import sqlite3
import subprocess

# Récupérer l'argument --username passé depuis connexion.py
username_index = sys.argv.index("--username")
logged_in_username = sys.argv[username_index + 1] if username_index != -1 else None

# Connexion à la base de données principale
conn_main = sqlite3.connect('gestion.db')
cursor_main = conn_main.cursor()

# Création de la table dans la base de données principale
cursor_main.execute('''CREATE TABLE IF NOT EXISTS appels (
                    id INTEGER PRIMARY KEY,
                    nom TEXT,
                    prenom TEXT,
                    telephone TEXT,
                    email TEXT,
                    adresse TEXT,
                    raison TEXT)''')
conn_main.commit()

# Connexion à la base de données de sauvegarde
conn_backup = sqlite3.connect('backup.db')
cursor_backup = conn_backup.cursor()

# Création de la table dans la base de données de sauvegarde
cursor_backup.execute('''CREATE TABLE IF NOT EXISTS backup_appels (
                    id INTEGER PRIMARY KEY,
                    nom TEXT,
                    prenom TEXT,
                    telephone TEXT,
                    email TEXT,
                    adresse TEXT,
                    raison TEXT)''')
conn_backup.commit()

# Fermeture des connexions
conn_main.close()
conn_backup.close()

# Fonction pour enregistrer un appel dans la base de données principale
def save_call():
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    telephone = entry_telephone.get()
    email = entry_email.get()
    adresse = entry_adresse.get()
    raison = entry_raison.get()

    # Vérifier si les champs sont vides
    if nom == "" or prenom == "" or telephone == "" or email == "" or adresse == "" or raison == "":
        messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
        return

    # Enregistrer l'appel dans la base de données principale
    conn_main = sqlite3.connect('gestion.db')
    cursor_main = conn_main.cursor()
    cursor_main.execute('''INSERT INTO appels (nom, prenom, telephone, email, adresse, raison) 
                      VALUES (?, ?, ?, ?, ?, ?)''', (nom, prenom, telephone, email, adresse, raison))
    conn_main.commit()
    conn_main.close()

    # Rafraîchir le tableau avec les données mises à jour
    refresh_table()

    # Afficher un message de confirmation
    messagebox.showinfo("Enregistrement réussi", "L'appel a été enregistré avec succès.")

# Fonction pour rafraîchir le tableau avec les données de la base de données principale
def refresh_table():
    # Effacer toutes les lignes du tableau
    for row in table.get_children():
        table.delete(row)

    # Récupérer les données depuis la base de données principale
    conn_main = sqlite3.connect('gestion.db')
    cursor_main = conn_main.cursor()
    cursor_main.execute("SELECT * FROM appels")
    rows = cursor_main.fetchall()
    conn_main.close()

    # Ajouter les données au tableau
    for row in rows:
        table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

# Fonction pour supprimer la ligne sélectionnée dans le tableau
def delete_selected_row():
    selected_item = table.selection()
    if selected_item:
        if messagebox.askyesno("Supprimer", "Voulez-vous vraiment supprimer cette entrée ?"):
            # Récupérer l'identifiant de la ligne sélectionnée
            selected_id = table.item(selected_item)['values'][0]

            # Supprimer la ligne sélectionnée de la base de données principale
            conn_main = sqlite3.connect('gestion.db')
            cursor_main = conn_main.cursor()
            cursor_main.execute("DELETE FROM appels WHERE id=?", (selected_id,))
            conn_main.commit()
            conn_main.close()

            # Insérer les données dans la base de données de sauvegarde
            conn_backup = sqlite3.connect('backup.db')
            cursor_backup = conn_backup.cursor()
            cursor_backup.execute('''INSERT INTO backup_appels (nom, prenom, telephone, email, adresse, raison) 
                                  VALUES (?, ?, ?, ?, ?, ?)''', table.item(selected_item)['values'][1:])  
            conn_backup.commit()
            conn_backup.close()

            # Supprimer la ligne du tableau
            table.delete(selected_item)

            # Rafraîchir le tableau pour refléter les modifications
            refresh_table()

            messagebox.showinfo("Suppression réussie", "La ligne sélectionnée a été supprimée.")
    else:
        messagebox.showinfo("Information", "Veuillez sélectionner une ligne à supprimer.")

# Fonction pour déconnecter l'utilisateur
def logout():
    if messagebox.askokcancel("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
        window.destroy()
        subprocess.run(["python", "connexion.py"])

# Fonction pour afficher la corbeille
def show_backup():
    subprocess.run(["python", "backup.py"])

# Créer la fenêtre principale
window = tk.Tk()
window.title("gestion des appels")
window.geometry("1400x900")
window.iconbitmap("images/logo delorme.ico")
window.configure(background='#36393e')

# Message de bienvenue
welcome_label = tk.Label(window, text="Bienvenue, {}!".format(logged_in_username), font=("Arial", 14), bg="#36393E", fg='White')
welcome_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=20)

# Bouton de déconnexion
logout_button = tk.Button(window, text="Déconnexion", font=("Arial", 10), bg="#000000", fg='White', command=logout)
logout_button.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=(0, 5))
logout_button.config(width=10)

# Bouton pour voir la corbeille
show_backup_button = tk.Button(window, text="Voir la corbeille", font=("Arial", 10), bg="#000000", fg='White', command=show_backup)
show_backup_button.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=(0, 5))
show_backup_button.config(width=15)

# Formulaire pour enregistrer un appel
frame = tk.Frame(window, bg='#36393e')
frame.pack(padx=20, pady=20)

# Zone de saisie pour le nom
label_nom = tk.Label(frame, text="Nom:", bg='#36393e', fg='White', font=('Arial', 10))
label_nom.grid(row=0, column=0, padx=5, pady=5)
entry_nom = tk.Entry(frame)
entry_nom.grid(row=0, column=1, padx=5, pady=5)

# Zone de saisie pour le prénom
label_prenom = tk.Label(frame, text="Prénom:", bg='#36393e', fg='White', font=('Arial', 10))
label_prenom.grid(row=1, column=0, padx=5, pady=5)
entry_prenom = tk.Entry(frame)
entry_prenom.grid(row=1, column=1, padx=5, pady=5)

# Zone de saisie pour le téléphone
label_telephone = tk.Label(frame, text="Téléphone:", bg='#36393e', fg='White', font=('Arial', 10))
label_telephone.grid(row=2, column=0, padx=5, pady=5)
entry_telephone = tk.Entry(frame)
entry_telephone.grid(row=2, column=1, padx=5, pady=5)

# Zone de saisie pour l'email
label_email = tk.Label(frame, text="Email:", bg='#36393e', fg='White', font=('Arial', 10))
label_email.grid(row=3, column=0, padx=5, pady=5)
entry_email = tk.Entry(frame)
entry_email.grid(row=3, column=1, padx=5, pady=5)

# Zone de saisie pour l'adresse
label_adresse = tk.Label(frame, text="Adresse:", bg='#36393e', fg='White', font=('Arial', 10))
label_adresse.grid(row=4, column=0, padx=5, pady=5)
entry_adresse = tk.Entry(frame)
entry_adresse.grid(row=4, column=1, padx=5, pady=5)

# Zone de saisie pour la raison
label_raison = tk.Label(frame, text="Raison de l'appel:", bg='#36393e', fg='White', font=('Arial', 10))
label_raison.grid(row=5, column=0, padx=5, pady=5)
entry_raison = tk.Entry(frame)
entry_raison.grid(row=5, column=1, padx=5, pady=5)

# Bouton pour enregistrer l'appel
btn_enregistrer = tk.Button(frame, text="Enregistrer l'appel", command=save_call)
btn_enregistrer.grid(row=6, columnspan=2, padx=5, pady=5)

# Création du tableau après les boutons
table_frame = tk.Frame(window)
table_frame.pack(padx=20, pady=(0, 20))

table = ttk.Treeview(table_frame, columns=("ID", "Nom", "Prénom", "Téléphone", "Email", "Adresse", "Raison de l'appel"), show="headings")
table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Ajouter des en-têtes au tableau
table.heading("ID", text="ID")
table.heading("Nom", text="Nom")
table.heading("Prénom", text="Prénom")
table.heading("Téléphone", text="Téléphone")
table.heading("Email", text="Email")
table.heading("Adresse", text="Adresse")
table.heading("Raison de l'appel", text="Raison de l'appel")

# Barre de défilement pour le tableau
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
table.configure(yscrollcommand=scrollbar.set)

# Bouton pour supprimer la ligne sélectionnée
btn_supprimer = tk.Button(frame, text="Supprimer l'appel sélectionné", command=delete_selected_row)
btn_supprimer.grid(row=7, columnspan=2, padx=5, pady=5)

# Appeler la fonction refresh_table() pour charger les données au démarrage de l'application
refresh_table()

# Lancer l'application
window.mainloop()
