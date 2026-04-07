import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import json

CONFIG_PATH = os.path.expanduser("~/.git_manager.json")

BG      = "#101010"
FG      = "#eaeaea"
ACCENT  = "#3a3a3a"
ACCENT2 = "#252525"
SEL_BG  = "#1e1e1e"
DIM     = "#666666"
GREEN   = "#88cc88"
RED     = "#ff5555"
FONT       = ("Consolas", 10)
FONT_BOLD  = ("Consolas", 10, "bold")
FONT_SMALL = ("Consolas", 9)
FONT_TITLE = ("Consolas", 13, "bold")

LICENSES = {
    "MIT": 'MIT License\n\nCopyright (c) {year} {author}\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\n',
    "Apache 2.0": 'Apache License\nVersion 2.0, January 2004\n\nCopyright {year} {author}\n\nLicensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.\n',
    "GPL v3": 'GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\n\nCopyright (C) {year} {author}\n\nThis program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.\n',
    "Unlicense": 'This is free and unencumbered software released into the public domain.\n\nAnyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.\n'
}

PRESETS = {
    "Python": ["__pycache__/", "*.pyc", "*.pyo", ".venv/", "venv/", "*.egg-info/", "dist/", "build/"],
    "Node":   ["node_modules/", "dist/", ".env", "*.log", ".DS_Store"],
    "General":[".DS_Store", "Thumbs.db", "*.log", ".env", ".env.*"],
    "VSCode": [".vscode/", "*.code-workspace"],
}


def run_cmd(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"repos": []}


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


class GitManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("git manager")
        self.configure(bg=BG)
        self.geometry("860x560")
        self.resizable(True, True)

        self.config = load_config()
        self.active_path = tk.StringVar(value="")
        self._selected_index = None

        self._build_ui()
        self._refresh_repo_list()

    def _build_ui(self):
        bar = tk.Frame(self, bg=BG, padx=12, pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="git manager", font=FONT_TITLE, bg=BG, fg=FG).pack(side="left")
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        tk.Frame(body, bg=ACCENT, width=1).pack(side="left", fill="y")

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_actions(right)
        tk.Frame(right, bg=ACCENT, height=1).pack(fill="x")
        self._build_log(right)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=BG, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        hdr = tk.Frame(sidebar, bg=BG, padx=10, pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text="repos", font=FONT_SMALL, bg=BG, fg=DIM).pack(side="left")
        tk.Button(hdr, text="+", font=FONT_BOLD, bg=BG, fg=DIM,
                  activebackground=ACCENT, activeforeground=FG, relief="flat",
                  bd=0, padx=4, command=self._add_existing_repo).pack(side="right")
        tk.Frame(sidebar, bg=ACCENT, height=1).pack(fill="x")

        canvas = tk.Canvas(sidebar, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self._repo_frame = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=self._repo_frame, anchor="nw")
        self._repo_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        tk.Frame(sidebar, bg=ACCENT, height=1).pack(fill="x")
        bot = tk.Frame(sidebar, bg=BG, padx=10, pady=6)
        bot.pack(fill="x")
        tk.Button(bot, text="remove", font=FONT_SMALL, bg=BG, fg=DIM,
                  activebackground=ACCENT, activeforeground=FG, relief="flat",
                  bd=0, command=self._remove_repo).pack(side="left")

    def _build_actions(self, parent):
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="x", padx=12, pady=8)

        path_row = tk.Frame(wrap, bg=BG)
        path_row.pack(fill="x", pady=(0, 6))
        tk.Label(path_row, text="dir:", font=FONT_SMALL, bg=BG, fg=DIM).pack(side="left")
        tk.Label(path_row, textvariable=self.active_path, font=FONT_SMALL,
                 bg=BG, fg=FG, anchor="w").pack(side="left", fill="x", expand=True)

        self.commit_msg = tk.Entry(wrap, font=FONT, bg=ACCENT2, fg=DIM,
                                   insertbackground=FG, relief="flat", bd=4)
        self.commit_msg.insert(0, "commit message...")
        self.commit_msg.bind("<FocusIn>", self._clear_placeholder)
        self.commit_msg.bind("<FocusOut>", self._restore_placeholder)
        self.commit_msg.pack(fill="x", pady=(0, 6))

        grid = tk.Frame(wrap, bg=BG)
        grid.pack(fill="x")
        buttons = [
            ("init repo",          self._init_repo),
            ("set remote",         self._set_remote),
            ("add README",         self._add_readme),
            ("add LICENSE",        self._add_license),
            ("add .gitignore",     lambda: self._add_gitignore(auto=False)),
            ("stage + commit",     self._stage_commit),
            ("push",               self._push),
            ("stage+commit+push",  self._stage_commit_push),
            ("view log",           self._view_log),
            ("rollback (soft)",    self._rollback_soft),
            ("rollback (hard)",    self._rollback_hard),
        ]
        cols = 3
        for i, (label, cmd) in enumerate(buttons):
            r, c = divmod(i, cols)
            tk.Button(grid, text=label, font=FONT_SMALL, bg=ACCENT2, fg=FG,
                      activebackground=ACCENT, activeforeground=FG,
                      relief="flat", bd=0, padx=6, pady=5, command=cmd
                      ).grid(row=r, column=c, padx=3, pady=3, sticky="ew")
        for c in range(cols):
            grid.columnconfigure(c, weight=1)

    def _build_log(self, parent):
        wrap = tk.Frame(parent, bg=BG, padx=12, pady=6)
        wrap.pack(fill="both", expand=True)
        hdr = tk.Frame(wrap, bg=BG)
        hdr.pack(fill="x")
        tk.Label(hdr, text="output", font=FONT_SMALL, bg=BG, fg=DIM).pack(side="left")
        tk.Button(hdr, text="clear", font=FONT_SMALL, bg=BG, fg=DIM,
                  activebackground=ACCENT, activeforeground=FG, relief="flat",
                  bd=0, command=self._clear_log).pack(side="right")
        self.log = tk.Text(wrap, font=("Consolas", 9), bg=ACCENT2, fg=FG,
                           insertbackground=FG, relief="flat", bd=4,
                           state="disabled", wrap="word", height=8)
        self.log.pack(fill="both", expand=True, pady=(4, 0))

    # ── REPO LIST ─────────────────────────────────────────────────────────────

    def _refresh_repo_list(self):
        for w in self._repo_frame.winfo_children():
            w.destroy()
        for i, repo in enumerate(self.config["repos"]):
            name = os.path.basename(repo) or repo
            is_sel = (i == self._selected_index)
            row_bg = SEL_BG if is_sel else BG
            f = tk.Frame(self._repo_frame, bg=row_bg, cursor="hand2")
            f.pack(fill="x")
            lbl = tk.Label(f, text=f"  {name}", font=FONT_SMALL, bg=row_bg, fg=FG, anchor="w", pady=5)
            lbl.pack(fill="x")
            sub = tk.Label(f, text=f"  {repo}", font=("Consolas", 7), bg=row_bg, fg=DIM, anchor="w")
            sub.pack(fill="x")
            tk.Frame(f, bg=ACCENT, height=1).pack(fill="x")
            for w in (f, lbl, sub):
                w.bind("<Button-1>", lambda e, idx=i, p=repo: self._select_repo(idx, p))

    def _select_repo(self, idx, path):
        self._selected_index = idx
        self.active_path.set(path)
        self._refresh_repo_list()
        self._log(f"\n📂 {path}")

    def _add_existing_repo(self):
        path = filedialog.askdirectory()
        if not path: return
        self._save_repo(path)
        self._select_repo(self.config["repos"].index(path), path)

    def _save_repo(self, path):
        if path not in self.config["repos"]:
            self.config["repos"].append(path)
            save_config(self.config)
            self._refresh_repo_list()

    def _remove_repo(self):
        if self._selected_index is None: return
        self.config["repos"].pop(self._selected_index)
        save_config(self.config)
        self._selected_index = None
        self.active_path.set("")
        self._refresh_repo_list()
        self._log("removed from list (files untouched)", DIM)

    # ── LOG ───────────────────────────────────────────────────────────────────

    def _log(self, text, color=None):
        self.log.configure(state="normal")
        if color:
            self.log.tag_config(color, foreground=color)
        self.log.insert("end", text + "\n", color)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _clear_placeholder(self, e=None):
        if self.commit_msg.get() == "commit message...":
            self.commit_msg.delete(0, "end")
            self.commit_msg.configure(fg=FG)

    def _restore_placeholder(self, e=None):
        if not self.commit_msg.get().strip():
            self.commit_msg.insert(0, "commit message...")
            self.commit_msg.configure(fg=DIM)

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _get_path(self):
        p = self.active_path.get().strip()
        if not p or not os.path.isdir(p):
            self._log("✗ no valid repo selected.", RED)
            return None
        return p

    def _run(self, cmd, cwd, label):
        out, err, code = run_cmd(cmd, cwd)
        if out: self._log(out)
        if err: self._log(err, DIM)
        self._log(f"{'✓' if code == 0 else '✗'} {label}", GREEN if code == 0 else RED)
        return code

    def _popup(self, title, fields, on_confirm, size="400x140"):
        win = tk.Toplevel(self, bg=BG)
        win.title(title)
        win.geometry(size)
        win.resizable(False, False)
        vars_ = {}
        for label, default in fields:
            tk.Label(win, text=label, font=FONT, bg=BG, fg=FG).pack(anchor="w", padx=12, pady=(10, 2))
            v = tk.StringVar(value=default)
            tk.Entry(win, textvariable=v, font=FONT, bg=ACCENT2, fg=FG,
                     insertbackground=FG, relief="flat", bd=4).pack(fill="x", padx=12)
            vars_[label] = v
        tk.Button(win, text="confirm", font=FONT, bg=ACCENT, fg=FG, relief="flat",
                  bd=0, padx=10, pady=4,
                  command=lambda: (on_confirm({k: v.get().strip() for k, v in vars_.items()}), win.destroy())
                  ).pack(pady=8)

    # ── GIT ACTIONS ───────────────────────────────────────────────────────────

    def _init_repo(self):
        p = self._get_path()
        if not p: return
        self._log("\n> git init")
        self._run(["git", "init"], p, "repo initialised")
        self._add_gitignore(auto=True)
        self._save_repo(p)

    def _set_remote(self):
        p = self._get_path()
        if not p: return
        def apply(vals):
            url = vals["remote URL:"]
            if not url: return
            out, _, _ = run_cmd(["git", "remote"], p)
            cmd = ["git", "remote", "set-url", "origin", url] if "origin" in out \
                  else ["git", "remote", "add", "origin", url]
            self._run(cmd, p, f"remote → {url}")
        self._popup("set remote origin", [("remote URL:", "")], apply)

    def _stage_commit(self):
        p = self._get_path()
        if not p: return
        msg = self.commit_msg.get().strip()
        if not msg or msg == "commit message...":
            self._log("✗ enter a commit message.", RED); return
        self._log("\n> stage + commit")
        self._run(["git", "add", "-A"], p, "staged")
        self._run(["git", "commit", "-m", msg], p, f'committed: "{msg}"')

    def _push(self):
        p = self._get_path()
        if not p: return
        self._log("\n> git push")
        self._run(["git", "push"], p, "pushed")

    def _stage_commit_push(self):
        p = self._get_path()
        if not p: return
        msg = self.commit_msg.get().strip()
        if not msg or msg == "commit message...":
            self._log("✗ enter a commit message.", RED); return
        self._log("\n> stage + commit + push")
        self._run(["git", "add", "-A"], p, "staged")
        code = self._run(["git", "commit", "-m", msg], p, f'committed: "{msg}"')
        if code == 0:
            self._run(["git", "push"], p, "pushed")

    def _rollback_soft(self):
        p = self._get_path()
        if not p: return
        if not messagebox.askyesno("soft rollback", "Undo last commit? (keeps changes staged)"): return
        self._run(["git", "reset", "--soft", "HEAD~1"], p, "soft rollback done")

    def _rollback_hard(self):
        p = self._get_path()
        if not p: return
        if not messagebox.askyesno("hard rollback", "Hard reset? Changes will be DISCARDED."): return
        self._run(["git", "reset", "--hard", "HEAD~1"], p, "hard rollback done")

    def _view_log(self):
        p = self._get_path()
        if not p: return
        self._log("\n> git log --oneline -10")
        out, err, _ = run_cmd(["git", "log", "--oneline", "-10"], p)
        self._log(out if out else (err or "no commits yet."), None if out else DIM)

    def _add_readme(self):
        p = self._get_path()
        if not p: return
        path = os.path.join(p, "README.md")
        if os.path.exists(path):
            self._log("✗ README.md already exists.", RED); return
        def apply(vals):
            name = vals["project name:"] or os.path.basename(p)
            desc = vals["description:"] or "no description."
            with open(path, "w") as f:
                f.write(f"# {name}\n\n{desc}\n")
            self._log("✓ README.md created", GREEN)
        self._popup("add README.md",
                    [("project name:", os.path.basename(p)), ("description:", "")],
                    apply, size="400x170")

    def _add_license(self):
        p = self._get_path()
        if not p: return
        path = os.path.join(p, "LICENSE")
        if os.path.exists(path):
            self._log("✗ LICENSE already exists.", RED); return

        win = tk.Toplevel(self, bg=BG)
        win.title("add LICENSE")
        win.geometry("400x180")
        win.resizable(False, False)
        tk.Label(win, text="author name:", font=FONT, bg=BG, fg=FG).pack(anchor="w", padx=12, pady=(12, 2))
        author_var = tk.StringVar()
        tk.Entry(win, textvariable=author_var, font=FONT, bg=ACCENT2, fg=FG,
                 insertbackground=FG, relief="flat", bd=4).pack(fill="x", padx=12)
        tk.Label(win, text="license type:", font=FONT, bg=BG, fg=FG).pack(anchor="w", padx=12, pady=(8, 2))
        lic_var = tk.StringVar(value="MIT")
        m = tk.OptionMenu(win, lic_var, *LICENSES.keys())
        m.configure(font=FONT, bg=ACCENT2, fg=FG, activebackground=ACCENT, relief="flat",
                    bd=0, highlightthickness=0)
        m["menu"].configure(bg=ACCENT2, fg=FG, font=FONT)
        m.pack(fill="x", padx=12)

        def confirm():
            import datetime
            author = author_var.get().strip() or "Author"
            year = datetime.datetime.now().year
            content = LICENSES[lic_var.get()].replace("{year}", str(year)).replace("{author}", author)
            with open(path, "w") as f:
                f.write(content)
            self._log(f"✓ LICENSE ({lic_var.get()}) created", GREEN)
            win.destroy()

        tk.Button(win, text="confirm", font=FONT, bg=ACCENT, fg=FG, relief="flat",
                  bd=0, padx=10, pady=4, command=confirm).pack(pady=8)

    def _add_gitignore(self, auto=False):
        p = self._get_path()
        if not p: return
        gi = os.path.join(p, ".gitignore")
        if os.path.exists(gi):
            if not auto:
                self._log("✗ .gitignore already exists.", RED)
            return

        def write(selected):
            lines = ["# self", ".gitignore", ""]
            for name in selected:
                lines += [f"# {name}"] + PRESETS[name] + [""]
            with open(gi, "w") as f:
                f.write("\n".join(lines))
            self._log("✓ .gitignore created (includes itself)", GREEN)

        if auto:
            write(["Python", "General"])
            return

        win = tk.Toplevel(self, bg=BG)
        win.title("add .gitignore")
        win.geometry("300x210")
        win.resizable(False, False)
        tk.Label(win, text="presets:", font=FONT, bg=BG, fg=FG).pack(anchor="w", padx=12, pady=(12, 4))
        vars_ = {}
        for name in PRESETS:
            v = tk.BooleanVar(value=name in ("Python", "General"))
            vars_[name] = v
            tk.Checkbutton(win, text=name, variable=v, font=FONT, bg=BG, fg=FG,
                           selectcolor=ACCENT, activebackground=BG,
                           activeforeground=FG).pack(anchor="w", padx=20)
        tk.Button(win, text="create", font=FONT, bg=ACCENT, fg=FG, relief="flat",
                  bd=0, padx=10, pady=4,
                  command=lambda: (write([n for n, v in vars_.items() if v.get()]), win.destroy())
                  ).pack(pady=8)


if __name__ == "__main__":
    GitManager().mainloop()