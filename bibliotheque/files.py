"""
Ce module gère toutes les opérations sur les fichiers pour le système de gestion de bibliothèque. 
Il comprend des fonctions de chargement et d'enregistrement de données dans des fichiers JSON.
"""

import json
from typing import List, Dict


class FileHandler:
    def __init__(self, file_name: str):
        self.file_name = f"database/{file_name}.json"

    def load_data(self) -> List[Dict]:
        """
        Charge les données à partir d'un fichier JSON.

        Returns:
            List[Dict]: Les données chargées.
        """
        data = []
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            # print(f"No file found at {self.file_name}")
            pass
        except json.JSONDecodeError:
            # print(f"Error decoding JSON from {self.file_name}")
            pass

        return data

    def save_data(self, data: List[Dict]) -> None:
        """
        Enregistre les données dans un fichier JSON.

        Args:
            data (List[Dict]): Les données à enregistrer.
            file_name (str): Le nom du fichier où enregistrer les données.
        """
        try:
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False)
        except json.JSONDecodeError:
            # print(f"Error encoding data to JSON at {self.file_name}")
            pass

    def update_data(self, item, key):
        """
        Met à jour un élément dans la base de données.

        Cette méthode charge les données actuelles, trouve l'élément à mettre à jour en utilisant la clé fournie,
        remplace l'ancien élément par le nouveau, et sauvegarde les données mises à jour dans la base de données.

        Args:
            item (dict): Le nouvel élément qui remplacera l'ancien.
            key (str): La clé utilisée pour trouver l'élément dans la base de données. Elle doit être une clé dans le dictionnaire de l'élément.
        """
        items = self.load_data()

        if not items:
            items.append(item)
        else:
            # Find the item in the database
            for i, existing_item in enumerate(items):
                if existing_item[key] == item[key]:
                    # Update the item
                    items[i] = item
                    break
            else:
                items.append(item)

        # Save the changes to the database
        self.save_data(items)


class StudentHandler(FileHandler):
    def __init__(self):
        super().__init__("etudiants")

    def update(self, student):
        super().update_data(student, "id")


class BookHandler(FileHandler):
    def __init__(self):
        super().__init__("books")

    def update(self, book):
        super().update_data(book, "isbn")


class AdminHandler(FileHandler):
    def __init__(self):
        super().__init__("admins")

    # Override the save_data method to prevent writing.
    def save_data(self, data: List[Dict]) -> None:
        raise NotImplementedError("Admin data is read-only.")
