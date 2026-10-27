"""Interface graphique Tkinter (entièrement en français)."""

import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import VERSION, journal
from . import libelles as L
from . import securite
from .rythme import MODE_HUMAIN, MODE_RAPIDE
from .saisie import ETAT_LIBELLE, Etat, MoteurSaisie, SurveillanceUrgence
from .style import (ACCENT, BLEU, FOND, ORANGE, PANNEAU, PANNEAU_CLAIR, POLICE, ROUGE, SEPARATEUR,
                    TEXTE, TEXTE_GRIS, VERT, BULLE as BULLE_COULEUR, Avatar, Bouton, Bulle, InfoBulle, appliquer_theme)
from .texte import ErreurImportation, importer_fichier, texte_est_vide
from .word_com import CibleWord

LIBELLE_ETAT_WORD = {
    securite.ETAT_ACTIF: L.WORD_DETECTE,
    securite.ETAT_OUVERT_NON_ACTIF: L.WORD_OUVERT_NON_ACTIF,
    securite.ETAT_FERME: L.WORD_NON_DETECTE,
    securite.ETAT_NON_INSTALLE: L.WORD_NON_INSTALLE,
}
VITESSE_DEFAUT = {L.MODE_RAPIDE: 60, L.MODE_HUMAIN: 8}


class Application:
    def __init__(self, racine: tk.Tk, moteur: MoteurSaisie):
        self.racine = racine
        self.moteur = moteur
        self.etat_word = securite.ETAT_FERME
        self.prochaine_verif_word = 0
        self.taille_groupe = tk.IntVar(value=4)
        self.journal_actif = tk.BooleanVar(value=False)
        self.arriere_plan = tk.BooleanVar(value=False)

        racine.title(L.NOM_LOGICIEL)
        racine.geometry("1100x740")
        racine.minsize(960, 680)
        self._construire()
        racine.protocol("WM_DELETE_WINDOW", self.quitter)
        self._sur_changement_mode()
        self._maj_compteur()
        self.racine.after(100, self._boucle_interface)

    # --- Construction ---

    def _construire(self):
        appliquer_theme(self.racine)
        self.racine.columnconfigure(1, weight=1)
        self.racine.rowconfigure(0, weight=1)
        self._construire_barre_laterale()
        self._construire_zone_principale()

    def _titre_section(self, parent, texte, fond=PANNEAU):
        tk.Label(parent, text=texte, bg=fond, fg=ACCENT, font=(POLICE, 10, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(14, 6))

    def _ligne_parametre(self, parent, titre):
        cadre = tk.Frame(parent, bg=PANNEAU)
        cadre.pack(fill="x", padx=16, pady=(0, 9))
        entete = tk.Frame(cadre, bg=PANNEAU)
        entete.pack(fill="x")
        tk.Label(entete, text=titre, bg=PANNEAU, fg=TEXTE_GRIS, font=(POLICE, 9),
                 anchor="w", wraplength=210, justify="left").pack(side="left")
        valeur = tk.Label(entete, text="", bg=PANNEAU, fg=TEXTE, font=(POLICE, 10, "bold"))
        valeur.pack(side="right")
        return cadre, valeur

    def _construire_barre_laterale(self):
        barre = tk.Frame(self.racine, bg=PANNEAU, width=320)
        barre.grid(row=0, column=0, sticky="ns")
        barre.grid_propagate(False)
        barre.pack_propagate(False)

        # En-tête : avatar, nom du logiciel et état de Word (comme « en ligne »)
        entete = tk.Frame(barre, bg=PANNEAU)
        entete.pack(fill="x", padx=16, pady=(16, 4))
        Avatar(entete, "A").pack(side="left")
        textes = tk.Frame(entete, bg=PANNEAU)
        textes.pack(side="left", padx=12)
        tk.Label(textes, text=L.NOM_LOGICIEL, bg=PANNEAU, fg=TEXTE,
                 font=(POLICE, 13, "bold"), anchor="w").pack(anchor="w")
        self.lbl_word = tk.Label(textes, text="", bg=PANNEAU, fg=TEXTE_GRIS,
                                 font=(POLICE, 9), anchor="w")
        self.lbl_word.pack(anchor="w")

        tk.Frame(barre, bg=SEPARATEUR, height=1).pack(fill="x", pady=(10, 0))
        self._titre_section(barre, L.ZONE_PARAMETRES)

        # Mode
        cadre, _ = self._ligne_parametre(barre, L.LBL_MODE)
        self.var_mode = tk.StringVar(value=L.MODE_RAPIDE)
        self.liste_mode = ttk.Combobox(cadre, textvariable=self.var_mode, state="readonly",
                                       values=[L.MODE_RAPIDE, L.MODE_HUMAIN])
        self.liste_mode.pack(fill="x", pady=(4, 0))
        self.liste_mode.bind("<<ComboboxSelected>>", lambda _: self._sur_changement_mode())
        InfoBulle(self.liste_mode, L.INFOBULLES["mode"])

        # Vitesse
        cadre, self.lbl_vitesse = self._ligne_parametre(barre, L.LBL_VITESSE)
        self.var_vitesse = tk.IntVar(value=VITESSE_DEFAUT[L.MODE_RAPIDE])
        self.echelle_vitesse = ttk.Scale(cadre, from_=1, to=200, variable=self.var_vitesse,
                                         command=lambda v: self.var_vitesse.set(int(float(v))))
        self.echelle_vitesse.pack(fill="x", pady=(4, 0))
        InfoBulle(self.echelle_vitesse, L.INFOBULLES["vitesse"])

        # Intensité des pauses
        cadre, self.lbl_intensite = self._ligne_parametre(barre, L.LBL_INTENSITE)
        self.var_intensite = tk.IntVar(value=5)
        self.echelle_intensite = ttk.Scale(cadre, from_=0, to=10, variable=self.var_intensite,
                                           command=lambda v: self.var_intensite.set(int(float(v))))
        self.echelle_intensite.pack(fill="x", pady=(4, 0))
        InfoBulle(self.echelle_intensite, L.INFOBULLES["intensite"])

        # Délai
        cadre, _ = self._ligne_parametre(barre, L.LBL_DELAI)
        self.var_delai = tk.IntVar(value=5)
        self.champ_delai = ttk.Spinbox(cadre, from_=1, to=60, textvariable=self.var_delai, width=8)
        self.champ_delai.pack(anchor="w", pady=(4, 0))
        InfoBulle(self.champ_delai, L.INFOBULLES["delai"])

        # Nombre de caractères et état de Word
        _, self.lbl_nb = self._ligne_parametre(barre, L.LBL_NB_CARACTERES)
        cadre, _ = self._ligne_parametre(barre, L.LBL_ETAT_WORD)
        self.lbl_word_param = tk.Label(cadre, text="", bg=PANNEAU, fg=TEXTE_GRIS,
                                       font=(POLICE, 9, "bold"), anchor="w", justify="left",
                                       wraplength=280)
        self.lbl_word_param.pack(fill="x", pady=(3, 0))

        # Saisie en arrière-plan
        self.chk_arriere = ttk.Checkbutton(barre, text=L.LBL_ARRIERE_PLAN, variable=self.arriere_plan)
        self.chk_arriere.pack(anchor="w", padx=16, pady=(2, 0))
        InfoBulle(self.chk_arriere, L.INFOBULLES["arriere_plan"])

        # Bas de la barre latérale : Paramètres, À propos, Quitter
        bas = tk.Frame(barre, bg=PANNEAU)
        bas.pack(side="bottom", fill="x", padx=16, pady=(0, 14))
        tk.Label(bas, text=f"Arrêt d'urgence : {L.RACCOURCI_URGENCE}", bg=PANNEAU,
                 fg=TEXTE_GRIS, font=(POLICE, 8), wraplength=280, justify="left",
                 anchor="w").pack(fill="x", pady=(0, 8))
        self.btn_parametres = Bouton(bas, L.BTN_PARAMETRES, self.ouvrir_parametres,
                                     "secondaire", PANNEAU, largeur=288)
        self.btn_apropos = Bouton(bas, L.BTN_APROPOS, self.apropos, "secondaire", PANNEAU,
                                  largeur=288)
        self.btn_quitter = Bouton(bas, L.BTN_QUITTER, self.quitter, "danger", PANNEAU,
                                  largeur=288)
        for bouton in (self.btn_parametres, self.btn_apropos, self.btn_quitter):
            bouton.pack(pady=3)

    def _construire_zone_principale(self):
        zone = tk.Frame(self.racine, bg=FOND)
        zone.grid(row=0, column=1, sticky="nsew")
        zone.columnconfigure(0, weight=1)
        zone.rowconfigure(2, weight=1)

        # Barre du haut (titre + compteur)
        haut = tk.Frame(zone, bg=PANNEAU, height=58)
        haut.grid(row=0, column=0, sticky="ew")
        haut.grid_propagate(False)
        tk.Label(haut, text=L.ZONE_TEXTE, bg=PANNEAU, fg=TEXTE,
                 font=(POLICE, 12, "bold")).place(x=20, y=8)
        self.lbl_compteur_haut = tk.Label(haut, text="", bg=PANNEAU, fg=TEXTE_GRIS,
                                          font=(POLICE, 9))
        self.lbl_compteur_haut.place(x=20, y=32)

        # Importation et effacement
        outils = tk.Frame(zone, bg=FOND)
        outils.grid(row=1, column=0, sticky="ew", padx=18, pady=(12, 6))
        tk.Label(outils, text=L.ZONE_IMPORT, bg=FOND, fg=TEXTE_GRIS,
                 font=(POLICE, 9)).pack(side="left", padx=(0, 10))
        self.btn_import_txt = Bouton(outils, L.BTN_IMPORT_TXT,
                                     lambda: self.importer([("txt", "*.txt")]), "discret", FOND)
        self.btn_import_docx = Bouton(outils, L.BTN_IMPORT_DOCX,
                                      lambda: self.importer([("docx", "*.docx")]), "discret", FOND)
        self.btn_importer = Bouton(outils, L.BTN_IMPORTER, self.importer, "discret", FOND)
        self.btn_effacer = Bouton(outils, L.BTN_EFFACER, self.effacer, "danger", FOND)
        for bouton in (self.btn_import_txt, self.btn_import_docx, self.btn_importer):
            bouton.pack(side="left", padx=3)
        self.btn_effacer.pack(side="right", padx=3)

        # Zone de texte (comme le fil de discussion)
        cadre_texte = tk.Frame(zone, bg=FOND)
        cadre_texte.grid(row=2, column=0, sticky="nsew", padx=18, pady=(4, 8))
        cadre_texte.columnconfigure(0, weight=1)
        cadre_texte.rowconfigure(0, weight=1)
        self.zone_texte = tk.Text(cadre_texte, wrap="word", undo=True, font=(POLICE, 11),
                                  bg=PANNEAU, fg=TEXTE, insertbackground=TEXTE, relief="flat",
                                  borderwidth=0, highlightthickness=0, padx=16, pady=12,
                                  selectbackground=BLEU, selectforeground="white",
                                  spacing3=4, height=8)
        defilement = ttk.Scrollbar(cadre_texte, command=self.zone_texte.yview)
        self.zone_texte.configure(yscrollcommand=defilement.set)
        self.zone_texte.grid(row=0, column=0, sticky="nsew")
        defilement.grid(row=0, column=1, sticky="ns")
        self.zone_texte.bind("<<Modified>>", self._sur_modification)

        # Bulle de progression
        bulle = Bulle(zone)
        bulle.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 8))
        interieur = bulle.interieur
        tk.Label(interieur, text=L.ZONE_PROGRESSION, bg=BULLE_COULEUR, fg=ACCENT,
                 font=(POLICE, 9, "bold"), anchor="w").pack(fill="x")
        self.lbl_etat = tk.Label(interieur, bg=BULLE_COULEUR, fg=TEXTE,
                                 font=(POLICE, 11, "bold"), anchor="w")
        self.lbl_etat.pack(fill="x", pady=(2, 4))
        self.barre = ttk.Progressbar(interieur, maximum=100,
                                     style="Telegram.Horizontal.TProgressbar")
        self.barre.pack(fill="x", pady=(0, 4))
        self.lbl_saisis = tk.Label(interieur, bg=BULLE_COULEUR, fg=TEXTE, font=(POLICE, 10),
                                   anchor="w")
        self.lbl_saisis.pack(fill="x")
        ligne = tk.Frame(interieur, bg=BULLE_COULEUR)
        ligne.pack(fill="x")
        self.lbl_mode_utilise = tk.Label(ligne, bg=BULLE_COULEUR, fg="#b9d3ee",
                                         font=(POLICE, 9), anchor="w")
        self.lbl_mode_utilise.pack(side="left")
        self.lbl_vitesse_reelle = tk.Label(ligne, bg=BULLE_COULEUR, fg="#b9d3ee",
                                           font=(POLICE, 9), anchor="e")
        self.lbl_vitesse_reelle.pack(side="right")
        self.lbl_message = tk.Label(interieur, bg=BULLE_COULEUR, fg="#ffb4a8",
                                    font=(POLICE, 9), anchor="w", justify="left", wraplength=640)
        self.lbl_message.pack(fill="x")

        # Barre de commandes (comme la zone de saisie de Telegram)
        commandes = tk.Frame(zone, bg=PANNEAU, height=64)
        commandes.grid(row=4, column=0, sticky="ew")
        commandes.grid_propagate(False)
        self.btn_demarrer = Bouton(commandes, L.BTN_DEMARRER, self.demarrer, "primaire",
                                   PANNEAU, hauteur=40, gras=True)
        self.btn_pause = Bouton(commandes, L.BTN_PAUSE, self.moteur.mettre_en_pause,
                                "secondaire", PANNEAU, hauteur=40)
        self.btn_reprendre = Bouton(commandes, L.BTN_REPRENDRE, self.reprendre,
                                    "secondaire", PANNEAU, hauteur=40)
        self.btn_arreter = Bouton(commandes, L.BTN_ARRETER, self.moteur.arreter,
                                  "danger", PANNEAU, hauteur=40)
        for i, bouton in enumerate((self.btn_demarrer, self.btn_pause, self.btn_reprendre,
                                    self.btn_arreter)):
            bouton.pack(side="left", padx=(18 if i == 0 else 6, 0), pady=12)

    # --- Actions ---

    def _texte(self) -> str:
        return self.zone_texte.get("1.0", "end-1c")

    def _sur_modification(self, _):
        self.zone_texte.edit_modified(False)
        self._maj_compteur()

    def _maj_compteur(self):
        nombre = len(self._texte())
        self.lbl_nb.config(text=str(nombre))
        self.lbl_compteur_haut.config(
            text=f"{nombre} caractère{'s' if nombre > 1 else ''}")

    def _mode_interne(self) -> str:
        return MODE_HUMAIN if self.var_mode.get() == L.MODE_HUMAIN else MODE_RAPIDE

    def _sur_changement_mode(self):
        self.var_vitesse.set(VITESSE_DEFAUT[self.var_mode.get()])
        humain = self._mode_interne() == MODE_HUMAIN
        self.echelle_intensite.state(["!disabled"] if humain else ["disabled"])

    def importer(self, types=None):
        if types is None:
            types = [(L.TYPE_TOUS, "*.txt *.docx"), (L.TYPE_TXT, "*.txt"), (L.TYPE_DOCX, "*.docx")]
        chemin = filedialog.askopenfilename(title=L.TITRE_OUVRIR_FICHIER, filetypes=types)
        if not chemin:
            return
        try:
            contenu = importer_fichier(chemin)
        except ErreurImportation as exc:
            messagebox.showerror(L.TITRE_ERREUR, str(exc))
            return
        self.zone_texte.delete("1.0", "end")
        self.zone_texte.insert("1.0", contenu)
        if chemin.lower().endswith(".docx"):
            messagebox.showinfo(L.TITRE_INFO, L.MSG_LIMITE_DOCX)

    def effacer(self):
        if self._texte() and messagebox.askyesno(L.TITRE_CONFIRMATION, L.MSG_CONFIRMER_EFFACER):
            self.zone_texte.delete("1.0", "end")

    def _delai(self) -> int:
        try:
            return max(1, min(60, int(self.var_delai.get())))
        except (tk.TclError, ValueError):
            return 5

    def demarrer(self):
        texte = self._texte()
        if texte_est_vide(texte):
            messagebox.showwarning(L.TITRE_ATTENTION, L.MSG_TEXTE_VIDE)
            return
        etat = securite.etat_word()
        if etat == securite.ETAT_NON_INSTALLE:
            messagebox.showerror(L.TITRE_ERREUR, L.MSG_WORD_NON_INSTALLE)
            return
        if etat == securite.ETAT_FERME:
            messagebox.showwarning(L.TITRE_ATTENTION, L.MSG_WORD_FERME)
            return
        arriere = self.arriere_plan.get()
        self.moteur.configurer(texte, self._mode_interne(), self.var_vitesse.get(),
                               self.var_intensite.get(), self.taille_groupe.get(), arriere)
        self.moteur.demarrer(0 if arriere else self._delai())

    def reprendre(self):
        self.moteur.reprendre(0 if self.moteur.arriere_plan else self._delai())

    def ouvrir_parametres(self):
        fenetre = tk.Toplevel(self.racine)
        fenetre.title(L.BTN_PARAMETRES)
        fenetre.transient(self.racine)
        fenetre.resizable(False, False)
        fenetre.configure(bg=PANNEAU)
        cadre = ttk.Frame(fenetre, padding=16)
        cadre.pack()
        ttk.Label(cadre, text=L.LBL_TAILLE_GROUPE).grid(row=0, column=0, sticky="w")
        ttk.Spinbox(cadre, from_=1, to=10, textvariable=self.taille_groupe, width=5).grid(
            row=0, column=1, padx=8)
        ttk.Checkbutton(cadre, text=L.LBL_JOURNAL, variable=self.journal_actif,
                        command=lambda: journal.activer(self.journal_actif.get())).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=8)
        Bouton(cadre, L.BTN_FERMER, fenetre.destroy, "primaire", PANNEAU).grid(
            row=2, column=1, sticky="e")

    def apropos(self):
        messagebox.showinfo(L.BTN_APROPOS, L.TEXTE_APROPOS.format(
            nom=L.NOM_LOGICIEL, version=VERSION, urgence=L.RACCOURCI_URGENCE))

    def quitter(self):
        if self.moteur.en_cours():
            if not messagebox.askyesno(L.TITRE_CONFIRMATION, L.MSG_CONFIRMER_QUITTER):
                return
            self.moteur.arreter()
        self.racine.destroy()

    # --- Mise à jour périodique ---

    def _boucle_interface(self):
        m = self.moteur
        etat = m.etat
        total = m.total
        pct = (100 * m.position / total) if total else 0
        self.barre["value"] = pct
        self.lbl_saisis.config(
            text=f"{L.LBL_CARACTERES_SAISIS} : {m.position} {L.LBL_SUR} {total} ({pct:.0f} %)")
        libelle = ETAT_LIBELLE[etat]
        if etat == Etat.ATTENTE and not texte_est_vide(self._texte()):
            libelle = L.ETAT_PRET
        self.lbl_etat.config(text=f"{L.LBL_ETAT} : {libelle}")
        self.lbl_message.config(text=m.message)
        couleur_etat = (VERT if etat == Etat.TERMINEE
                        else ROUGE if etat in (Etat.ERREUR, Etat.ERREUR_WORD)
                        else ORANGE if etat in (Etat.SUSPENDUE, Etat.PAUSE)
                        else TEXTE)
        self.lbl_etat.config(fg=couleur_etat)
        self.lbl_mode_utilise.config(
            text=f"{L.LBL_MODE_UTILISE} : "
                 f"{L.MODE_HUMAIN if m.mode == MODE_HUMAIN else L.MODE_RAPIDE}")
        reelle = m.vitesse_reelle()
        self.lbl_vitesse_reelle.config(
            text=f"{L.LBL_VITESSE_REELLE} : {reelle:.0f} {L.UNITE_CPS}" if reelle else "")
        self.lbl_vitesse.config(text=str(self.var_vitesse.get()))
        self.lbl_intensite.config(text=str(self.var_intensite.get()))

        maintenant = self.racine.tk.call("clock", "milliseconds")
        if int(maintenant) >= self.prochaine_verif_word:
            self.etat_word = securite.etat_word()
            texte_word = LIBELLE_ETAT_WORD[self.etat_word]
            couleur = (VERT if self.etat_word == securite.ETAT_ACTIF
                       else ORANGE if self.etat_word == securite.ETAT_OUVERT_NON_ACTIF
                       else TEXTE_GRIS)
            self.lbl_word.config(text=texte_word, fg=couleur)
            self.lbl_word_param.config(text=texte_word, fg=couleur)
            self.prochaine_verif_word = int(maintenant) + 500
        self._maj_boutons(etat)
        self.racine.after(100, self._boucle_interface)

    def _maj_boutons(self, etat: Etat):
        actif = etat in (Etat.COMPTE_A_REBOURS, Etat.VERIFICATION, Etat.EN_COURS)
        reprise = etat in (Etat.PAUSE, Etat.SUSPENDUE)
        inactif = not actif and not reprise

        def regler(bouton, active):
            bouton.state(["!disabled"] if active else ["disabled"])

        regler(self.btn_demarrer, inactif)
        regler(self.btn_pause, actif)
        regler(self.btn_reprendre, reprise)
        regler(self.btn_arreter, actif or reprise)
        regler(self.btn_effacer, inactif)
        regler(self.btn_importer, inactif)
        regler(self.btn_import_txt, inactif)
        regler(self.btn_import_docx, inactif)
        regler(self.btn_parametres, inactif)
        regler(self.liste_mode, inactif)
        regler(self.champ_delai, not actif)
        regler(self.chk_arriere, inactif)
        self.zone_texte.config(state="normal" if inactif else "disabled")


def lancer():
    racine = tk.Tk()
    moteur = MoteurSaisie(securite.obtenir_fenetre_active, _envoyeur_windows(),
                          fabrique_arriere_plan=CibleWord)
    Application(racine, moteur)
    if sys.platform == "win32":
        SurveillanceUrgence(moteur).start()
    racine.mainloop()


def _envoyeur_windows():
    if sys.platform == "win32":
        from . import winapi
        return winapi.envoyer_texte

    def indisponible(_):
        raise OSError("Windows requis")
    return indisponible
