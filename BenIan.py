import tkinter as tk
from tkinter import ttk, messagebox
import math
import tkinter.font as tkfont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D 

import numpy as np
import sympy as sp
import pandas as pd

x, y, z, t = sp.symbols('x y z t')


class HPPrimeUltimate:
    def __init__(self, root):
        self.root = root
        self.root.title("BenIan")
        
        self.f_btn_norm = tkfont.Font(family="Segoe UI", size=10)
        self.f_btn_bold = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.f_btn_small = tkfont.Font(family="Segoe UI", size=9)
        
        self.colors = {
            "bg_window": "#303030",       
            "bg_app": "#F0F0F0",
            "topbar": "#0055A3",
            "tab_active": "#FFFFFF",
            "tab_inactive": "#E1E1E1",
            "key_num": "#FFFFFF",         
            "key_func": "#E0E0E0",        
            "key_dark": "#202124",        
            "key_enter": "#FFFFFF",       
            "key_orange": "#FF8C00",      
            "key_blue": "#0096D6",        
            "text_main": "#000000",
            "sash": "#505050" 
        }

        self.root.geometry("518x818+100+20") 
        self.root.minsize(280, 500)
        self.root.configure(bg=self.colors["bg_window"])

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0) 
        self.root.rowconfigure(1, weight=1) 

        self.home_last_result = 0.0      
        self.cas_last_result = sp.Integer(0)  
        self.exam_mode = False  
        self.program_env = {}    

        self.shift_mode = False
        self.alpha_mode = False
        self.btn_cache = {} 
        self.matrix_overlay = None
        self.matrix_view = "list"       # "list" ou "edit"
        self.matrix_selected = "M1"
        self.matrix_cursor = (0, 0)     # (row, col) selecionado no editor
        self.matrix_viewport = (0, 0)   # canto superior esquerdo visível no editor
        self.matrix_win = None
        self._init_matrix_store()

        self.KEY_MAP = {
            # --- LINHA 1 ---
            "Vars":  ["Chars", "A"],
            "🧰":   ["Mem", "B"],
            "믐, √◻, |◻|": ["Units", "C"],
            "x t θ n":["Define", "D"],
            "aᵇ/ᶜ":  ["° ' \"", "E"],      
            "⌫":   ["Del", ""],

            # --- LINHA 2 ---
            "xʸ":    ["ⁿ√", "F"],       
            "sin":   ["sin⁻¹", "G"],     
            "cos":   ["cos⁻¹", "H"],
            "tan":   ["tan⁻¹", "I"],
            "ln":    ["eˣ", "J"],        
            "log":   ["10ˣ", "K"],

            # --- LINHA 3 ---
            "x²":    ["√", "L"],         
            "±":     ["|x|", "M"],       
            "( )":    ["'□'", "N"],        
            ",":     ["Eval", "O"],      
            "Enter": ["≈", ""],          

            # --- LINHA 4 ---
            "EEX":   ["Sto", "P"],
            "7":     ["List", "Q"],
            "8":     ["{ }", "R"],
            "9":     ["!,∞,→", "S"],
            "÷":     ["x⁻¹", "T"],       

            # --- LINHA 5 ---
            "4":     ["Matrix", "U"],
            "5":     ["[ ]", "V"],
            "6":     ["≤, ≥, ≠", "W"],         
            "*":     ["∠", "X"],

            # --- LINHA 6 ---
            "1":     ["Program", "Y"],
            "2":     ["i", "Z"],
            "3":     ["π", "#"],         
            "-":     ["Base", ":"],

            # --- LINHA 7 ---
            "0":     ["Notes", '" "'],
            ".":     ["=", " "],
            "⊔":     ["_", " "],
            "+":     ["Ans", ";"],
            "On":    ["Off", ""],

            # --- TECLAS PRETAS ---
            "Apps":  ["Info", ""], "Home":  ["Settings", ""], "Esc":   ["Clear", ""],
            "Symb":  ["Setup", ""], "Plot":  ["Setup", ""], "Num":   ["Setup", ""],
            "Help":  ["User", ""], "View":  ["Copy", ""], "Menu":  ["Paste", ""], "CAS":   ["Settings", ""]
        }

        self._create_top_bar()

        self.main_pane = tk.PanedWindow(
            self.root, 
            orient=tk.VERTICAL, 
            bg=self.colors["bg_window"],
            sashwidth=6,
            sashrelief="raised",
            showhandle=False 
        )
        self.main_pane.grid(row=1, column=0, sticky="nsew")

        self._create_notebook_and_apps()
        self._create_keypad()

        self.entry_home.focus_set()
        
        self.root.bind('<Configure>', self._on_resize)

    def _create_top_bar(self):
        self.topbar = tk.Frame(self.root, height=25)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.pack_propagate(False) 

        self.app_label = tk.Label(
            self.topbar, 
            text="Function", 
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg=self.colors["topbar"] 
        )
        self.app_label.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        from datetime import datetime
        self.clock_label = tk.Label(
            self.topbar,
            text=datetime.now().strftime("%H:%M"),
            font=("Segoe UI", 9),
            fg="white",
            bg=self.colors["topbar"]
        )
        self.clock_label.pack(side=tk.RIGHT, padx=5)
        
        self.exam_indicator = tk.Label(
            self.topbar, text="EXAM", fg="#FFCCCC", bg=self.colors["topbar"], 
            font=("Segoe UI", 8, "bold")
        )
    
    def _update_topbar_style(self):
        """Atualiza cor e texto da barra baseado na aba ativa"""
        current_idx = self.notebook.index(self.notebook.select())
        
        app_config = {
            self.idx_home:   ("Início",    "#0055A3"),
            self.idx_cas:    ("CAS",       "#C62828"),
            self.idx_plot2d: ("Função",    "#FF9800"),
            self.idx_plot3d: ("Gráfico 3D","#FF5722"), 
            self.idx_stats:  ("Estatística","#9C27B0"), 
            self.idx_sheet:  ("Planilha",  "#4CAF50"),
            self.idx_prog:   ("Python",    "#FFC107"), 
        }

        name, color = app_config.get(current_idx, ("HP Prime", "#333333"))

        if self.exam_mode:
            name = f"{name} (EXAM)"
            color = "#8B0000" 
            self.exam_indicator.pack(side=tk.RIGHT, padx=5)
        else:
            self.exam_indicator.pack_forget()

        self.topbar.config(bg=color)
        self.app_label.config(text=name, bg=color)
        self.clock_label.config(bg=color)
        self.exam_indicator.config(bg=color)

    def toggle_exam_mode(self):
        self.exam_mode = not self.exam_mode

        if self.exam_mode:
            self.topbar.configure(bg="#8B0000")
            self.title_label.configure(bg="#8B0000")
            self.exam_led.configure(fg="#FF0000", bg="#8B0000")
            self.exam_label.configure(text="Mode Prova: ON", bg="#8B0000")
            self.exam_button.configure(bg="#660000")

            self.notebook.tab(self.idx_cas, state="disabled")
            self.notebook.tab(self.idx_prog, state="disabled")
        else:
            self.topbar.configure(bg="#0055A3")
            self.title_label.configure(bg="#0055A3")
            self.exam_led.configure(fg="#00FF00", bg="#0055A3")
            self.exam_label.configure(text="Mode Prova: OFF", bg="#0055A3")
            self.exam_button.configure(bg="#003f7d")

            self.notebook.tab(self.idx_cas, state="normal")
            self.notebook.tab(self.idx_prog, state="normal")

    def _create_notebook_and_apps(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.layout('TNotebook.Tab', []) 
        self.style.configure("TNotebook", background=self.colors["bg_window"], borderwidth=0)

        self.notebook = ttk.Notebook(self.main_pane) 
        
        self.main_pane.add(self.notebook, stretch="always", height=250)

        self._create_home_app()
        self._create_cas_app()
        self._create_plot2d_app()
        self._create_plot3d_app()
        self._create_stats_app()
        self._create_spreadsheet_app()
        self._create_programs_app()
        
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
    
    def _on_tab_change(self, event):
        current = self.notebook.index(self.notebook.select())

        if current == self.idx_home:
            self.entry_home.focus_set()
        elif current == self.idx_cas and not self.exam_mode:
            self.entry_cas.focus_set()
        elif current == self.idx_plot2d:
            self.entry_plot.focus_set()
        elif current == self.idx_plot3d:
            self.entry_plot3d.focus_set()
        elif current == self.idx_stats:
            self.entry_stat_x.focus_set()
        elif current == self.idx_sheet:
            if hasattr(self, 'cells') and (0,0) in self.cells:
                self.cells[(0, 0)].focus_set()
        elif current == self.idx_prog and not self.exam_mode:
            self.program_editor.focus_set()
            
        self._update_topbar_style()

    def _create_home_app(self):
        self.tab_home = tk.Frame(self.notebook, bg="#e0e0e0") 
        self.notebook.add(self.tab_home, text=" Início ")

        self.idx_home = self.notebook.index(self.tab_home)

        self.home_history = tk.Text(
            self.tab_home,
            height=1,  
            font=('Consolas', 11),
            state='disabled',
            bg="#f7f7f7"
        )
        self.home_history.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.entry_home = tk.Entry(self.tab_home, font=('Arial', 14), bd=2, relief="sunken")
        self.entry_home.pack(padx=5, pady=5, fill=tk.X)
        self.entry_home.bind("<Return>", lambda e: self.process_home())

    def _home_log(self, expr, result):
        self.home_history.config(state='normal')
        self.home_history.insert(tk.END, f"> {expr}\n")
        self.home_history.insert(tk.END, f"≈ {result}\n\n")
        self.home_history.see(tk.END)
        self.home_history.config(state='disabled')
    
    def _sanitize_input(self, expr_str):
        """
        O GRANDE TRADUTOR: 
        Converte símbolos visuais (Unicode) do Catálogo para sintaxe Python/SymPy válida.
        """
        if not expr_str:
            return ""
            
        # Mapa Completo de Substituição
        replacements = {
            # --- Operadores Básicos ---
            "÷": "/", 
            "×": "*", 
            "^": "**", 
            "²": "**2",
            "−": "-",  # Menos 'en-dash'
            "±": "+",  # Simplificação para evitar crash (ou poderia ser lista)
            "‰": "/1000.0",

            # --- Comparação ---
            "≠": "!=", 
            "≤": "<=", 
            "≥": ">=",
            "≈": "==", # Aproximado vira igualdade simbólica
            "≡": "==", # Identidade vira igualdade
            
            # --- Constantes ---
            "π": "pi", 
            "∞": "oo", 
            "i": "I", 
            "e": "E",
            "°": "*pi/180", # Converte graus para radianos
            "ħ": "hbar",
            "Å": "Angstrom",

            # --- Cálculo e Funções ---
            "√": "sqrt", 
            "∛": "cbrt", 
            "∫": "integrate", 
            "∬": "integrate", # SymPy usa o mesmo comando, exige mais argumentos
            "∂": "diff", 
            "∇": "diff",
            "∑": "Sum", 
            "∏": "Product", 
            "lim": "limit",
            "∠": "angle",
            
            # --- Lógica e Conjuntos ---
            "⇒": ">>",  # Implicação SymPy
            "→": ">>",
            "⇔": "==", # Bi-implicação
            "∈": " in ", 
            "∉": " not in ",
            "∪": "|",  # União
            "∩": "&",  # Interseção
            "⊂": ".is_subset(", # Requer sintaxe orientada a objeto, mas ajuda
            "⊃": ".is_superset(",
            "∅": "S.EmptySet",
            
            # --- Símbolos Semânticos (Trata como variáveis/funções vazias) ---
            "∀": "ForAll",
            "∃": "Exists",
            "∴": "Therefore",
            "†": "dagger",
            "‡": "ddagger",

            # --- Alfabeto Grego (Mapeia para nomes em inglês) ---
            "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", 
            "ε": "epsilon", "ζ": "zeta", "η": "eta", "θ": "theta",
            "ι": "iota", "κ": "kappa", "λ": "lamda", "μ": "mu", 
            "ν": "nu", "ξ": "xi", "ρ": "rho", "σ": "sigma", 
            "τ": "tau", "υ": "upsilon", "φ": "phi", "χ": "chi", 
            "ψ": "psi", "ω": "omega",
            
            # Grego Maiúsculo
            "Δ": "Delta", "Γ": "Gamma", "Θ": "Theta", "Λ": "Lambda", 
            "Ξ": "Xi", "Π": "Pi", "Σ": "Sigma", "Φ": "Phi", 
            "Ψ": "Psi", "Ω": "Omega"
        }
        
        # Faz a troca de todos
        for char, code in replacements.items():
            if char in expr_str:
                expr_str = expr_str.replace(char, code)
            
        return expr_str

    def process_home(self):
        expr_str = self.entry_home.get().strip()
        if not expr_str:
            return

        # USANDO O SANITIZADOR AQUI
        expr_clean = self._sanitize_input(expr_str)

        env = {
            **math.__dict__, 
            "np": np, 
            "Ans": self.home_last_result,
            "cbrt": lambda n: n**(1/3),
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
             # Adiciona suporte básico para conjuntos
            "set": set,
        }
        
        try:
            val = eval(expr_clean, {"__builtins__": {}}, env)
            self.home_last_result = float(val)
            self._home_log(expr_str, self.home_last_result)
            self.entry_home.delete(0, tk.END)
        except Exception as e:
            # Mostra o erro amigável sem crashar
            self._home_log(expr_str, f"Erro: {e}")

    def _create_cas_app(self):
        self.tab_cas = tk.Frame(self.notebook, bg="#e0e0e0")
        self.notebook.add(self.tab_cas, text=" Álgebra ")

        self.idx_cas = self.notebook.index(self.tab_cas)

        self.cas_history = tk.Text(
            self.tab_cas,
            height=10,
            font=('Consolas', 11),
            state='disabled',
            bg="#f7f7f7"
        )
        self.cas_history.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.entry_cas = tk.Entry(self.tab_cas, font=('Arial', 14), bd=2, relief="sunken")
        self.entry_cas.pack(padx=5, pady=5, fill=tk.X)
        self.entry_cas.bind("<Return>", lambda e: self.process_cas())

    def _cas_log(self, expr, result):
        self.cas_history.config(state='normal')
        self.cas_history.insert(tk.END, f"> {expr}\n")
        self.cas_history.insert(tk.END, f"= {result}\n\n")
        self.cas_history.see(tk.END)
        self.cas_history.config(state='disabled')

    def process_cas(self):
        expr_str = self.entry_cas.get().strip()
        if not expr_str:
            return

        local_dict = {
            'x': x, 'y': y, 'z': z, 't': t,
            'Ans': self.cas_last_result,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            'sqrt': sp.sqrt, 'log': sp.log, 'ln': sp.log, 'exp': sp.exp,
            'pi': sp.pi, 'E': sp.E, 'I': sp.I,
            'diff': sp.diff, 'integrate': sp.integrate, 'solve': sp.solve,
            'Sum': sp.Sum, 'factor': sp.factor, 'expand': sp.expand,
            'cbrt': lambda n: sp.Pow(n, sp.Rational(1, 3)), # Define raiz cubica
            'approx': lambda v: sp.N(v),
            'cbrt': lambda n: sp.Pow(n, sp.Rational(1, 3)),
                'Sum': sp.Sum,
                'Product': sp.Product,
                'limit': sp.limit,
                'oo': sp.oo,
                'I': sp.I,
                'E': sp.E,
                'S': sp.S,
        }
        local_dict.update(self.program_env)

        try:
            # USANDO O SANITIZADOR AQUI
            expr_clean = self._sanitize_input(expr_str)
            
            expr = sp.sympify(expr_clean, locals=local_dict)

            if isinstance(expr, sp.Equality):
                result = sp.solve(expr, x)
            else:
                if hasattr(expr, 'free_symbols') and len(expr.free_symbols) == 0:
                    result = expr.evalf()
                else:
                    result = sp.simplify(expr)

            self.cas_last_result = result
            self._cas_log(expr_str, str(result))
            self.entry_cas.delete(0, tk.END)
        except Exception as e:
            self._cas_log(expr_str, f"Erro: {e}")

    def _create_plot2d_app(self):
        self.tab_plot2d = tk.Frame(self.notebook, bg="#e0e0e0")
        self.notebook.add(self.tab_plot2d, text=" Gráfico 2D ")

        self.idx_plot2d = self.notebook.index(self.tab_plot2d)

        toolbar = tk.Frame(self.tab_plot2d, bg="#d0d0d0")
        toolbar.pack(fill=tk.X)

        self.graph_view_mode = tk.StringVar(value="Plot")

        for mode in ["Simb", "Plot", "Num", "Vista"]:
            b = tk.Radiobutton(
                toolbar,
                text=mode,
                variable=self.graph_view_mode,
                value=mode,
                indicatoron=False,
                command=self.graph2d_update_view,
                width=8,
                bg="#c0c0c0",
                fg="black",
                relief="raised"
            )
            b.pack(side=tk.LEFT, padx=2, pady=2)

        self.graph2d_symb_frame = tk.Frame(self.tab_plot2d, bg="#e0e0e0")
        self.graph2d_plot_frame = tk.Frame(self.tab_plot2d, bg="#e0e0e0")
        self.graph2d_num_frame = tk.Frame(self.tab_plot2d, bg="#e0e0e0")
        self.graph2d_view_frame = tk.Frame(self.tab_plot2d, bg="#e0e0e0")

        for f in [
            self.graph2d_symb_frame,
            self.graph2d_plot_frame,
            self.graph2d_num_frame,
            self.graph2d_view_frame,
        ]:
            f.pack(fill=tk.BOTH, expand=True)

        symb_top = tk.Frame(self.graph2d_symb_frame, bg="#e0e0e0")
        symb_top.pack(fill=tk.X, pady=5)

        tk.Label(symb_top, text="f(x) =", font=('Arial', 12, 'bold'), bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
        self.entry_plot = tk.Entry(symb_top, font=('Arial', 12))
        self.entry_plot.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_plot.insert(0, "sin(x)*x")

        tk.Button(
            symb_top,
            text="Plotar",
            command=self.update_graph2d,
            bg="#4a6fa5",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        symb_eval = tk.Frame(self.graph2d_symb_frame, bg="#e0e0e0")
        symb_eval.pack(fill=tk.X, pady=5)

        tk.Label(symb_eval, text="x₀ =", bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
        self.entry_x0 = tk.Entry(symb_eval, font=('Arial', 10), width=10)
        self.entry_x0.pack(side=tk.LEFT)
        self.entry_x0.insert(0, "0")
        self.label_fx0 = tk.Label(symb_eval, text="f(x₀) = ?", bg="#e0e0e0")
        self.label_fx0.pack(side=tk.LEFT, padx=10)

        tk.Button(
            symb_eval,
            text="Avaliar",
            command=self.evaluate_at_point,
            bg="#5cb85c",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        self.figure2d = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax2d = self.figure2d.add_subplot(111)
        self.ax2d.grid(True, linestyle='--')
        self.ax2d.axhline(0, color='black', linewidth=1)
        self.ax2d.axvline(0, color='black', linewidth=1)

        self.canvas2d = FigureCanvasTkAgg(self.figure2d, self.graph2d_plot_frame)
        self.canvas2d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.graph2d_table = tk.Text(self.graph2d_num_frame, font=("Consolas", 10))
        self.graph2d_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        view_inner = tk.Frame(self.graph2d_view_frame, bg="#e0e0e0")
        view_inner.pack(pady=10)

        tk.Label(view_inner, text="x_min:", bg="#e0e0e0").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        tk.Label(view_inner, text="x_max:", bg="#e0e0e0").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        tk.Label(view_inner, text="Pontos:", bg="#e0e0e0").grid(row=2, column=0, padx=5, pady=2, sticky="e")

        self.var_xmin2d = tk.Entry(view_inner, width=8)
        self.var_xmax2d = tk.Entry(view_inner, width=8)
        self.var_npts2d = tk.Entry(view_inner, width=8)

        self.var_xmin2d.insert(0, "-10")
        self.var_xmax2d.insert(0, "10")
        self.var_npts2d.insert(0, "500")

        self.var_xmin2d.grid(row=0, column=1, padx=5, pady=2)
        self.var_xmax2d.grid(row=1, column=1, padx=5, pady=2)
        self.var_npts2d.grid(row=2, column=1, padx=5, pady=2)

        tk.Button(
            view_inner,
            text="Aplicar & Plotar",
            command=self.update_graph2d,
            bg="#4a6fa5",
            fg="white"
        ).grid(row=3, column=0, columnspan=2, pady=10)

        self.graph2d_last_x = None
        self.graph2d_last_y = None

        self.graph2d_update_view()

    def graph2d_update_view(self):
        mode = self.graph_view_mode.get()

        for f in [
            self.graph2d_symb_frame,
            self.graph2d_plot_frame,
            self.graph2d_num_frame,
            self.graph2d_view_frame,
        ]:
            f.pack_forget()

        if mode == "Simb":
            self.graph2d_symb_frame.pack(fill=tk.BOTH, expand=True)
        elif mode == "Plot":
            self.graph2d_plot_frame.pack(fill=tk.BOTH, expand=True)
        elif mode == "Num":
            self.graph2d_num_frame.pack(fill=tk.BOTH, expand=True)
        elif mode == "Vista":
            self.graph2d_view_frame.pack(fill=tk.BOTH, expand=True)

    def _build_numeric_function(self, expr_str):
        # USANDO O SANITIZADOR AQUI
        expr_str = self._sanitize_input(expr_str)
        
        local_dict = {
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'sqrt': sp.sqrt, 'log': sp.log, 'ln': sp.log, 'exp': sp.exp,
            'pi': sp.pi, 'E': sp.E,
            'cbrt': lambda n: n**(1/3)
        }
        local_dict.update(self.program_env)

        f_sym = sp.sympify(expr_str, locals=local_dict)
        f_num = sp.lambdify(x, f_sym, modules=['numpy'])
        return f_num

    def update_graph2d(self):
        expr_str = self.entry_plot.get().strip()
        if not expr_str:
            return
        try:
            xmin = float(self.var_xmin2d.get())
            xmax = float(self.var_xmax2d.get())
            npts = int(self.var_npts2d.get())
        except Exception:
            xmin, xmax, npts = -10, 10, 500

        try:
            f_num = self._build_numeric_function(expr_str)
            x_vals = np.linspace(xmin, xmax, npts)
            y_vals = f_num(x_vals)

            self.graph2d_last_x = x_vals
            self.graph2d_last_y = y_vals

            self.ax2d.clear()
            self.ax2d.grid(True, linestyle='--')
            self.ax2d.axhline(0, color='black', linewidth=1)
            self.ax2d.axvline(0, color='black', linewidth=1)
            self.ax2d.plot(x_vals, y_vals, label=f"f(x)={expr_str}", color='blue')
            self.ax2d.legend()
            self.canvas2d.draw()

            self.graph2d_table.delete(1.0, tk.END)
            self.graph2d_table.insert(tk.END, "   x\t\tf(x)\n")
            self.graph2d_table.insert(tk.END, "-" * 30 + "\n")
            for xi, yi in zip(x_vals[::max(1, len(x_vals)//40)], y_vals[::max(1, len(y_vals)//40)]):
                self.graph2d_table.insert(tk.END, f"{xi: .4f}\t{yi: .4f}\n")

            self.graph_view_mode.set("Plot")
            self.graph2d_update_view()

        except Exception as e:
            messagebox.showerror("Erro Gráfico 2D", str(e))

    def evaluate_at_point(self):
        expr_str = self.entry_plot.get().strip()
        x0_str = self.entry_x0.get().strip()
        if not expr_str or not x0_str:
            return
        try:
            f_num = self._build_numeric_function(expr_str)
            x0 = float(x0_str)
            y0 = f_num(x0)
            self.label_fx0.config(text=f"f(x₀) = {y0:.6g}")
        except Exception as e:
            messagebox.showerror("Erro Avaliação", str(e))

    def _create_plot3d_app(self):
        self.tab_plot3d = tk.Frame(self.notebook, bg="#e0e0e0")
        self.notebook.add(self.tab_plot3d, text=" Gráfico 3D ")

        self.idx_plot3d = self.notebook.index(self.tab_plot3d)

        top = tk.Frame(self.tab_plot3d, bg="#e0e0e0")
        top.pack(fill=tk.X, pady=5)

        tk.Label(top, text="z(x,y) =", font=('Arial', 12, 'bold'), bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
        self.entry_plot3d = tk.Entry(top, font=('Arial', 12))
        self.entry_plot3d.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_plot3d.insert(0, "sin(sqrt(x**2 + y**2))")

        tk.Button(
            top,
            text="Plotar 3D",
            command=self.update_graph3d,
            bg="#4a6fa5",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        ranges = tk.Frame(self.tab_plot3d, bg="#e0e0e0")
        ranges.pack(fill=tk.X, pady=5)

        tk.Label(ranges, text="x_min:", bg="#e0e0e0").grid(row=0, column=0, padx=3, pady=2, sticky="e")
        tk.Label(ranges, text="x_max:", bg="#e0e0e0").grid(row=0, column=2, padx=3, pady=2, sticky="e")
        tk.Label(ranges, text="y_min:", bg="#e0e0e0").grid(row=1, column=0, padx=3, pady=2, sticky="e")
        tk.Label(ranges, text="y_max:", bg="#e0e0e0").grid(row=1, column=2, padx=3, pady=2, sticky="e")

        self.entry_xmin3d = tk.Entry(ranges, width=8)
        self.entry_xmax3d = tk.Entry(ranges, width=8)
        self.entry_ymin3d = tk.Entry(ranges, width=8)
        self.entry_ymax3d = tk.Entry(ranges, width=8)

        self.entry_xmin3d.insert(0, "-5")
        self.entry_xmax3d.insert(0, "5")
        self.entry_ymin3d.insert(0, "-5")
        self.entry_ymax3d.insert(0, "5")

        self.entry_xmin3d.grid(row=0, column=1)
        self.entry_xmax3d.grid(row=0, column=3)
        self.entry_ymin3d.grid(row=1, column=1)
        self.entry_ymax3d.grid(row=1, column=3)

        self.figure3d = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax3d = self.figure3d.add_subplot(111, projection='3d')
        self.canvas3d = FigureCanvasTkAgg(self.figure3d, self.tab_plot3d)
        self.canvas3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_graph3d(self):
        expr_str = self.entry_plot3d.get().strip()
        if not expr_str:
            return

        local_dict = {
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'sqrt': sp.sqrt,
            'log': sp.log,
            'ln': sp.log,
            'exp': sp.exp,
            'pi': sp.pi,
            'E': sp.E,
        }
        local_dict.update(self.program_env)

        try:
            f_sym = sp.sympify(expr_str, locals=local_dict)
            f_num = sp.lambdify((x, y), f_sym, modules=['numpy'])

            xmin = float(self.entry_xmin3d.get())
            xmax = float(self.entry_xmax3d.get())
            ymin = float(self.entry_ymin3d.get())
            ymax = float(self.entry_ymax3d.get())

            X = np.linspace(xmin, xmax, 40)
            Y = np.linspace(ymin, ymax, 40)
            X, Y = np.meshgrid(X, Y)
            Z = f_num(X, Y)

            self.ax3d.clear()
            surf = self.ax3d.plot_surface(X, Y, Z, cmap=cm.viridis, linewidth=0, antialiased=True)
            self.ax3d.set_xlabel("x")
            self.ax3d.set_ylabel("y")
            self.ax3d.set_zlabel("z")
            self.figure3d.colorbar(surf, ax=self.ax3d, shrink=0.5, aspect=10)
            self.canvas3d.draw()
        except Exception as e:
            messagebox.showerror("Erro Gráfico 3D", str(e))

    def _create_stats_app(self):
        self.tab_stats = tk.Frame(self.notebook, bg="#e0e0e0")
        self.notebook.add(self.tab_stats, text=" Estatística ")

        self.idx_stats = self.notebook.index(self.tab_stats)

        tk.Label(self.tab_stats, text="Lista X (separar por vírgula):", bg="#e0e0e0").pack(anchor="w", padx=10)
        self.entry_stat_x = tk.Entry(self.tab_stats)
        self.entry_stat_x.pack(fill=tk.X, padx=10)
        self.entry_stat_x.insert(0, "1, 2, 3, 4, 5")

        tk.Label(self.tab_stats, text="Lista Y (opcional):", bg="#e0e0e0").pack(anchor="w", padx=10)
        self.entry_stat_y = tk.Entry(self.tab_stats)
        self.entry_stat_y.pack(fill=tk.X, padx=10)
        self.entry_stat_y.insert(0, "2, 4, 5, 4, 5")

        btn_calc = tk.Button(
            self.tab_stats,
            text="Calcular Estatísticas",
            command=self.calc_stats,
            bg="#f0ad4e"
        )
        btn_calc.pack(pady=5)

        self.stats_result = tk.Text(self.tab_stats, height=10)
        self.stats_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def calc_stats(self):
        try:
            x_data = [float(i) for i in self.entry_stat_x.get().split(',') if i.strip()]
            y_str = self.entry_stat_y.get()
            y_data = [float(i) for i in y_str.split(',') if i.strip()] if y_str.strip() else []

            df = pd.DataFrame({'X': x_data})
            res = "--- Estatística 1-Var (X) ---\n"
            res += str(df['X'].describe()) + "\n\n"

            if y_data and len(x_data) == len(y_data):
                df['Y'] = y_data
                res += "--- Estatística 2-Var ---\n"
                res += f"Correlação (r): {df['X'].corr(df['Y']):.4f}\n"
                fit = np.polyfit(x_data, y_data, 1)
                res += f"Regressão: y = {fit[0]:.2f}x + {fit[1]:.2f}\n"

            self.stats_result.delete(1.0, tk.END)
            self.stats_result.insert(tk.END, res)
        except Exception as e:
            messagebox.showerror("Erro Estatístico", str(e))

    def _create_spreadsheet_app(self):
        self.tab_sheet = tk.Frame(self.notebook, bg="#e0e0e0")
        self.notebook.add(self.tab_sheet, text=" Planilha ")

        self.idx_sheet = self.notebook.index(self.tab_sheet)

        self.cells = {}
        for r in range(5):
            for c in range(5):
                e = tk.Entry(self.tab_sheet, width=10)
                e.grid(row=r, column=c, padx=1, pady=1)
                self.cells[(r, c)] = e

        tk.Button(
            self.tab_sheet,
            text="Recalcular (Python Eval)",
            command=self.recalc_sheet,
            bg="#5cb85c",
            fg="white"
        ).grid(row=6, column=0, columnspan=5, sticky="we")
        tk.Label(
            self.tab_sheet,
            text="Dica: Use sintaxe Python. Ex: =5*10",
            bg="#e0e0e0"
        ).grid(row=7, column=0, columnspan=5)

    def recalc_sheet(self):
        for pos, widget in self.cells.items():
            val = widget.get()
            if val.startswith("="):
                try:
                    res = eval(val[1:], {"__builtins__": {}}, {})
                    widget.delete(0, tk.END)
                    widget.insert(0, str(res))
                except Exception:
                    pass

    def _create_programs_app(self):
        self.tab_prog = tk.Frame(self.notebook, bg="#e0e0e0")
        self.notebook.add(self.tab_prog, text=" Programação ")

        self.idx_prog = self.notebook.index(self.tab_prog)

        tk.Label(
            self.tab_prog,
            text="Editor de Programas (Python demo)\nDefina funções como f(x) e use no CAS/Graph.",
            bg="#e0e0e0"
        ).pack(pady=5)

        self.program_editor = tk.Text(self.tab_prog, height=12, font=("Consolas", 10))
        self.program_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        default_prog = (
            "# Exemplo:\n"
            "import math\n\n"
            "def f(x):\n"
            "    return x**2 + 1\n\n"
            "def g(x):\n"
            "    return math.sin(x) + 2\n"
        )
        self.program_editor.insert(tk.END, default_prog)

        tk.Button(
            self.tab_prog,
            text="Compilar / Atualizar Funções",
            command=self.run_programs,
            bg="#4a6fa5",
            fg="white"
        ).pack(pady=5)

        self.program_output = tk.Text(self.tab_prog, height=5, font=("Consolas", 9))
        self.program_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def run_programs(self):
        code = self.program_editor.get("1.0", tk.END)
        env = {
            "np": np,
            "sp": sp,
            "x": x,
            "y": y,
            "z": z,
            "t": t,
            "math": math,
        }
        try:
            exec(code, {"__builtins__": {}}, env)
            self.program_env = env  

            self.program_output.delete(1.0, tk.END)
            self.program_output.insert(tk.END, "Compilado com sucesso.\nFunções disponíveis:\n")
            names = [k for k in env.keys() if not k.startswith("__")]
            for n in names:
                self.program_output.insert(tk.END, f" - {n}\n")
        except Exception as e:
            self.program_output.delete(1.0, tk.END)
            self.program_output.insert(tk.END, f"Erro ao compilar:\n{e}")

    def _create_keypad(self):
        main_pad = tk.Frame(self.main_pane, bg=self.colors["bg_window"])
        self.main_pane.add(main_pad, stretch="always")

        main_pad.columnconfigure(0, weight=1)
        main_pad.rowconfigure(0, weight=2) 
        main_pad.rowconfigure(1, weight=3)
        main_pad.rowconfigure(2, weight=4)

        nav_frame = tk.Frame(main_pad, bg=self.colors["bg_window"])
        nav_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        for i in range(5): nav_frame.columnconfigure(i, weight=1)
        for i in range(3): nav_frame.rowconfigure(i, weight=1)

        self._make_btn(nav_frame, "Apps", 0, 0, "dark")
        self._make_btn(nav_frame, "Symb", 0, 1, "dark")
        self._make_btn(nav_frame, "Home", 2, 0, "dark")
        self._make_btn(nav_frame, "Plot", 1, 1, "dark")
        self._make_btn(nav_frame, "Num",  2, 1, "dark")

        dpad_frame = tk.Frame(nav_frame, bg=self.colors["bg_window"])
        dpad_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")
        for i in range(3): dpad_frame.columnconfigure(i, weight=1)
        for i in range(3): dpad_frame.rowconfigure(i, weight=1)
        
        self._make_btn(dpad_frame, "▲", 0, 1, "dark")
        self._make_btn(dpad_frame, "◄", 1, 0, "dark")
        self._make_btn(dpad_frame, "►", 1, 2, "dark")
        self._make_btn(dpad_frame, "▼", 2, 1, "dark")

        self._make_btn(nav_frame, "Help", 0, 3, "dark")
        self._make_btn(nav_frame, "Esc",  0, 4, "dark")
        self._make_btn(nav_frame, "View", 1, 3, "dark")
        self._make_btn(nav_frame, "CAS",  2, 4, "dark")
        self._make_btn(nav_frame, "Menu", 2, 3, "dark")

        sci_frame = tk.Frame(main_pad, bg=self.colors["bg_window"])
        sci_frame.grid(row=1, column=0, sticky="nsew", padx=2)

        for i in range(6): sci_frame.columnconfigure(i, weight=1)
        for i in range(3): sci_frame.rowconfigure(i, weight=1)

        row1 = ["Vars", "🧰", "믐, √◻, |◻|", "x t θ n", "aᵇ/ᶜ", "⌫"]
        row2 = ["xʸ", "sin", "cos", "tan", "ln", "log"]
        
        for c, key in enumerate(row1): self._make_btn(sci_frame, key, 0, c, "func")
        for c, key in enumerate(row2): self._make_btn(sci_frame, key, 1, c, "func")

        self._make_btn(sci_frame, "x²", 2, 0, "func")
        self._make_btn(sci_frame, "±",  2, 1, "func")
        self._make_btn(sci_frame, "( )", 2, 2, "func") 
        self._make_btn(sci_frame, ",",  2, 3, "func")
        
        btn_ent = tk.Button(
            sci_frame, text="Enter", 
            bg=self.colors["key_func"], fg="black", font=self.f_btn_bold,
            relief="raised", bd=1,
            command=lambda: self.btn_press("Enter")
        )
        btn_ent.grid(row=2, column=4, columnspan=2, padx=1, pady=1, sticky="nsew")
        self.btn_cache["Enter"] = btn_ent

        num_frame = tk.Frame(main_pad, bg=self.colors["bg_window"])
        num_frame.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)

        for i in range(5): num_frame.columnconfigure(i, weight=1)
        for i in range(4): num_frame.rowconfigure(i, weight=1)

        num_keys = [
            ["EEX", "7", "8", "9", "÷"],
            ["Alpha", "4", "5", "6", "*"],
            ["Shift", "1", "2", "3", "-"],
            ["On", "0", ".", "⊔", "+"]
        ]

        for r, row in enumerate(num_keys):
            for c, key in enumerate(row):
                color = "num"
                if key == "Alpha": color = "orange"
                elif key == "Shift": color = "blue"
                elif key in ["/", "*", "-", "+", "=", "EEX"]: color = "num"
                
                self._make_btn(num_frame, key, r, c, color)

    def _make_btn(self, parent, text, r, c, style, label=None):
        bg = self.colors["key_func"]
        fg = "black"
        font_obj = self.f_btn_norm 
        
        if style == "dark":
            bg = self.colors["key_dark"]; fg = "white"; font_obj = self.f_btn_small
        elif style == "num":
            bg = self.colors["key_num"]; font_obj = self.f_btn_bold
        elif style == "enter":
            bg = self.colors["key_num"]; font_obj = self.f_btn_bold
        elif style == "orange":
            bg = self.colors["key_orange"]; fg = "white"; font_obj = self.f_btn_bold
        elif style == "blue":
            bg = self.colors["key_blue"]; fg = "white"; font_obj = self.f_btn_bold

        display_text = label if label else text
        
        b = tk.Button(
            parent, text=display_text, 
            bg=bg, fg=fg, font=font_obj,
            relief="raised", bd=1,
            command=lambda k=text: self.btn_press(k)
        )
        b.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
        
        self.btn_cache[text] = b

    def _on_resize(self, event):
        if event.widget == self.root:
            new_size_norm = max(8, int(event.height / 65)) 
            new_size_small = max(7, int(event.height / 75))

            self.f_btn_norm.configure(size=new_size_norm)
            self.f_btn_bold.configure(size=new_size_norm) 
            self.f_btn_small.configure(size=new_size_small)
    
    # -------------------------------------------------------------------------
    # PATCH: Menu CHARS com SCROLLBAR e ÍCONES GRANDES (Estilo Catálogo)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # PATCH: Menu CHARS (Posição SUPERIOR - Libera o campo de digitação embaixo)
    # -------------------------------------------------------------------------
    def cmd_chars(self):
        """Abre o catálogo de caracteres no TOPO, deixando a digitação (fundo) livre."""
        
        # 1. Toggle (Se já aberto, fecha)
        if getattr(self, "chars_overlay", None) is not None and self.chars_overlay.winfo_exists():
            self.chars_overlay.destroy()
            return

        # 2. Captura o alvo
        target_widget = self.root.focus_get()
        valid_types = (tk.Entry, tk.Text, ttk.Entry)
        
        if not isinstance(target_widget, valid_types):
            current = self.notebook.index(self.notebook.select())
            if current == self.idx_home: target_widget = self.entry_home
            elif current == self.idx_cas: target_widget = self.entry_cas
            elif current == self.idx_plot2d: target_widget = self.entry_plot
            elif current == self.idx_plot3d: target_widget = self.entry_plot3d
            elif current == self.idx_sheet: 
                 if hasattr(self, 'cells'): target_widget = self.cells.get((0,0))
            elif current == self.idx_prog: target_widget = self.program_editor

        # 3. Cria o Frame no TOPO (rely=0)
        # Ocupa 55% da altura superior, deixando os 45% inferiores livres para você ver o Entry
        self.chars_overlay = tk.Frame(self.notebook, bg="#E1E1E1", bd=2, relief="raised")
        self.chars_overlay.place(relx=0, rely=0, relwidth=1, relheight=0.87)

        # --- Header ---
        header = tk.Frame(self.chars_overlay, bg=self.colors["topbar"], height=30)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="Catálogo de Símbolos", bg=self.colors["topbar"], fg="white",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        
        # Botão Fechar
        close_btn = tk.Label(header, text="✕", bg=self.colors["topbar"], fg="white", 
                             font=("Arial", 12, "bold"), cursor="hand2")
        close_btn.pack(side="right", padx=10)
        close_btn.bind("<Button-1>", lambda e: self.chars_overlay.destroy())

        # --- Canvas com Scrollbar ---
        scroll_container = tk.Frame(self.chars_overlay, bg="#E1E1E1")
        scroll_container.pack(fill="both", expand=True, padx=2, pady=2)

        canvas = tk.Canvas(scroll_container, bg="#E1E1E1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg="#E1E1E1")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll com Mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.chars_overlay.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- Lista de Caracteres ---
        all_chars = [
            'π', 'e', 'i', '∞', '°', '∠', '√', '∛', 
            '≠', '≤', '≥', '±', '≈', '≡', '×', '÷',
            '∫', '∬', '∂', '∇', '∑', '∏', 'lim', 'd',
            '→', '⇒', '⇔', '∈', '∉', '⊂', '⊃', '∪', '∩', '∅', '∀', '∃', '∴',
            'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 
            'λ', 'μ', 'ν', 'ξ', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ψ', 'ω',
            'Δ', 'Γ', 'Θ', 'Λ', 'Ξ', 'Π', 'Σ', 'Φ', 'Ψ', 'Ω',
            'ħ', '†', '‡', '‰', 'Å'
        ]

        COLUMNS = 6 
        for i in range(COLUMNS):
            scrollable_frame.columnconfigure(i, weight=1)

        for index, char in enumerate(all_chars):
            r, c = divmod(index, COLUMNS)
            
            btn = tk.Button(
                scrollable_frame,
                text=char,
                font=("Segoe UI", 14),
                bg="white",
                fg="#222",
                relief="raised",
                bd=1,
                activebackground=self.colors["topbar"],
                activeforeground="white",
                command=lambda ch=char, tw=target_widget: self._insert_char_overlay(ch, tw)
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2, ipady=5)

    def _insert_char_overlay(self, char, target_widget):
        if target_widget:
            try:
                if isinstance(target_widget, (tk.Entry, ttk.Entry)):
                    target_widget.insert(tk.INSERT, char)
                    target_widget.xview_moveto(1)
                elif isinstance(target_widget, tk.Text):
                    target_widget.insert(tk.INSERT, char)
                    target_widget.see(tk.INSERT)
            except Exception:
                pass
            
    def _toggle_apps_menu(self):
        """Abre o menu de Apps com rolagem e ícones grandes"""
        
        if hasattr(self, 'apps_overlay') and self.apps_overlay.winfo_exists():
            self.apps_overlay.destroy()
            return

        self.apps_overlay = tk.Frame(self.notebook, bg="#F4F4F4")
        self.apps_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        header = tk.Frame(self.apps_overlay, bg="#0099CC", height=35)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="Biblioteca de Aplicações", bg="#0099CC", fg="white", 
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        
        close_btn = tk.Label(header, text="✕", bg="#0099CC", fg="white", font=("Arial", 11), cursor="hand2")
        close_btn.pack(side="right", padx=10)
        close_btn.bind("<Button-1>", lambda e: self.apps_overlay.destroy())

        container_scroll = tk.Frame(self.apps_overlay, bg="#F4F4F4")
        container_scroll.pack(fill="both", expand=True)

        canvas = tk.Canvas(container_scroll, bg="#F4F4F4", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_scroll, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg="#F4F4F4")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_frame_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.apps_overlay.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        colunas = 2
        for i in range(colunas): 
            scrollable_frame.columnconfigure(i, weight=1)

        apps_list = [
            ("Função",      "𝑓(𝑥)",   "#FD9800", self.idx_plot2d),
            ("Avançado",    "𝑥 < 𝑦",  "#E65100", self.idx_plot2d),
            ("Geometria",   "△○□",    "#4CAF50", self.idx_plot2d),
            ("Planilha",    "📅",     "#2196F3", self.idx_sheet),
            ("Estat. 1Var", "𝑥̄",      "#9C27B0", self.idx_stats),
            ("Estat. 2Var", "𝑥𝑦",     "#673AB7", self.idx_stats),
            ("Inferência",  "𝐻₀",     "#F44336", self.idx_stats),
            ("Solucionador","𝑋=0",    "#FFC107", self.idx_cas),
            ("Finanças",    "💲",     "#1B5E20", self.idx_home),
            ("Linear",      "𝐴𝑥=𝑏",   "#3F51B5", self.idx_home),
            ("Triângulos",  "📐",     "#FF5722", self.idx_home),
            ("Paramétrico", "𝑋(𝑡)",   "#FF9800", self.idx_plot2d),
            ("Polar",       "𝑟=𝜃",    "#FF9800", self.idx_plot2d),
            ("Sequência",   "𝑈(𝑛)",   "#FF9800", self.idx_home),
            ("Python",      "🐍",     "#FFEB3B", self.idx_prog),
            ("Arquivos",    "📁",     "#607D8B", self.idx_prog)
        ]

        for i, (name, icon_txt, color, target_idx) in enumerate(apps_list):
            r, c = divmod(i, colunas)
            
            f_container = tk.Frame(scrollable_frame, bg="#F4F4F4")
            f_container.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
            
            btn_frame = tk.Frame(f_container, bg="white", bd=2, relief="raised", height=100)
            btn_frame.pack(fill="both", expand=True)
            btn_frame.pack_propagate(False) 

            lbl_icon = tk.Label(btn_frame, text=icon_txt, font=("Segoe UI", 24, "bold"),
                                fg=color, bg="white")
            lbl_icon.pack(side="top", expand=True, fill="both", pady=(10, 0))
            
            lbl_name = tk.Label(btn_frame, text=name, font=("Segoe UI", 10, "bold"), 
                                bg="white", fg="#404040")
            lbl_name.pack(side="bottom", pady=(0, 10))

            def open_app(idx=target_idx):
                self.apps_overlay.destroy()
                
                if self.exam_mode and idx in [self.idx_cas, self.idx_prog]:
                    messagebox.showwarning("Modo Prova", "Aplicação bloqueada durante o exame!")
                    return

                self.notebook.select(idx)
                if idx == self.idx_home: self.entry_home.focus_set()
                elif idx == self.idx_cas: self.entry_cas.focus_set()

            for w in (btn_frame, lbl_icon, lbl_name):
                w.bind("<Button-1>", lambda e, cb=open_app: cb())
                w.bind("<Enter>", lambda e, f=btn_frame: f.config(bg="#E8F0FE", relief="solid")) 
                w.bind("<Leave>", lambda e, f=btn_frame: f.config(bg="white", relief="raised"))

    def btn_press(self, key):
        # Se a janela de matrizes está aberta, Esc/On fecha ela primeiro
        if getattr(self, "matrix_win", None) is not None and self.matrix_win.winfo_exists():
            if key in ("Esc", "On"):
                self._close_matrix_win()
                return
        
        if getattr(self, "chars_overlay", None) is not None and self.chars_overlay.winfo_exists():
            if key in ("Esc", "On"):
                self.chars_overlay.destroy()
                return

        # --- Modificadores ---
        if key == 'Shift':
            self.shift_mode = not self.shift_mode
            self.alpha_mode = False
            self._update_keys()
            return

        if key == 'Alpha':
            self.alpha_mode = not self.alpha_mode
            self.shift_mode = False
            self._update_keys()
            return

        # --- Determina Tecla Efetiva ---
        effective_key = key

        if self.shift_mode and key in self.KEY_MAP:
            effective_key = self.KEY_MAP[key][0]
            self.shift_mode = False
            self._update_keys()
        elif self.alpha_mode and key in self.KEY_MAP:
            effective_key = self.KEY_MAP[key][1]
            self.alpha_mode = False
            self._update_keys()

        # --- Comandos de Sistema ---
        if key == 'Apps':
            self._toggle_apps_menu()
            return
        if key == 'Home':
            self.notebook.select(self.idx_home)
            self.entry_home.focus_set()
            return

        # Navegação de Abas
        if key == 'CAS': 
            if not self.exam_mode: self.notebook.select(self.idx_cas); self.entry_cas.focus_set()
            return
        if key == 'Plot': self.notebook.select(self.idx_plot2d); return
        if key == 'Symb': 
            if not self.exam_mode: self.notebook.select(self.idx_cas)
            return
        if key == 'Num': self.notebook.select(self.idx_stats); return
        
        # Foco
        focus = self.root.focus_get()
        if not isinstance(focus, (tk.Entry, tk.Text)):
            current = self.notebook.index(self.notebook.select())
            if current == self.idx_home: focus = self.entry_home
            elif current == self.idx_cas: focus = self.entry_cas
            if focus: focus.focus_set()

        # Edição
        if key == 'Esc':
            if effective_key == 'Clear':
                if isinstance(focus, tk.Entry): focus.delete(0, tk.END)
            else:
                if isinstance(focus, tk.Entry): focus.delete(0, tk.END)
            return
    
        # CORREÇÃO 2: Verifica effective_key (o resultado do Shift) e não a tecla física
        if effective_key == "Matrix":
            self._open_matrices_app()
            return

        if effective_key == "Chars":
            self.cmd_chars()
            return

        if key == "Help":
            pass
        
        if key == 'Del':
            if isinstance(focus, tk.Entry):
                try:
                    idx = focus.index(tk.INSERT)
                    if idx > 0: focus.delete(idx-1, idx)
                except: pass
            return

        if effective_key == 'Off':
                self.root.destroy()
                return

        if key == 'On':
            self._clear_screen()
            return

        # Enter vs Approx
        if (key in ['Enter', '=']) and (effective_key != '≈'):
            current = self.notebook.index(self.notebook.select())
            if current == self.idx_home: self.process_home()
            elif current == self.idx_cas: self.process_cas()
            elif isinstance(focus, tk.Entry): focus.event_generate("<Return>")
            return
        
        # Copy/Paste
        if effective_key == 'Copy':
            if isinstance(focus, tk.Entry) and focus.select_present():
                self.root.clipboard_clear()
                self.root.clipboard_append(focus.selection_get())
            return
        if effective_key == 'Paste':
            if isinstance(focus, tk.Entry):
                try: focus.insert(tk.INSERT, self.root.clipboard_get())
                except: pass
            return

        text_to_insert = effective_key
        
        text_to_insert = effective_key
        
        insert_map = {
            # Trigonométricas Inversas
            "sin⁻¹": "asin(", "cos⁻¹": "acos(", "tan⁻¹": "atan(",
            "sin": "sin(",    "cos": "cos(",    "tan": "tan(",
            
            # Potências e Raízes
            "x²": "**2",      "xʸ": "**",       "x⁻¹": "**(-1)",
            "√": "sqrt(",     "ⁿ√": "root(",    
            "eˣ": "exp(",     "10ˣ": "10**",    "ln": "ln(",   "log": "log(",
            
            # Símbolos Matemáticos
            "π": "pi",        "i": "I",         "±": "-",
            "|x|": "abs(",    "∠": "angle(",    "≤": "<=",
            "aᵇ/ᶜ": "/",      "ᵈ/ᶜ": "/",       "Sto": "->",   "Ans": "Ans",
            "≈": "approx(",   "EEX": "*10**",   "x": "x",
            "( )": "()",       "{ }": "{}",       "[]": "[]"
        }
        
        if effective_key in insert_map:
            text_to_insert = insert_map[effective_key]
        
        ignored = [
            "Setup", "Info", "User", "Help", "Settings", "Shift", "Alpha", 
            "▲", "◄", "►", "▼", "Apps", "Home", "CAS", "Plot", "Symb", 
            "Num", "View", "Menu", "Esc", "Clear", "Del", "On", "Enter",
            "Cmds", "Chars", "Mem", "Units", "Def", "List", "Matrix", "Note", "Base"
        ]
        
        if effective_key in ignored:
            return 

        if isinstance(focus, tk.Entry):
            focus.insert(tk.INSERT, text_to_insert)
            
            if effective_key in ["()", "{}", "[]"]:
                idx = focus.index(tk.INSERT)
                focus.icursor(idx - 1)
    
    def _update_keys(self):
        """Atualiza os labels dos botões baseado no estado Shift/Alpha"""
        
        btn_shift = self.btn_cache.get("Shift")
        if btn_shift:
            color = "#0055A3" if self.shift_mode else self.colors["key_blue"]
            btn_shift.config(bg=color)
            
        btn_alpha = self.btn_cache.get("Alpha")
        if btn_alpha:
            color = "#CC5500" if self.alpha_mode else self.colors["key_orange"]
            btn_alpha.config(bg=color)

        for key_orig, btn in self.btn_cache.items():
            if key_orig in ["Shift", "Alpha"]: 
                continue
            
            new_text = key_orig
            
            if self.shift_mode:
                if key_orig in self.KEY_MAP:
                    mapped_text = self.KEY_MAP[key_orig][0]
                    if mapped_text: 
                        new_text = mapped_text

            elif self.alpha_mode:
                if key_orig in self.KEY_MAP:
                    new_text = self.KEY_MAP[key_orig][1] 
                else:
                    new_text = "" 
            
            if btn.cget("text") != new_text:
                btn.config(text=new_text)
    
    def _clear_screen(self):
        """Limpa o histórico e entrada da aba ativa (Comportamento do botão ON)"""
        current = self.notebook.index(self.notebook.select())
        
        focus = self.root.focus_get()
        if isinstance(focus, tk.Entry):
            focus.delete(0, tk.END)

        if current == self.idx_home:
            self.home_history.config(state='normal')
            self.home_history.delete(1.0, tk.END)
            self.home_history.config(state='disabled')
            
        elif current == self.idx_cas:
            self.cas_history.config(state='normal')
            self.cas_history.delete(1.0, tk.END)
            self.cas_history.config(state='disabled')
            
        elif current == self.idx_prog:
            self.program_output.delete(1.0, tk.END)
    
    # --- COLA ISTO ANTES DE _open_matrix_catalog ---
    def _insert_text(self, text):
        """Insere texto no widget que estiver com foco (Entry ou Text)"""
        focus = self.root.focus_get()
        
        # Se o foco não estiver num campo de texto (ex: está na lista),
        # recupera o foco para o campo de entrada da aba atual
        if not isinstance(focus, (tk.Entry, tk.Text)):
            current = self.notebook.index(self.notebook.select())
            if current == self.idx_home: focus = self.entry_home
            elif current == self.idx_cas: focus = self.entry_cas
            elif current == self.idx_plot2d: focus = self.entry_plot
            elif current == self.idx_plot3d: focus = self.entry_plot3d
        
        # Insere o texto
        if focus:
            if isinstance(focus, tk.Entry):
                idx = focus.index(tk.INSERT)
                focus.insert(idx, text)
                # Opcional: mover cursor para dentro dos parênteses se houver
                if "()" in text: focus.icursor(idx + text.index("(") + 1)
                elif "[]" in text: focus.icursor(idx + text.index("[") + 1)
            elif isinstance(focus, tk.Text):
                focus.insert(tk.INSERT, text)
    
    # =========================
    # MATRICES APP (ROBUST - Toplevel)
    # =========================

    def _init_matrix_store(self):
        self.matrices = {f"M{i}": np.zeros((1, 1), dtype=float) for i in range(1, 11)}
        self.matrix_selected = "M1"
        self.matrix_cursor = (0, 0)

    def _close_matrix_win(self):
        if getattr(self, "matrix_win", None) is not None and self.matrix_win.winfo_exists():
            self.matrix_win.destroy()
        self.matrix_win = None

    def _open_matrices_app(self):
        # toggle
        if getattr(self, "matrix_win", None) is not None and self.matrix_win.winfo_exists():
            self.matrix_win.lift()
            return

        # overlay dentro da "telinha" (Notebook)
        w = tk.Frame(self.notebook, bg="#F5F5F5")
        self.matrix_win = w
        w.place(relx=0, rely=0, relwidth=1, relheight=1)

        # fecha com Esc
        self.root.bind("<Escape>", lambda e: self._close_matrix_win())

        # ===== Header =====
        header = tk.Frame(w, bg="#1E63B5", height=42)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Matrizes",
            bg="#1E63B5", fg="white",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=12)

        tk.Button(
            header, text="✕",
            command=self._close_matrix_win,
            bg="#1E63B5", fg="white",
            bd=0, font=("Segoe UI", 12)
        ).pack(side="right", padx=10)

        # ===== Stack frames (list/edit) =====
        self._mat_stack = tk.Frame(w, bg="#F5F5F5")
        self._mat_stack.pack(fill="both", expand=True)

        self._mat_list_frame = tk.Frame(self._mat_stack, bg="#F5F5F5")
        self._mat_edit_frame = tk.Frame(self._mat_stack, bg="#BFD7EA")

        for f in (self._mat_list_frame, self._mat_edit_frame):
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ===== List UI =====
        cols = ("name", "dims", "mem")
        tree = ttk.Treeview(self._mat_list_frame, columns=cols, show="headings", selectmode="browse")
        self._mat_tree = tree

        tree.heading("name", text="Matriz")
        tree.heading("dims", text="Dim")
        tree.heading("mem", text="Mem")

        tree.column("name", width=120, anchor="w")
        tree.column("dims", width=90, anchor="w")
        tree.column("mem", width=90, anchor="e")

        vsb = ttk.Scrollbar(self._mat_list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        vsb.pack(side="right", fill="y", padx=(0, 10), pady=10)

        def refresh_tree():
            tree.delete(*tree.get_children())
            for i in range(1, 11):
                name = f"M{i}"
                A = self.matrices[name]
                dims = f"{A.shape[0]}×{A.shape[1]}"
                mem = f"{A.nbytes/1024.0:.2f} KB"
                tree.insert("", "end", iid=name, values=(name, dims, mem))

            if self.matrix_selected not in self.matrices:
                self.matrix_selected = "M1"
            tree.selection_set(self.matrix_selected)
            tree.see(self.matrix_selected)

        def on_select(_e=None):
            sel = tree.selection()
            if sel:
                self.matrix_selected = sel[0]

        tree.bind("<<TreeviewSelect>>", on_select)
        tree.bind("<Double-Button-1>", lambda e: open_editor())
        tree.bind("<Return>", lambda e: open_editor())

        # ===== Buttons bottom =====
        bar = tk.Frame(w, bg="#202124", height=52)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        def bar_btn(text, cmd):
            b = tk.Button(bar, text=text, command=cmd, bg="#202124", fg="white",
                          bd=0, font=("Segoe UI", 10))
            b.pack(side="left", fill="both", expand=True, padx=1, pady=1)
            return b

        def confirm_delete():
            name = self.matrix_selected
            if not name:
                return
            ok = messagebox.askokcancel("Eliminar", f"Quer mesmo eliminar {name}?")
            if not ok:
                return
            self.matrices[name] = np.zeros((1, 1), dtype=float)
            self.matrix_cursor = (0, 0)
            refresh_tree()

        def vet_action():
            name = self.matrix_selected
            A = self.matrices[name]
            r, c = A.shape
            if (r == 1 and c > 1) or (c == 1 and r > 1):
                self.matrices[name] = A.T
                self.matrix_cursor = (0, 0)
            else:
                messagebox.showinfo("Vet", "Vet funciona para vetores 1×N ou N×1 (faz transposição).")
            refresh_tree()

        def open_editor():
            name = self.matrix_selected
            if not name:
                return
            self._matrix_open_editor_view(name)

        bar_btn("Editar", open_editor)
        bar_btn("Eliminar", confirm_delete)
        bar_btn("Vet", vet_action)
        bar_btn("Fechar", self._close_matrix_win)

        refresh_tree()
        self._mat_list_frame.lift()

    def _matrix_open_editor_view(self, name):
        self.matrix_selected = name

        # limpa edit frame
        for w in self._mat_edit_frame.winfo_children():
            w.destroy()

        top = tk.Frame(self._mat_edit_frame, bg="#BFD7EA", height=44)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text=f"{name}", bg="#BFD7EA", fg="#111",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=12)

        def back():
            self._mat_list_frame.lift()

        tk.Button(top, text="Voltar", command=back,
                  bg="#E0E0E0", fg="#111", relief="raised").pack(side="right", padx=10, pady=6)

        # botões
        ctrl = tk.Frame(self._mat_edit_frame, bg="#BFD7EA")
        ctrl.pack(fill="x", padx=10, pady=(6, 0))

        def add_row():
            A = self.matrices[name]
            self.matrices[name] = np.vstack([A, np.zeros((1, A.shape[1]))])
            render_grid()

        def add_col():
            A = self.matrices[name]
            self.matrices[name] = np.hstack([A, np.zeros((A.shape[0], 1))])
            render_grid()

        def del_row():
            A = self.matrices[name]
            if A.shape[0] <= 1:
                return
            self.matrices[name] = A[:-1, :]
            self.matrix_cursor = (min(self.matrix_cursor[0], self.matrices[name].shape[0]-1), self.matrix_cursor[1])
            render_grid()

        def del_col():
            A = self.matrices[name]
            if A.shape[1] <= 1:
                return
            self.matrices[name] = A[:, :-1]
            self.matrix_cursor = (self.matrix_cursor[0], min(self.matrix_cursor[1], self.matrices[name].shape[1]-1))
            render_grid()

        def goto():
            A = self.matrices[name]

            # se já existir um "Ir p/" aberto, fecha antes
            if hasattr(self, "_goto_overlay") and self._goto_overlay.winfo_exists():
                self._goto_overlay.destroy()

            # overlay por cima da tela de matrizes (dentro do app)
            ov = tk.Frame(self.matrix_win, bg="#000000")
            self._goto_overlay = ov
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            ov.lift()

            # "card" central
            card = tk.Frame(ov, bg="#FFFFFF", bd=2, relief="raised")
            card.place(relx=0.5, rely=0.5, anchor="c")

            tk.Label(card, text="Ir para", bg="#FFFFFF", font=("Segoe UI", 11, "bold")).grid(
                row=0, column=0, columnspan=2, padx=12, pady=(10, 6)
            )

            tk.Label(card, text="Linha (1..):", bg="#FFFFFF").grid(row=1, column=0, padx=10, pady=6, sticky="e")
            tk.Label(card, text="Coluna (1..):", bg="#FFFFFF").grid(row=2, column=0, padx=10, pady=6, sticky="e")

            er = tk.Entry(card, width=10)
            ec = tk.Entry(card, width=10)
            er.grid(row=1, column=1, padx=10, pady=6)
            ec.grid(row=2, column=1, padx=10, pady=6)

            r, c = self.matrix_cursor
            er.insert(0, str(r + 1))
            ec.insert(0, str(c + 1))

            def close():
                if ov.winfo_exists():
                    ov.destroy()

            def ok(_e=None):
                try:
                    rr = int(er.get()) - 1
                    cc = int(ec.get()) - 1
                except Exception:
                    close()
                    return

                rr = max(0, min(A.shape[0] - 1, rr))
                cc = max(0, min(A.shape[1] - 1, cc))
                self.matrix_cursor = (rr, cc)
                render_grid()
                close()

            btns = tk.Frame(card, bg="#FFFFFF")
            btns.grid(row=3, column=0, columnspan=2, pady=(6, 10))

            tk.Button(btns, text="Cancelar", command=close, bg="#E0E0E0").pack(side="left", padx=6)
            tk.Button(btns, text="OK", command=ok, bg="#4a6fa5", fg="white").pack(side="left", padx=6)

            # atalhos
            ov.bind("<Escape>", lambda e: close())
            er.bind("<Return>", ok)
            ec.bind("<Return>", ok)

            # prende o foco no modal
            er.focus_set()
            er.select_range(0, tk.END)

        tk.Button(ctrl, text="+Linha", command=add_row, bg="#E0E0E0").pack(side="left", padx=4, pady=4)
        tk.Button(ctrl, text="+Col", command=add_col, bg="#E0E0E0").pack(side="left", padx=4, pady=4)
        tk.Button(ctrl, text="-Linha", command=del_row, bg="#E0E0E0").pack(side="left", padx=4, pady=4)
        tk.Button(ctrl, text="-Col", command=del_col, bg="#E0E0E0").pack(side="left", padx=4, pady=4)
        tk.Button(ctrl, text="Ir p/", command=goto, bg="#E0E0E0").pack(side="left", padx=12, pady=4)

        # scroll area
        wrap = tk.Frame(self._mat_edit_frame, bg="#BFD7EA")
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(wrap, bg="#BFD7EA", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=canvas.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        inner = tk.Frame(canvas, bg="#BFD7EA")
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=max(e.width, 300)))

        entries = {}

        def parse_cell(s):
            s = s.strip()
            if s == "":
                return 0.0
            v = sp.N(sp.sympify(s, locals={"pi": sp.pi, "E": sp.E}))
            return float(v)

        def commit(i, j):
            A = self.matrices[name]

            # ✅ se a matriz mudou de tamanho (re-render / delete col/row), ignora commits antigos
            rows, cols = A.shape
            if i < 0 or j < 0 or i >= rows or j >= cols:
                return

            e = entries.get((i, j))
            if not e or not e.winfo_exists():
                return

            try:
                A[i, j] = parse_cell(e.get())
            except Exception:
                # se não conseguir converter, não quebra
                return

            # escreve o valor normalizado de volta
            e.delete(0, tk.END)
            e.insert(0, str(A[i, j]))

        def focus_cell(i, j):
            A = self.matrices[name]
            i = max(0, min(A.shape[0] - 1, i))
            j = max(0, min(A.shape[1] - 1, j))
            self.matrix_cursor = (i, j)
            ee = entries.get((i, j))
            if ee:
                ee.focus_set()
                ee.select_range(0, tk.END)

        def render_grid():
            for w in inner.winfo_children():
                w.destroy()
            entries.clear()

            A = self.matrices[name]
            rows, cols = A.shape

            tk.Label(inner, text=name, bg="#DDE6EE", width=6, relief="solid").grid(row=0, column=0, sticky="nsew")
            for j in range(cols):
                tk.Label(inner, text=str(j + 1), bg="#DDE6EE", width=10, relief="solid").grid(row=0, column=j + 1, sticky="nsew")

            for i in range(rows):
                tk.Label(inner, text=str(i + 1), bg="#DDE6EE", width=6, relief="solid").grid(row=i + 1, column=0, sticky="nsew")
                for j in range(cols):
                    e = tk.Entry(inner, width=12, justify="right")
                    e.insert(0, str(A[i, j]))
                    e.grid(row=i + 1, column=j + 1, sticky="nsew")
                    entries[(i, j)] = e

                    e.bind("<FocusOut>", lambda ev, ii=i, jj=j: commit(ii, jj))
                    e.bind("<Return>", lambda ev, ii=i, jj=j: (commit(ii, jj), "break"))

                    e.bind("<Up>",    lambda ev, ii=i, jj=j: (commit(ii, jj), focus_cell(ii - 1, jj), "break"))
                    e.bind("<Down>",  lambda ev, ii=i, jj=j: (commit(ii, jj), focus_cell(ii + 1, jj), "break"))
                    e.bind("<Left>",  lambda ev, ii=i, jj=j: (commit(ii, jj), focus_cell(ii, jj - 1), "break"))
                    e.bind("<Right>", lambda ev, ii=i, jj=j: (commit(ii, jj), focus_cell(ii, jj + 1), "break"))

                    e.bind("<FocusIn>", lambda ev, ii=i, jj=j: setattr(self, "matrix_cursor", (ii, jj)))

            r, c = getattr(self, "matrix_cursor", (0, 0))
            focus_cell(r, c)

        render_grid()
        self._mat_edit_frame.lift()

if __name__ == "__main__":
    root = tk.Tk()
    app = HPPrimeUltimate(root)
    root.mainloop()
