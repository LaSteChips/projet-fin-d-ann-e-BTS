import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Fonction pour supprimer la ligne sélectionnée dans le tableau de sauvegarde
def delete_selected_row_backup():
    selected_item = table.selection()
    if selected_item:
        if messagebox.askyesno("Supprimer", "Voulez-vous vraiment supprimer cette entrée de la corbeille ?"):
            # Récupérer les données de la ligne sélectionnée
            selected_values = table.item(selected_item)['values']

            # Supprimer la ligne sélectionnée de la base de données de sauvegarde
            conn_backup = sqlite3.connect('backup.db')
            cursor_backup = conn_backup.cursor()
            cursor_backup.execute("DELETE FROM backup_appels WHERE id=?", (selected_values[0],))
            conn_backup.commit()
            conn_backup.close()

            # Rafraîchir le tableau pour refléter les modifications
            refresh_table_backup()
    else:
        messagebox.showinfo("Information", "Veuillez sélectionner une ligne à supprimer.")

# Fonction pour rafraîchir le tableau de sauvegarde avec les données de la base de données de sauvegarde
def refresh_table_backup():
    # Effacer toutes les lignes du tableau
    for row in table.get_children():
        table.delete(row)

    # Récupérer les données depuis la base de données de sauvegarde
    conn_backup = sqlite3.connect('backup.db')
    cursor_backup = conn_backup.cursor()
    cursor_backup.execute("SELECT * FROM backup_appels")
    rows = cursor_backup.fetchall()
    conn_backup.close()

    # Ajouter les données au tableau
    for row in rows:
        table.insert("", "end", values=(row[1], row[2], row[3], row[4], row[5], row[6]))

# Créer la fenêtre principale pour l'application de sauvegarde
def main():
    window_backup = tk.Tk()
    window_backup.title("Corbeille des appels sauvegardés")
    window_backup.geometry("1250x300")
    window_backup.iconbitmap("images/logo delorme.ico")
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

    # Barre de défilement pour le tableau
    scrollbar = ttk.Scrollbar(table_frame_backup, orient="vertical", command=table.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")
    table.configure(yscrollcommand=scrollbar.set)

    # Bouton pour supprimer la ligne sélectionnée de la corbeille
    btn_supprimer_backup = tk.Button(window_backup, text="Supprimer l'appel sélectionné", command=delete_selected_row_backup)
    btn_supprimer_backup.pack(pady=10)

    # Afficher les données initiales dans le tableau de sauvegarde
    refresh_table_backup()

    # Lancer l'application de sauvegarde
    window_backup.mainloop()

if __name__ == "__main__":
    main()
