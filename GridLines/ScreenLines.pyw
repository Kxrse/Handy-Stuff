import tkinter as tk
from tkinter import ttk
import ctypes
from screeninfo import get_monitors

LINE_COLOR = "#00ffff"
LINE_ALPHA = 0.4
SPACING = 50
PRESETS = ["#00ffff", "#ff00ff", "#ffffff", "#ff4444", "#44ff88", "#ffaa00", "#4488ff", "#ff88cc"]

overlay = None
current_color = LINE_COLOR


def apply_click_through(window):
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)


def show_overlay(monitor):
    global overlay
    hide_overlay()

    overlay = tk.Toplevel()
    overlay.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", alpha_var.get())
    overlay.configure(bg="black")
    overlay.wm_attributes("-transparentcolor", "black")

    canvas = tk.Canvas(overlay, width=monitor.width, height=monitor.height, bg="black", highlightthickness=0)
    canvas.pack()

    overlay.update_idletasks()
    apply_click_through(overlay)

    spacing = int(spacing_var.get())
    cx, cy = monitor.width // 2, monitor.height // 2

    for x in range(cx, monitor.width, spacing):
        canvas.create_line(x, 0, x, monitor.height, fill=current_color)
    for x in range(cx - spacing, 0, -spacing):
        canvas.create_line(x, 0, x, monitor.height, fill=current_color)
    for y in range(cy, monitor.height, spacing):
        canvas.create_line(0, y, monitor.width, y, fill=current_color)
    for y in range(cy - spacing, 0, -spacing):
        canvas.create_line(0, y, monitor.width, y, fill=current_color)


def hide_overlay():
    global overlay
    if overlay:
        overlay.destroy()
        overlay = None


def refresh_overlay():
    if overlay:
        toggle()
        toggle()


def toggle():
    monitors = get_monitors()
    monitor = next((m for m in monitors if str(m) == monitor_var.get()), monitors[0])
    if toggle_btn.config("text")[-1] == "Enable":
        show_overlay(monitor)
        toggle_btn.config(text="Disable")
        status_dot.config(fg="#00ff88")
    else:
        hide_overlay()
        toggle_btn.config(text="Enable")
        status_dot.config(fg="#555555")


def pick_color(color=None):
    global current_color
    if color:
        current_color = color
    else:
        val = hex_var.get().strip()
        if len(val) == 7 and val.startswith("#"):
            current_color = val
        else:
            return
    color_preview.config(bg=current_color)
    hex_var.set(current_color)
    for i, btn in enumerate(preset_btns):
        btn.config(relief="sunken" if PRESETS[i] == current_color else "flat")
    refresh_overlay()


def on_alpha_change(val):
    alpha_label.config(text=f"{float(val):.2f}")
    if overlay:
        overlay.attributes("-alpha", float(val))


def on_spacing_change(val):
    spacing_label.config(text=f"{int(float(val))}px")
    refresh_overlay()


# --- Root Window ---
root = tk.Tk()
root.title("Grid Overlay")
root.resizable(False, False)
root.configure(bg="#1a1a1a")

style = ttk.Style()
style.theme_use("clam")
style.configure(".", background="#1a1a1a", foreground="#cccccc", fieldbackground="#2a2a2a", bordercolor="#333333")
style.configure("TLabel", background="#1a1a1a", foreground="#cccccc", font=("Consolas", 9))
style.configure("TButton", background="#2a2a2a", foreground="#cccccc", bordercolor="#444444", focuscolor="none", font=("Consolas", 9))
style.map("TButton", background=[("active", "#3a3a3a")])
style.configure("TCombobox", fieldbackground="#2a2a2a", background="#2a2a2a", foreground="#cccccc", bordercolor="#444444")
style.configure("TScale", background="#1a1a1a", troughcolor="#2a2a2a", bordercolor="#444444")
style.configure("TSeparator", background="#333333")

# --- Header ---
header = tk.Frame(root, bg="#111111", pady=8)
header.grid(row=0, column=0, columnspan=3, sticky="ew")
tk.Label(header, text="GRID OVERLAY", bg="#111111", fg="#ffffff", font=("Consolas", 11, "bold")).pack(side="left", padx=12)
status_dot = tk.Label(header, text="●", bg="#111111", fg="#555555", font=("Consolas", 12))
status_dot.pack(side="right", padx=12)

# --- Monitor ---
monitors = get_monitors()
monitor_var = tk.StringVar(value=str(monitors[0]))
ttk.Label(root, text="MONITOR").grid(row=1, column=0, sticky="w", padx=12, pady=(10, 2))
ttk.Combobox(root, textvariable=monitor_var, values=[str(m) for m in monitors], width=36, state="readonly").grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew")

ttk.Separator(root, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew", padx=12, pady=4)

# --- Spacing ---
spacing_var = tk.DoubleVar(value=SPACING)
ttk.Label(root, text="SPACING").grid(row=4, column=0, sticky="w", padx=12, pady=(6, 2))
spacing_label = ttk.Label(root, text=f"{SPACING}px", width=5)
spacing_label.grid(row=4, column=2, sticky="e", padx=12)
ttk.Scale(root, from_=10, to=200, variable=spacing_var, command=on_spacing_change, orient="horizontal", length=220).grid(row=5, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew")

# --- Opacity ---
alpha_var = tk.DoubleVar(value=LINE_ALPHA)
ttk.Label(root, text="OPACITY").grid(row=6, column=0, sticky="w", padx=12, pady=(6, 2))
alpha_label = ttk.Label(root, text=f"{LINE_ALPHA:.2f}", width=5)
alpha_label.grid(row=6, column=2, sticky="e", padx=12)
ttk.Scale(root, from_=0.05, to=1.0, variable=alpha_var, command=on_alpha_change, orient="horizontal", length=220).grid(row=7, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew")

ttk.Separator(root, orient="horizontal").grid(row=8, column=0, columnspan=3, sticky="ew", padx=12, pady=4)

# --- Color ---
ttk.Label(root, text="COLOR").grid(row=9, column=0, sticky="w", padx=12, pady=(6, 2))
hex_var = tk.StringVar(value=current_color)
hex_entry = tk.Entry(root, textvariable=hex_var, bg="#2a2a2a", fg="#cccccc", insertbackground="#cccccc",
                     relief="flat", font=("Consolas", 9), width=10)
hex_entry.grid(row=9, column=1, sticky="w", padx=(0, 4), pady=(6, 2))
color_preview = tk.Label(root, bg=current_color, width=3, relief="flat")
color_preview.grid(row=9, column=2, sticky="ew", padx=(0, 12), pady=(6, 2))
hex_entry.bind("<Return>", lambda e: pick_color())

presets_frame = tk.Frame(root, bg="#1a1a1a")
presets_frame.grid(row=10, column=0, columnspan=3, padx=12, pady=(2, 8), sticky="ew")
preset_btns = []
for i, c in enumerate(PRESETS):
    btn = tk.Label(presets_frame, bg=c, width=3, cursor="hand2", relief="flat")
    btn.pack(side="left", padx=2)
    btn.bind("<Button-1>", lambda e, col=c: pick_color(col))
    preset_btns.append(btn)

ttk.Separator(root, orient="horizontal").grid(row=11, column=0, columnspan=3, sticky="ew", padx=12, pady=4)

# --- Toggle ---
toggle_btn = ttk.Button(root, text="Enable", command=toggle, width=20)
toggle_btn.grid(row=12, column=0, columnspan=3, padx=12, pady=12)

root.mainloop()