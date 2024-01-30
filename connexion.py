from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox
import subprocess


# DB
conn = sqlite3.connect('user.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT)''')
conn.commit()

# open the app if the connection is successful and close the login page
def open_app():
    window.destroy()    
    subprocess.run(["python", "app.py"])

# check who is login
def check_user():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute('''SELECT * FROM user WHERE username = ? AND password = ?''', (username, password))
    user_found = cursor.fetchone()

    if user_found:
        open_app()
    else:
        messagebox.showerror("Erreur de connexion", "Identifiants incorrects")

# user registration
def save_user():
    username = entry_username.get()
    password = entry_password.get()

    # check if the user already exists
    cursor.execute('''SELECT * FROM user WHERE username = ?''', (username,))
    user_exist = cursor.fetchone()

    if user_exist:
        messagebox.showerror("Erreur d'enregistrement", "Ce nom d'utilisateur existe déjà.")
    else:
        # save the user in the DB
        cursor.execute('''INSERT INTO user (username, password) VALUES (?, ?)''', (username, password))
        conn.commit()
        messagebox.showinfo("Enregistrement réussi", "Utilisateur enregistré avec succès !")

# create a window
window = Tk()
window.title("Page de connexion")

# custom the window 
window.geometry("240x140")
window.minsize(320, 140)
window.iconbitmap("images/logo delorme.ico")
window.configure(background='#36393e')

# create a frame
frame = tk.Frame(window, bg='#36393e')
frame.pack(padx=20, pady=20)

# user settings
label_username = tk.Label(frame, text="Nom d'Utilisateur:")
label_username.grid(row=0, column=0, padx=5, pady=5)
entry_username = tk.Entry(frame)
entry_username.grid(row=0, column=1, padx=5, pady=5)

# password settings
label_password = tk.Label(frame, text="Mot de passe:")
label_password.grid(row=1, column=0, padx=5, pady=5)
entry_password = tk.Entry(frame, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

# login button
btn_register = tk.Button(frame, text="S'enregistrer", command=save_user)
btn_register.grid(row=2, column=0, padx=5, pady=5)

# connection button
btn_connection = tk.Button(frame, text="Se connecter", command=check_user)
btn_connection.grid(row=2, column=1, padx=5, pady=5)

window.mainloop()