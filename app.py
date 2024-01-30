from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox
import subprocess


# DB
conn = sqlite3.connect('user.db')
cursor = conn.cursor

window = tk.Tk()
window.title("Gestion des appels clients")

# custom th window
window.geometry("1024x576")
window.minsize(400, 300)
window.iconbitmap("images/logo delorme.ico")
window.configure(background='#36393e')

# create a frame
frame = tk.Frame(window, bg='#36393e')

# title
label_title = Label(frame, text="Liste des appels", font=("Arial", 40), bg="#36393E", fg='White')
label_title.pack()

# add button
add_button = Button(frame, text="ajouter", font=("Arial", 40),bg="#000000", fg='White')
add_button.pack()

# update button


# delete button


# list view

window.mainloop()