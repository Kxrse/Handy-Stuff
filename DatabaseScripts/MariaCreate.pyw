import tkinter as tk
from tkinter import messagebox
import subprocess

ROOT_PASSWORD = "Kxrse1999"
MARIADB_BIN = r"C:\Program Files\MariaDB 10.11\bin\mysql.exe"

def run_sql(commands: list[str]) -> tuple[bool, str]:
    sql = "\n".join(commands)
    try:
        result = subprocess.run(
            [MARIADB_BIN, "-u", "root", f"-p{ROOT_PASSWORD}"],
            input=sql,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except FileNotFoundError:
        return False, f"mysql.exe not found at:\n{MARIADB_BIN}"
    except subprocess.TimeoutExpired:
        return False, "Connection timed out."
    except Exception as e:
        return False, str(e)

def create_database():
    name     = entry_name.get().strip()
    password = entry_pass.get().strip()

    if not name or not password:
        messagebox.showwarning("Missing Fields", "All fields are required.")
        return

    commands = [
        f"CREATE DATABASE IF NOT EXISTS `{name}`;",
        f"CREATE USER IF NOT EXISTS '{name}'@'127.0.0.1' IDENTIFIED BY '{password}';",
        f"GRANT ALL PRIVILEGES ON `{name}`.* TO '{name}'@'127.0.0.1';",
        "FLUSH PRIVILEGES;"
    ]

    ok, err = run_sql(commands)
    if ok:
        messagebox.showinfo("Success", f"Database '{name}' created.\nUser '{name}' granted access.")
        entry_name.delete(0, tk.END)
        entry_pass.delete(0, tk.END)
    else:
        messagebox.showerror("Error", f"Failed:\n{err}")

# =============================================================================
# UI
# =============================================================================

root = tk.Tk()
root.title("MariaDB — Create Database")
root.resizable(False, False)
root.configure(bg="#1e1e2e")

FONT_LABEL = ("Consolas", 10)
FONT_ENTRY = ("Consolas", 10)
FONT_BTN   = ("Consolas", 11, "bold")
BG         = "#1e1e2e"
FG         = "#cdd6f4"
ENTRY_BG   = "#313244"
ACCENT     = "#89b4fa"

pad = {"padx": 16, "pady": 6}

tk.Label(root, text="CREATE DATABASE", font=("Consolas", 13, "bold"),
         bg=BG, fg=ACCENT).grid(row=0, column=0, columnspan=2, pady=(18, 10))

tk.Label(root, text="Name", font=FONT_LABEL, bg=BG, fg=FG, anchor="w")\
    .grid(row=1, column=0, sticky="w", **pad)
entry_name = tk.Entry(root, font=FONT_ENTRY, bg=ENTRY_BG, fg=FG,
                      insertbackground=FG, relief="flat", width=28)
entry_name.grid(row=1, column=1, **pad)

tk.Label(root, text="User Password", font=FONT_LABEL, bg=BG, fg=FG, anchor="w")\
    .grid(row=2, column=0, sticky="w", **pad)
entry_pass = tk.Entry(root, font=FONT_ENTRY, bg=ENTRY_BG, fg=FG,
                      insertbackground=FG, relief="flat", width=28, show="*")
entry_pass.grid(row=2, column=1, **pad)

tk.Label(root, text="(database name = username)", font=("Consolas", 8),
         bg=BG, fg="#6c7086").grid(row=3, column=0, columnspan=2)

tk.Button(root, text="CREATE", font=FONT_BTN,
          bg=ACCENT, fg="#1e1e2e", activebackground="#74c7ec",
          relief="flat", cursor="hand2", command=create_database)\
    .grid(row=4, column=0, columnspan=2, pady=(12, 18), ipadx=10, ipady=6)

root.mainloop()