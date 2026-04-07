import tkinter as tk
from tkinter import messagebox
import subprocess
import os

ROOT_PASSWORD = "Kxrse1999"
PSQL_BIN = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"

def run_sql(commands: list[str], dbname: str = "postgres") -> tuple[bool, str]:
    sql = "\n".join(commands)
    full_env = os.environ.copy()
    full_env["PGPASSWORD"] = ROOT_PASSWORD
    try:
        result = subprocess.run(
            [PSQL_BIN, "-U", "postgres", "-d", dbname],
            input=sql,
            capture_output=True,
            text=True,
            timeout=10,
            env=full_env
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except FileNotFoundError:
        return False, f"psql.exe not found at:\n{PSQL_BIN}"
    except subprocess.TimeoutExpired:
        return False, "Connection timed out."
    except Exception as e:
        return False, str(e)

def delete_database():
    name = entry_name.get().strip()

    if not name:
        messagebox.showwarning("Missing Field", "Database name is required.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"This will permanently delete:\n  Database: '{name}'\n  User: '{name}'\n\nAre you sure?"
    )
    if not confirm:
        return

    ok, err = run_sql([
        f"DROP DATABASE IF EXISTS {name};",
        f"DROP USER IF EXISTS {name};"
    ])
    if ok:
        messagebox.showinfo("Deleted", f"Database '{name}' and user '{name}' removed.")
        entry_name.delete(0, tk.END)
    else:
        messagebox.showerror("Error", f"Failed:\n{err}")

root = tk.Tk()
root.title("PostgreSQL — Delete Database")
root.resizable(False, False)
root.configure(bg="#1e1e2e")

FONT_LABEL = ("Consolas", 10)
FONT_ENTRY = ("Consolas", 10)
FONT_BTN   = ("Consolas", 11, "bold")
BG         = "#1e1e2e"
FG         = "#cdd6f4"
ENTRY_BG   = "#313244"
ACCENT     = "#f38ba8"

pad = {"padx": 16, "pady": 6}

tk.Label(root, text="DELETE POSTGRES DATABASE", font=("Consolas", 13, "bold"),
         bg=BG, fg=ACCENT).grid(row=0, column=0, columnspan=2, pady=(18, 10))

tk.Label(root, text="Name", font=FONT_LABEL, bg=BG, fg=FG, anchor="w")\
    .grid(row=1, column=0, sticky="w", **pad)
entry_name = tk.Entry(root, font=FONT_ENTRY, bg=ENTRY_BG, fg=FG,
                      insertbackground=FG, relief="flat", width=28)
entry_name.grid(row=1, column=1, **pad)

tk.Label(root, text="(drops database and user)", font=("Consolas", 8),
         bg=BG, fg="#6c7086").grid(row=2, column=0, columnspan=2)

tk.Button(root, text="DELETE", font=FONT_BTN,
          bg=ACCENT, fg="#1e1e2e", activebackground="#eba0ac",
          relief="flat", cursor="hand2", command=delete_database)\
    .grid(row=3, column=0, columnspan=2, pady=(12, 18), ipadx=10, ipady=6)

root.mainloop()