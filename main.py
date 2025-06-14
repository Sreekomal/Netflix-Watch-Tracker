import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import numpy as np
from collections import Counter

# Global variable to store path of the latest simplified CSV
simplified_csv_path = None

plt.style.use('seaborn-v0_8-darkgrid')

CSV_FILE = "netflix_watch_log.csv"
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Title", "Genre", "Watch Time (mins)", "Date Watched", "Rating"])
    df.to_csv(CSV_FILE, index=False)

def save_entry():
    title = entry_title.get()
    genre = entry_genre.get()
    time = entry_time.get()
    date = entry_date.get()
    rating = entry_rating.get()

    if not (title and genre and time and date and rating):
        messagebox.showwarning("Missing Info", "Please fill all fields!")
        return

    try:
        int_time = int(time)
        float_rating = float(rating)
    except ValueError:
        messagebox.showerror("Invalid Input", "Watch time must be an integer & rating a number!")
        return

    new_data = pd.DataFrame([{
        "Title": title,
        "Genre": genre,
        "Watch Time (mins)": int_time,
        "Date Watched": date,
        "Rating": float_rating
    }])

    try:
        existing = pd.read_csv(CSV_FILE)
        updated_df = pd.concat([existing, new_data], ignore_index=True)
    except FileNotFoundError:
        updated_df = new_data

    updated_df.to_csv(CSV_FILE, index=False)
    messagebox.showinfo("Saved", f"'{title}' added to your watch log!")
    clear_fields()

def view_stats():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        messagebox.showerror("Error", "No data found!")
        return

    if df.empty:
        messagebox.showinfo("Stats", "No entries available yet.")
        return

    watch_times = np.array(df["Watch Time (mins)"])
    ratings = np.array(df["Rating"])

    total_entries = len(df)
    total_time = np.sum(watch_times)
    avg_time = np.mean(watch_times)
    avg_rating = np.mean(ratings)
    genres = df["Genre"].dropna().tolist()
    most_common_genre = Counter(genres).most_common(1)[0][0] if genres else "N/A"

    stats_msg = (
        f"📺 Total Shows Watched: {total_entries}\n"
        f"⏱️ Total Watch Time: {total_time} mins\n"
        f"📉 Average Watch Time: {avg_time:.2f} mins\n"
        f"⭐ Average Rating: {avg_rating:.2f}/5\n"
        f"🎬 Most Watched Genre: {most_common_genre}"
    )
    messagebox.showinfo("Your Watch Stats", stats_msg)

def view_netflix_csv_stats():
    global simplified_csv_path
    if not simplified_csv_path:
        messagebox.showerror("Error", "Please upload and simplify a Netflix CSV first!")
        return

    try:
        df = pd.read_csv(simplified_csv_path)
    except FileNotFoundError:
        messagebox.showerror("Error", "Simplified CSV not found!")
        return

    if df.empty or "title" not in df.columns or "date_added" not in df.columns:
        messagebox.showerror("Error", "Invalid or empty Netflix CSV!")
        return

    df["date_added"] = pd.to_datetime(df["date_added"], errors='coerce')
    df.dropna(subset=["date_added"], inplace=True)
    df["Month"] = df["date_added"].dt.strftime('%B')
    df["Year"] = df["date_added"].dt.year

    total_entries = len(df)
    title_counts = df["title"].dropna().value_counts()
    most_watched_title = title_counts.idxmax() if not title_counts.empty else "N/A"
    month_counts = df["Month"].value_counts()
    most_common_month = month_counts.idxmax() if not month_counts.empty else "N/A"
    year_counts = df["Year"].value_counts()
    most_active_year = year_counts.idxmax() if not year_counts.empty else "N/A"


    message = (
        f"🎬 Total Shows Watched: {total_entries}\n"
        f"🔥 Most Watched Title: {most_watched_title}\n"
        f"📆 Most Active Month: {most_common_month}\n"
        f"📅 Most Active Year: {most_active_year}"
    )
    messagebox.showinfo("Netflix History Stats", message)

def show_top_5_titles():
    global simplified_csv_path
    if not simplified_csv_path:
        messagebox.showerror("Error", "Please upload and simplify a Netflix CSV first!")
        return

    try:
        df = pd.read_csv(simplified_csv_path)
    except FileNotFoundError:
        messagebox.showerror("Error", "Simplified CSV not found!")
        return

    if df.empty or "title" not in df.columns:
        messagebox.showerror("Error", "Invalid or empty Netflix CSV!")
        return

    top_titles = df["title"].value_counts().head(5)
    plt.figure(figsize=(8, 5))
    bars = plt.bar(top_titles.index, top_titles.values, color="#E50914")
    plt.title("Top 5 Most Watched Titles", fontsize=14, color="white")
    plt.xlabel("Title", color="white")
    plt.ylabel("Watch Count", color="white")
    plt.xticks(rotation=20, color="white")
    plt.yticks(color="white")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.2, int(yval), ha='center', va='bottom', fontsize=10, color='white')
    plt.gca().set_facecolor("#1e1e1e")
    plt.gcf().patch.set_facecolor("#1e1e1e")
    plt.tight_layout()
    plt.show()

def simplify_csv():
    global simplified_csv_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load file:\n{e}")
        return

    simplified = pd.DataFrame()
    simplified["title"] = df["title"] if "title" in df.columns else ["Unknown"] * len(df)
    simplified["start time"] = df.get("start time", ["Unknown"] * len(df))
    simplified["device"] = df.get("device", ["Unknown"] * len(df))
    simplified["duration"] = df.get("duration", ["Unknown"] * len(df))
    simplified["date_added"] = df.get("date_added", ["Unknown"] * len(df))  # optional, for stats

    simplified_csv_path = "simplified_netflix.csv"
    simplified.to_csv(simplified_csv_path, index=False)
    messagebox.showinfo("Success", f"Simplified CSV saved and ready to use!")


def clear_fields():
    entry_title.delete(0, tk.END)
    entry_genre.delete(0, tk.END)
    entry_time.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_rating.delete(0, tk.END)

# UI Setup
app = tk.Tk()
app.title("📺 Netflix Watch Tracker")
app.geometry("550x650")
app.configure(bg="#1e1e1e")

main_frame = tk.Frame(app, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, bg="#1e1e1e", highlightthickness=0)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

font_style = ("Segoe UI", 10)
entry_bg = "#2e2e2e"
label_fg = "#ffffff"
btn_style = {"bg": "#e50914", "fg": "white", "font": ("Segoe UI", 10, "bold"), "padx": 6, "pady": 6}

scrollable_frame.grid_columnconfigure(0, weight=1)
# App Title at the top
tk.Label(
    scrollable_frame,
    text="🎬 Netflix Watch Tracker",
    fg="#E50914",
    bg="#1e1e1e",
    font=("Segoe UI", 16, "bold")
).grid(row=0, column=0, pady=(20, 10), sticky="ew", padx=100)
row = 1  # Reset row counter after title


for label, var in zip([
    "Title", "Genre", "Watch Time (mins)", "Date Watched (YYYY-MM-DD)", "Your Rating (1-5)"
], [
    "entry_title", "entry_genre", "entry_time", "entry_date", "entry_rating"
]):
    tk.Label(scrollable_frame, text=label, fg=label_fg, bg="#1e1e1e", font=font_style).grid(row=row, column=0, pady=(6, 1), sticky="ew", padx=100)
    globals()[var] = tk.Entry(scrollable_frame, bg=entry_bg, fg="white", font=font_style, insertbackground="white")
    if label.startswith("Date"):
        globals()[var].insert(0, datetime.today().strftime('%Y-%m-%d'))
    globals()[var].grid(row=row+1, column=0, pady=1, ipady=4, ipadx=5, sticky="ew", padx=100)
    row += 2

for heading, subtitle in [
    ("Your Manual Entries", "(Entries you manually typed)"),
    #("Your Uploaded Netflix CSV", "(From official Netflix download)")
]:
    tk.Label(
        scrollable_frame, text=heading, fg="#E50914", bg="#1e1e1e",
        font=("Segoe UI", 11, "bold")
    ).grid(row=row, column=0, pady=(20, 5), sticky="ew", padx=100)
    row += 1
    tk.Label(
        scrollable_frame, text=subtitle, fg="#aaaaaa", bg="#1e1e1e",
        font=("Segoe UI", 8, "italic")
    ).grid(row=row, column=0, pady=(0, 10), sticky="ew", padx=100)
    row += 1

# Buttons under "Your Manual Entries"
manual_buttons = [
    ("💾 Save Entry", save_entry),
    ("📖 View Watch Log", lambda: pd.read_csv(CSV_FILE).to_csv("temp_log.csv") or os.system("notepad temp_log.csv")),
    ("📊 View Stats", view_stats)
]
for text, cmd in manual_buttons:
    tk.Button(scrollable_frame, text=text, command=cmd, **btn_style).grid(row=row, column=0, pady=6, padx=100, sticky="ew")
    row += 1

# Add second section heading
tk.Label(
    scrollable_frame, text="Your Uploaded Netflix CSV", fg="#E50914", bg="#1e1e1e",
    font=("Segoe UI", 11, "bold")
).grid(row=row, column=0, pady=(20, 5), sticky="ew", padx=100)
row += 1
tk.Label(
    scrollable_frame, text="(From official Netflix download)", fg="#aaaaaa", bg="#1e1e1e",
    font=("Segoe UI", 8, "italic")
).grid(row=row, column=0, pady=(0, 10), sticky="ew", padx=100)
row += 1

# Buttons under "Netflix CSV"
netflix_buttons = [
    ("📈 View Netflix CSV Stats", view_netflix_csv_stats),
    ("🏆 Show Top 5 Titles", show_top_5_titles),
    ("📁 Upload & Simplify Netflix CSV", simplify_csv)
]
for text, cmd in netflix_buttons:
    tk.Button(scrollable_frame, text=text, command=cmd, **btn_style).grid(row=row, column=0, pady=6, padx=100, sticky="ew")
    row += 1


app.mainloop()
