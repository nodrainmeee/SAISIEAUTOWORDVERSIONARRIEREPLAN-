"""Accès aux API Windows (ctypes). Ce module ne s'importe que sous Windows."""

import ctypes
import os
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_PAUSE = 0x13
VK_X = 0x58

ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class _UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _UNION)]


user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]


def _classe(hwnd) -> str:
    tampon = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, tampon, 256)
    return tampon.value


def _chemin_processus(pid: int) -> str:
    poignee = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not poignee:
        return ""
    try:
        taille = wintypes.DWORD(1024)
        tampon = ctypes.create_unicode_buffer(1024)
        if kernel32.QueryFullProcessImageNameW(poignee, 0, tampon, ctypes.byref(taille)):
            return tampon.value
        return ""
    finally:
        kernel32.CloseHandle(poignee)


def fenetre_active():
    """Retourne (identifiant, pid, chemin_exe, classe) de la fenêtre active, ou None."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wintypes.DWORD(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None
    return (int(hwnd), int(pid.value), _chemin_processus(pid.value), _classe(hwnd))


def fenetres_word_ouvertes() -> int:
    """Compte les fenêtres principales de Word (classe OpusApp) appartenant à WINWORD.EXE."""
    compteur = [0]

    def rappel(hwnd, _):
        if user32.IsWindowVisible(hwnd) and _classe(hwnd) == "OpusApp":
            pid = wintypes.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            chemin = _chemin_processus(pid.value) if pid.value else ""
            if os.path.basename(chemin).lower() == "winword.exe":
                compteur[0] += 1
        return True

    user32.EnumWindows(WNDENUMPROC(rappel), 0)
    return compteur[0]


def word_installe() -> bool:
    import winreg
    sous_cle = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WINWORD.EXE"
    for racine in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for vue in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(racine, sous_cle, 0, winreg.KEY_READ | vue) as cle:
                    chemin, _ = winreg.QueryValueEx(cle, "")
                    if chemin and os.path.exists(chemin.strip('"')):
                        return True
            except OSError:
                continue
    return False


def touche_enfoncee(vk: int) -> bool:
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


def _entree_clavier(vk=0, scan=0, drapeaux=0) -> INPUT:
    entree = INPUT()
    entree.type = INPUT_KEYBOARD
    entree.u.ki = KEYBDINPUT(vk, scan, drapeaux, 0, 0)
    return entree


def _envoyer(entrees) -> None:
    if not entrees:
        return
    tableau = (INPUT * len(entrees))(*entrees)
    envoyees = user32.SendInput(len(entrees), tableau, ctypes.sizeof(INPUT))
    if envoyees != len(entrees):
        raise OSError("SendInput a échoué")


def envoyer_texte(texte: str) -> None:
    """Envoie du texte Unicode (accents inclus). \\n = Entrée, \\t = Tabulation."""
    segment = []

    def vider():
        if segment:
            donnees = "".join(segment).encode("utf-16-le")
            unites = [int.from_bytes(donnees[i:i + 2], "little") for i in range(0, len(donnees), 2)]
            entrees = []
            for unite in unites:
                entrees.append(_entree_clavier(0, unite, KEYEVENTF_UNICODE))
                entrees.append(_entree_clavier(0, unite, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))
            _envoyer(entrees)
            segment.clear()

    for caractere in texte:
        if caractere in ("\n", "\t"):
            vider()
            vk = VK_RETURN if caractere == "\n" else VK_TAB
            _envoyer([_entree_clavier(vk, 0, 0), _entree_clavier(vk, 0, KEYEVENTF_KEYUP)])
        else:
            segment.append(caractere)
    vider()
