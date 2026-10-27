"""Thème visuel « façon Telegram » (mode sombre) : couleurs et composants Tkinter."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# Palette inspirée du thème sombre de Telegram Desktop
FOND = "#0e1621"
PANNEAU = "#17212b"
PANNEAU_CLAIR = "#242f3d"
SEPARATEUR = "#0b121a"
BULLE = "#2b5278"
BLEU = "#5288c1"
BLEU_SURVOL = "#6a9bd1"
ACCENT = "#6ab3f3"
TEXTE = "#f5f5f5"
TEXTE_GRIS = "#7f91a4"
VERT = "#4fae4e"
ORANGE = "#e0a84f"
ROUGE = "#ec7676"
POLICE = "Segoe UI"


def rect_arrondi(canevas, x1, y1, x2, y2, rayon, **options):
    points = [x1 + rayon, y1, x2 - rayon, y1, x2, y1, x2, y1 + rayon,
              x2, y2 - rayon, x2, y2, x2 - rayon, y2, x1 + rayon, y2,
              x1, y2, x1, y2 - rayon, x1, y1 + rayon, x1, y1]
    return canevas.create_polygon(points, smooth=True, **options)


class Bouton(tk.Canvas):
    """Bouton arrondi (pilule) avec survol et état désactivé."""

    STYLES = {
        "primaire": (BLEU, BLEU_SURVOL, "#ffffff"),
        "secondaire": (PANNEAU_CLAIR, "#2f3d4e", TEXTE),
        "danger": ("#33262b", "#47303a", ROUGE),
        "discret": (PANNEAU, PANNEAU_CLAIR, ACCENT),
    }

    def __init__(self, parent, texte, commande, style="secondaire", fond=PANNEAU,
                 largeur=None, hauteur=36, gras=False):
        self._police = tkfont.Font(family=POLICE, size=10, weight="bold" if gras else "normal")
        self._largeur = largeur or self._police.measure(texte) + 36
        self._hauteur = hauteur
        super().__init__(parent, width=self._largeur, height=hauteur, bg=fond,
                         highlightthickness=0, cursor="hand2")
        self._texte, self._commande, self._style = texte, commande, style
        self._actif, self._survol = True, False
        self._dessiner()
        self.bind("<Enter>", lambda _: self._changer_survol(True))
        self.bind("<Leave>", lambda _: self._changer_survol(False))
        self.bind("<ButtonRelease-1>", self._clic)

    def _dessiner(self):
        self.delete("all")
        normal, survol, texte = self.STYLES[self._style]
        if not self._actif:
            couleur, couleur_texte = "#1b2632", "#52616f"
        else:
            couleur = survol if self._survol else normal
            couleur_texte = texte
        rect_arrondi(self, 1, 1, self._largeur - 1, self._hauteur - 1, self._hauteur // 2,
                     fill=couleur, outline=couleur)
        self.create_text(self._largeur // 2, self._hauteur // 2, text=self._texte,
                         fill=couleur_texte, font=self._police)
        self.configure(cursor="hand2" if self._actif else "arrow")

    def _changer_survol(self, valeur):
        self._survol = valeur
        self._dessiner()

    def _clic(self, evenement):
        if self._actif and 0 <= evenement.x <= self._largeur and 0 <= evenement.y <= self._hauteur:
            self._commande()

    def state(self, etats):
        """Même interface que ttk : state(["disabled"]) / state(["!disabled"])."""
        if "disabled" in etats:
            self._actif = False
        elif "!disabled" in etats:
            self._actif = True
        self._dessiner()


class Bulle(tk.Canvas):
    """Bulle de message arrondie ; placez les widgets dans `.interieur`."""

    def __init__(self, parent, couleur=BULLE, fond=FOND, rayon=16, marge=12):
        super().__init__(parent, bg=fond, highlightthickness=0, height=20)
        self._couleur, self._rayon, self._marge = couleur, rayon, marge
        self.interieur = tk.Frame(self, bg=couleur)
        self._fenetre = self.create_window(marge, marge, window=self.interieur, anchor="nw")
        self.bind("<Configure>", self._redessiner)
        self.interieur.bind("<Configure>", self._ajuster)

    def _ajuster(self, _):
        self.configure(height=self.interieur.winfo_reqheight() + 2 * self._marge)

    def _redessiner(self, evenement):
        self.delete("fond")
        rect_arrondi(self, 0, 0, evenement.width, evenement.height, self._rayon,
                     fill=self._couleur, outline=self._couleur, tags="fond")
        self.tag_lower("fond")
        self.itemconfigure(self._fenetre, width=max(10, evenement.width - 2 * self._marge))


class Avatar(tk.Canvas):
    def __init__(self, parent, lettre="A", taille=44, fond=PANNEAU):
        super().__init__(parent, width=taille, height=taille, bg=fond, highlightthickness=0)
        self.create_oval(1, 1, taille - 1, taille - 1, fill=BLEU, outline=BLEU)
        self.create_text(taille // 2, taille // 2, text=lettre, fill="white",
                         font=(POLICE, int(taille * 0.42), "bold"))


class InfoBulle:
    def __init__(self, widget, texte):
        self.widget, self.texte, self.fenetre = widget, texte, None
        widget.bind("<Enter>", self._afficher, add="+")
        widget.bind("<Leave>", self._masquer, add="+")

    def _afficher(self, _):
        if self.fenetre:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.fenetre = tk.Toplevel(self.widget)
        self.fenetre.wm_overrideredirect(True)
        self.fenetre.wm_geometry(f"+{x}+{y}")
        tk.Label(self.fenetre, text=self.texte, background=PANNEAU_CLAIR, foreground=TEXTE,
                 relief="flat", borderwidth=0, wraplength=320, justify="left",
                 padx=10, pady=6, font=(POLICE, 9)).pack()

    def _masquer(self, _):
        if self.fenetre:
            self.fenetre.destroy()
            self.fenetre = None


def appliquer_theme(racine: tk.Tk) -> None:
    """Configure les widgets ttk (curseurs, listes, cases, barre de progression)."""
    racine.configure(bg=FOND)
    style = ttk.Style(racine)
    style.theme_use("clam")
    style.configure("TFrame", background=PANNEAU)
    style.configure("TLabel", background=PANNEAU, foreground=TEXTE, font=(POLICE, 10))
    style.configure("Horizontal.TScale", background=PANNEAU, troughcolor=FOND,
                    bordercolor=PANNEAU, lightcolor=BLEU, darkcolor=BLEU)
    style.map("Horizontal.TScale", background=[("active", PANNEAU)])
    for nom in ("TCombobox", "TSpinbox"):
        style.configure(nom, fieldbackground=PANNEAU_CLAIR, background=PANNEAU_CLAIR,
                        foreground=TEXTE, arrowcolor=ACCENT, bordercolor=PANNEAU_CLAIR,
                        lightcolor=PANNEAU_CLAIR, darkcolor=PANNEAU_CLAIR,
                        selectbackground=PANNEAU_CLAIR, selectforeground=TEXTE, padding=5)
        style.map(nom, fieldbackground=[("readonly", PANNEAU_CLAIR), ("disabled", PANNEAU)],
                  foreground=[("disabled", TEXTE_GRIS)])
    style.configure("TCheckbutton", background=PANNEAU, foreground=TEXTE, font=(POLICE, 10))
    style.map("TCheckbutton", background=[("active", PANNEAU)],
              foreground=[("disabled", TEXTE_GRIS)],
              indicatorcolor=[("selected", BLEU), ("!selected", PANNEAU_CLAIR)])
    style.configure("Telegram.Horizontal.TProgressbar", troughcolor="#1d3a57", background=ACCENT,
                    bordercolor=BULLE, lightcolor=ACCENT, darkcolor=ACCENT, thickness=6)
    style.configure("Vertical.TScrollbar", background=PANNEAU_CLAIR, troughcolor=FOND,
                    bordercolor=FOND, arrowcolor=TEXTE_GRIS, lightcolor=PANNEAU_CLAIR,
                    darkcolor=PANNEAU_CLAIR)
    racine.option_add("*TCombobox*Listbox.background", PANNEAU_CLAIR)
    racine.option_add("*TCombobox*Listbox.foreground", TEXTE)
    racine.option_add("*TCombobox*Listbox.selectBackground", BLEU)
    racine.option_add("*TCombobox*Listbox.selectForeground", "white")
