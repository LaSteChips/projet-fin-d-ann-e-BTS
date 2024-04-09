import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="votre_mot_de_passe",  # Assurez-vous de remplacer "votre_mot_de_passe" par votre mot de passe MySQL
    database="call_management"
)
cursor = conn.cursor()

# Fonction pour supprimer la ligne sélectionnée dans le tableau de sauvegarde
def delete_selected_row_backup():
    selected_item = table.selection()
    if selected_item:
        if messagebox.askyesno("Supprimer", "Voulez-vous vraiment supprimer cette entrée de la corbeille ?"):
            # Récupérer les données de la ligne sélectionnée
            selected_values = table.item(selected_item)['values']

            # Supprimer la ligne sélectionnée de la table "bin"
            cursor.execute("DELETE FROM bin WHERE id=%s", (selected_values[0],))
            conn.commit()

            # Rafraîchir le tableau pour refléter les modifications
            refresh_table_backup()
    else:
        messagebox.showinfo("Information", "Veuillez sélectionner une ligne à supprimer.")

# Fonction pour rafraîchir le tableau de sauvegarde avec les données de la table "bin"
def refresh_table_backup():
    # Effacer toutes les lignes du tableau
    for row in table.get_children():
        table.delete(row)

    # Récupérer les données depuis la table "bin"
    cursor.execute("SELECT * FROM bin")
    rows = cursor.fetchall()

    # Ajouter les données au tableau
    for row in rows:
        table.insert("", "end", values=(row[1], row[2], row[3], row[4], row[5], row[6]))

# Créer la fenêtre principale pour l'application de sauvegarde
def main():
    window_backup = tk.Tk()
    window_backup.title("Corbeille des appels sauvegardés")
    window_backup.geometry("1250x300")
    window_backup.configure(background='#36393e')

    # Tableau pour afficher les appels sauvegardés
    table_frame_backup = tk.Frame(window_backup)
    table_frame_backup.pack(padx=20, pady=(20, 0))

    global table
    table = ttk.Treeview(table_frame_backup, columns=("Nom", "Prénom", "Téléphone", "Email", "Adresse", "Raison de l'appel"), show="headings")
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Ajouter des en-têtes au tableau
    table.heading("Nom", text="Nom")
    table.heading("Prénom", text="Prénom")
    table.heading("Téléphone", text="Téléphone")
    table.heading("Email", text="Email")
    table.heading("Adresse", text="Adresse")
    table.heading("Raison de l'appel", text="Raison de l'appel")

    # Bouton pour supprimer la ligne sélectionnée de la corbeille
    btn_supprimer_backup = tk.Button(window_backup, text="Supprimer l'appel sélectionné", command=delete_selected_row_backup)
    btn_supprimer_backup.pack(pady=10)

    # Afficher les données initiales dans le tableau de sauvegarde
    refresh_table_backup()

    # Lancer l'application de sauvegarde
    window_backup.mainloop()

if __name__ == "__main__":
    main()
