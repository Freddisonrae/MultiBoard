import tkinter as tk

# Fenster vorbereiten
root = tk.Tk()
root.title("Raum 21 Mathe Challenge")
root.geometry("1000x600")
root.configure(bg="white")

# Frame-Wechsel Funktion
def show_frame(frame):
    frame.tkraise()

# Beide Screens anlegen
challenge_frame = tk.Frame(root, bg="white")
leaderboard_frame = tk.Frame(root, bg="white")

for f in (challenge_frame, leaderboard_frame):
    f.place(relwidth=1, relheight=1)




# Linke Box (Schwierigkeitsbereich + Frage)
left = tk.Frame(challenge_frame, bd=1, relief="solid")
left.place(relx=0, rely=0, relwidth=0.33, relheight=1)

tk.Label(left, text="Leicht", font=("Arial", 16)).pack(fill="x", pady=10)
tk.Label(left, text="Was ist 15 + 6 (-2)^3", font=("Arial", 16), wraplength=250).pack(pady=150)

# Mittlere Box (Titel + Antworten)
mid = tk.Frame(challenge_frame, bd=1, relief="solid")
mid.place(relx=0.33, rely=0, relwidth=0.34, relheight=1)

tk.Label(mid, text="Raum 21\nMathe Challenge", font=("Arial", 20)).pack(pady=20)

# Antwortfelder A–D
options = ["A", "B", "C", "D"]
for opt in options:
    row = tk.Frame(mid)
    row.pack(pady=15)

    # Antwortkreis
    c = tk.Canvas(row, width=50, height=50)
    c.create_oval(10, 10, 40, 40, outline="black", width=2)
    c.create_text(25, 25, text=opt, font=("Arial", 14))
    c.pack(side="left")

    # Eingabefeld
    tk.Entry(row, font=("Arial", 14), width=30).pack(side="left", padx=10)

# Rechte Box (Leaderboard-Seite + Umschaltbutton)
right = tk.Frame(challenge_frame, bd=1, relief="solid")
right.place(relx=0.67, rely=0, relwidth=0.33, relheight=1)

tk.Label(right, text="Leaderboard", font=("Arial", 16)).pack(fill="x", pady=10)

# Umschalten  Leaderboard-Screen
tk.Button(
    right,
    text="Leaderboard öffnen",
    font=("Arial", 14),
    command=lambda: show_frame(leaderboard_frame)
).pack(pady=40)





# Linke Box (Räume)
lb_left = tk.Frame(leaderboard_frame, bd=1, relief="solid")
lb_left.place(relx=0, rely=0, relwidth=0.33, relheight=1)

tk.Label(lb_left, text="Leaderboard", font=("Arial", 16)).pack(fill="x", pady=10)
tk.Label(lb_left, text="Woche 14", font=("Arial", 14, "underline")).pack(pady=5)

rooms = ["Raum 22", "Raum 5", "Raum 12", "Raum 21", "Raum 7", "Raum 19"]
for r in rooms:
    btn = tk.Button(lb_left, text=r, font=("Arial", 14), width=12)
    if r == "Raum 21":
        btn.configure(relief="solid", bd=2)
    btn.pack(pady=5)

# Mitte (Platz + Zurück-Button)
lb_mid = tk.Frame(leaderboard_frame, bd=1, relief="solid")
lb_mid.place(relx=0.33, rely=0, relwidth=0.34, relheight=1)

tk.Label(lb_mid, text="Ihr seid Platz:\nNr. 4 !!", font=("Arial", 24)).pack(pady=40)

# Umschalten  Challenge-Screen
tk.Button(
    lb_mid,
    text="Zurück zu Challenge",
    font=("Arial", 14),
    command=lambda: show_frame(challenge_frame)
).pack(pady=40)

# Rechte Box (Pokal + Kekse)
lb_right = tk.Frame(leaderboard_frame, bd=1, relief="solid")
lb_right.place(relx=0.67, rely=0, relwidth=0.33, relheight=1)

tk.Label(lb_right, text="Gewinnsammlung", font=("Arial", 16)).pack(pady=20)

# Pokal rudimentär zeichnen
cup = tk.Canvas(lb_right, width=200, height=250)
cup.pack()
cup.create_rectangle(80, 150, 120, 250, fill="black")
cup.create_polygon(50, 50, 150, 50, 170, 150, 30, 150, fill="black")

tk.Label(lb_right, text="36 Kekse", font=("Arial", 16)).pack(pady=20)


# Startscreen setzen
show_frame(challenge_frame)

root.mainloop()
#goonhub