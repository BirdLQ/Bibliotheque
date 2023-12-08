"""
Ce module contient des fonctions utilitaires pour le système de gestion de bibliothèque. 
Il comprend des fonctions permettant de gérer les entrées de l'utilisateur, 
d'effacer la console, d'afficher les données sous forme de tableau, etc.
"""

import subprocess, platform, builtins
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
from pynput import keyboard
import re

custom_theme = Theme(
    {"error": "bold red", "success": "bold green", "repr.number": "dim"}
)
console = Console(theme=custom_theme)


def print(prompt, *args, **kwargs):
    """
    Fonction pour afficher un message et des arguments supplémentaires en utilisant console.

    Args:
        prompt (str): Le message à imprimer.
        *args: Arguments supplémentaires à imprimer.
        **kwargs: Arguments de mots-clés supplémentaires à passer à la console.
    """
    console.print(prompt, *args, **kwargs)


def input(prompt: str = "") -> str:
    """
    Fonction pour obtenir une entrée de l'utilisateur.

    Args:
        prompt (str): Le message à afficher à l'utilisateur.

    Returns:
        str: L'entrée de l'utilisateur.
    """
    user_input = builtins.input(prompt).strip()
    while not user_input:
        print("Entrée vide. Veuillez réessayer.", style="error")
        user_input = builtins.input(prompt).strip()
    return user_input


def int_input(prompt: str) -> int:
    """
    Fonction pour obtenir une entrée "int" de l'utilisateur.

    Args:
        prompt (str): Le message à afficher à l'utilisateur.

    Returns:
        int: L'entrée "int" de l'utilisateur.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Entrée invalide. Veuillez saisir un nombre entier.", style="error")


def get_input(x: int) -> int:
    """
    Fonction pour obtenir une entrée entière de l'utilisateur dans une plage spécifique.

    Args:
        x (int): La limite supérieure de la plage.

    Returns:
        int: L'entrée entière de l'utilisateur.
    """
    while True:
        choix = int_input("\n-> Votre choix: ")
        if choix < 1 or choix > x:
            print(
                f"L'entrée n'est pas dans la plage valide: {list(range(1,x+1))}. Veuillez réessayer.",
                style="error",
            )
        else:
            return choix


def is_valid_email(email):
    regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$"
    if re.search(regex, email):
        return True
    else:
        return False


def clear(validation: bool = False) -> None:
    """
    Fonction pour effacer la console.

    Args:
        validation (bool, optional): Si True, demande une confirmation à l'utilisateur avant d'effacer. Par défaut False.
    """
    if validation:
        builtins.input("\nAppuyez sur ENTRER pour continuer...")
    if platform.system() == "Windows":
        subprocess.Popen("cls", shell=True).communicate()
    else:  # Linux && MacOS
        print("\033c", end="")


def json_to_table(data: list[dict], effacer: bool = True) -> bool:
    """
    Fonction pour afficher des données JSON sous forme de tableau.

    Args:
        data (List[Dict]): Les données à afficher.
        effacer (bool, optional): Si True, efface la console après l'affichage. Par défaut True.
    """
    if len(data):
        cols = data[0].keys()
    else:
        print("Aucune donnée à afficher!", style="error")
        clear(True)
        return False

    table = Table(
        box=box.SQUARE_DOUBLE_HEAD, header_style="bold reverse", show_lines=True
    )
    for col in cols:
        table.add_column(col)

    for row in data:
        table.add_row(*[str(row[col]) for col in cols])

    print(table)

    if effacer:
        clear(True)

    return True


def message(prompts, validation=True):
    """
    Fonction pour imprimer un titre, un sous-titre, une invite et des arguments supplémentaires en utilisant une boîte.

    Args:
        prompts (list): Une liste de tuples où chaque tuple contient une partie de l'invite et son style.
    """
    clear()

    box_content = Text()
    for i, (prompt, style) in enumerate(prompts):
        box_content.append(prompt, style=style)
        if i < len(prompts) - 1:  # Don't add newline after the last element
            box_content.append("\n")

    panel = Panel(box_content)
    aligned_panel = Align.center(panel)

    print(aligned_panel)

    if validation:
        clear(True)


class InputBox:
    def __init__(self, titre, elements, mask=None):
        self.keys = ""  # Stocke les touches pressées par l'utilisateur
        self.titre = Text(titre, style="reverse")  # Titre de la boîte de saisie
        self.subtitle = ""  # Sous-titre de la boîte de saisie
        self.elements = elements  # Éléments à afficher dans la boîte de saisie
        self.idx_element = -1  # Index de l'élément actuellement sélectionné
        self.inputs = {
            element: "" for element in elements
        }  # Dictionnaire pour stocker les entrées de l'utilisateur
        self.max_len = len(
            max(self.elements, key=len)
        )  # Longueur maximale des éléments
        self.caps = 0  # Variable pour gérer la touche Caps Lock
        self.mask = mask if mask else [False] * len(elements)

    # Méthode appelée lorsqu'une touche est pressée
    def on_press(self, key):
        # Si la touche Backspace est pressée, supprime le dernier caractère
        if key == keyboard.Key.backspace and len(self.keys) > 0:
            self.keys = self.keys[:-1]
        # Si moins de 20 caractères ont été saisis, ajoute le caractère à la chaîne de touches
        elif len(self.keys) < 20:
            try:
                # Si la touche est un chiffre du pavé numérique, ajoute le chiffre à la chaîne de touches
                if hasattr(key, "vk") and 96 <= key.vk <= 105:
                    self.keys += str(key.vk - 96)
                else:
                    # Sinon, ajoute le caractère à la chaîne de touches
                    k = key.char
                    self.keys += k.upper() if self.caps % 2 != 0 else k.lower()
            except (AttributeError, TypeError):
                # Si la touche Caps Lock est pressée, incrémente la variable caps
                if key == keyboard.Key.caps_lock:
                    self.caps += 1
        # Dessine la boîte de saisie
        self.draw_box()

    # Méthode appelée lorsqu'une touche est relâchée
    def on_release(self, key):
        self.subtitle = ""
        # Si la touche Entrée est pressée
        if key == keyboard.Key.enter:
            # Si aucun élément n'est actuellement sélectionné, sélectionne le premier élément
            if self.idx_element == -1:
                self.idx_element += 1
            # Si la chaîne de touches est vide, affiche un message d'erreur
            elif self.keys == "":
                self.subtitle = Text("L'entrée ne peut pas être vide.", style="error")
            # Sinon, ajoute la chaîne de touches à l'élément actuellement sélectionné
            else:
                self.subtitle = ""
                self.inputs[self.elements[self.idx_element]] = self.keys
                self.keys = ""
                self.idx_element += 1
                # Si tous les éléments ont été remplis, quitte la boucle
                if self.idx_element >= len(self.elements):
                    clear()
                    return False
        # Dessine la boîte de saisie
        self.draw_box()

    # Méthode pour dessiner la boîte de saisie
    def draw_box(self):
        box_content = self.box_content()

        # Si la chaîne de touches contient 20 caractères, affiche un message d'erreur
        if len(self.keys) == 20:
            self.subtitle = Text("Vous avez atteint la limite.", style="error")

        # Crée un panneau avec le contenu de la boîte
        panel = Panel(box_content, title=self.titre, subtitle=self.subtitle)
        aligned_panel = Align.center(panel, vertical="middle")
        clear()
        print(aligned_panel)

    # Méthode pour créer le contenu de la boîte de saisie
    def box_content(self):
        box_content = []
        for i, element in enumerate(self.elements):
            if i < self.idx_element:
                box_content.append(
                    f"{element.rjust(self.max_len)} : {self.inputs[element]}"
                )
            elif i == self.idx_element:
                if self.mask[i]:
                    box_content.append(
                        f"{element.rjust(self.max_len)} : {'*' * len(self.keys):21}"
                    )
                else:
                    box_content.append(
                        f"{element.rjust(self.max_len)} : {self.keys:21}"
                    )
            else:
                box_content.append(f"{element.rjust(self.max_len)} : ")
        return "\n".join(box_content)


# Fonction pour créer une boîte de saisie et récupérer les entrées de l'utilisateur
def box_input(titre: str, elements: list, mask: list = None) -> dict:
    logger = InputBox(titre, elements, mask)
    with keyboard.Listener(
        on_press=logger.on_press, on_release=logger.on_release, suppress=True
    ) as listener:
        listener.join()

    listener.stop()

    return logger.inputs
