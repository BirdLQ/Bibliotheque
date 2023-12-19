"""
Ce module définit la classe Bibliotheque qui représente une bibliothèque. 
La classe Bibliotheque comprend des méthodes pour l'enregistrement des utilisateurs, 
la connexion des utilisateurs, l'affichage des livres, etc.
"""

from files import BookHandler
from utils import print
import utils
import datetime

class Bibliotheque:
    book_handler = BookHandler()
    livres = book_handler.load_data()

    def afficher_livres(self, user_type="Etudiant", effacer = False) -> list[dict] | None:
        """
        Méthode pour afficher les livres disponibles.

        Returns:
            List[Dict[str, [str | int]]]: Liste des livres disponibles.
        """
        # Si l'utilisateur est un administrateur, tous les livres sont affichés
        if user_type == "Admin":
            livres_disponibles = self.livres
        else:
            # Si l'utilisateur est un étudiant, seuls les livres qui ont un nombre d'exemplaires supérieur à 0 sont affichés
            livres_disponibles = list(
                filter(
                    lambda row: {
                        "id": row["id"],
                        "titre": row["titre"],
                        "auteur": row["auteur"],
                        "isbn": row["isbn"],
                        "emprunter_par": row["emprunter_par"],
                    }
                    if (row["nbr_ex"]) > 0
                    else None,
                    self.livres,
                )
            )

            # Et si aucun livre n'est disponible, affiche un message d'erreur
            if not len(livres_disponibles):
                utils.message([("Aucun livre disponible!", "error")])
                return None

        # Affiche la liste des livres disponibles
        print("La liste des livres :")
        utils.json_to_table(livres_disponibles, effacer)

        return livres_disponibles

    def ajouter_exemplaires(self, isbn, nbr_ex=None) -> bool:
        for livre in self.livres:
            if livre.get("isbn") == isbn:
                if not nbr_ex:
                    print(
                        f"\nLe livre {livre['titre']} est deja dans la bibliotheque.\n"
                    )
                    # Demander combien d'exemplaires faut il ajouter
                    nbr_ex = utils.int_input(
                        "Combien d'exemplaires voulez vous ajouter : "
                    )

                livre["nbr_ex"] += nbr_ex
                self.update_book(livre)

                return nbr_ex

        return False

    def ajouter_livre(self) -> None:
        isbn = input("Entrez l'ISBN du livre : ")

        if nbr_ex := self.ajouter_exemplaires(isbn):
            utils.message([(f"{nbr_ex} exemplaires ajouté(s) avec succés.", "success")])
            return

        # Si l'ISBN saisi ne correspond à aucun livre, demande à l'admin de saisir les informations du nouveau livre
        idLivre = len(self.livres) + 1
        titre = input("Entrez le titre du livre : ")
        auteur = input("Entrez le nom de l'auteur : ")
        editeur = input("Entrez le nom de l'éditeur : ")
        nbr_ex = utils.int_input("Entrez le nombre d'exemplaires : ")
        annee = input("Entrez l'année de publication : ")

        # Création du nouveau livre
        livre = {
            "id": idLivre,
            "titre": titre,
            "auteur": auteur,
            "editeur": editeur,
            "isbn": isbn,
            "nbr_ex": nbr_ex,
            "annee": annee,
            "emprunter_par": [],
        }

        # Ajout du nouveau livre à la liste des livres
        self.livres.append(livre)
        # Sauvegarde de la liste des livres
        self.book_handler.save_data(self.livres)

        utils.message([(f"Le livre {titre} a été ajouté avec succès.", "success")])

    def supprimer_livre(self):
        self.afficher_livres("Admin")
        
        isbn = input("Entrez l'ISBN du livre à supprimer : ")

        # Parcours de la liste des livres
        for i, livre in enumerate(self.livres):
            # Si l'ISBN du livre correspond à l'ISBN saisi
            if livre["isbn"] == isbn:
                utils.message(
                    [(f"Livre {livre['titre']} supprimé avec succès.", "success")]
                )

                # Suppression du livre de la liste des livres
                del self.livres[i]

                # Sauvegarde de la liste des livres
                self.book_handler.save_data(self.livres)
                return

        utils.message([(f"Aucun livre trouvé avec l'ISBN: {isbn}.", "error")])

    def modifier_livre(self):
        self.afficher_livres("Admin")
                
        choix = utils.int_input("Entrez l'id du livre que vous voulez modifier : ")
        utils.clear()
        
        livre = [self.livres[choix - 1]]        
        
        utils.json_to_table(livre, False)
        
        while True:
            attr_a_modifier = utils.input("Quel attribut voulez-vous modifier ?\n->").lower()
            if attr_a_modifier not in livre[0].keys():
                print("Attribut non valide veuilez recommencer.")
            else:
                break
        
        if attr_a_modifier in ["id", "nbr_ex"]:
            nouvelle_val = utils.int_input(f"Entrez la nouvelle valeur de {attr_a_modifier} : ")
        else:
            nouvelle_val = utils.input(f"Entrez la nouvelle valeur de {attr_a_modifier} : ")
        
        livre[0][attr_a_modifier] = nouvelle_val
        
        self.update_book(livre[0])
        
        utils.message([("Attribut modfifier avec succés", "success")])
        

    def retourner_livre(self, livre_rendu) -> None:
        for livre in self.livres:
            if livre.get("isbn") == livre_rendu["isbn"]:
                livre["nbr_ex"] += 1
                livre["emprunter_par"].append(
                    {
                        key: livre_rendu[key]
                        for key in ["login", "nom", "prenom", "date"]
                        if key in livre_rendu
                    }
                )
                livre["emprunter_par"][0].update(
                    {"date_rendu": datetime.date.today().isoformat()}
                )
                self.update_book(livre)
                break

        utils.message([("Livre retourné avec succès.", "success")])
        
    def historique_emprunts(self):
        livres_empruntes = [livre for livre in self.livres if livre['emprunter_par']]
        
        utils.json_to_table(livres_empruntes)

    def regle_7jours(self, etudiant_s) -> list[dict]:
        """
        Méthode pour vérifier la règle des 7 jours.

        Args:
            id_etudiant (Optional[int], optional): ID de l'étudiant. Par défaut None.

        Returns:
            List[Dict[str, str]]: Liste des infractions.
        """
        infractions = []

        # Pour chaque étudiant, vérifie si la date de l'emprunt est supérieure à 7 jours
        for etudiant in etudiant_s:
            for emprunt in etudiant["emprunts"]:
                if (
                    datetime.date.today()
                    - datetime.datetime.strptime(emprunt["date"], "%Y-%m-%d").date()
                ).days > 7:
                    for livre in self.livres:
                        if livre["isbn"] == emprunt["isbn"]:
                            infractions.append(
                                {
                                    "id": etudiant["id"],
                                    "nom": etudiant["nom"],
                                    "prenom": etudiant["prenom"],
                                    "titre": livre["titre"],
                                }
                            )
        return infractions

    def update_book(self, book=None) -> None:
        """
        Met à jour un livre spécifique dans la base de données.

        Args:
            student (dict): Le livre à mettre à jour.
        """
        self.book_handler.update(book)
