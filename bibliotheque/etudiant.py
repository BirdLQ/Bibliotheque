"""
Ce module définit la classe Etudiant qui représente un utilisateur étudiant dans le système de gestion de la bibliothèque. 
La classe Etudiant comprend des méthodes pour emprunter des livres, les rendre, etc.
"""
from bibliotheque import Bibliotheque
from files import StudentHandler
from utils import print
import utils


class Etudiant:
    bibliotheque = Bibliotheque()
    student_handler: StudentHandler = StudentHandler()

    def __init__(self, attributs):
        for attr in attributs:
            setattr(self, attr, attributs[attr])

        self.update_student()

    def choisir_livre(self) -> None:
        """
        Méthode pour choisir un livre à emprunter.
        """
        # Si l'étudiant a déjà emprunté 3 livres, affiche un message d'erreur
        if len(self.emprunts) >= 3:
            utils.message([("Vous avez déjà emprunté 3 livres!", "error")])
            return
        # Si l'étudiant a emprunté un livre depuis plus de 7 jours, affiche un message d'erreur
        if self.regle_7jours():
            utils.message([("Vous avez emprunter un livre plus de 7 jours.", "error")])
            return

        # Affiche les livres disponibles
        livres_disponibles = self.bibliotheque.afficher_livres()

        if not livres_disponibles:
            return

        # Récupération de la liste des ids des livres disponibles
        ids = [livre["id"] for livre in livres_disponibles]

        # Vérfier l'entrée de l'utilisateur
        while True:
            choix = utils.int_input(
                "Entrez l'ID du livre que vous souhaitez emprunter : "
            )
            if choix in ids:
                self.demande_emprunt_livre(livres_disponibles[choix - 1])
                return
            else:
                print("Veuillez entrez un ID valide.")

    def demande_emprunt_livre(self, livre: list) -> None:
        """
        Méthode pour faire une demande d'emprunt d'un livre.

        Args:
            livre_id (int): ID du livre à emprunter.
        """
        self.demandes.append({"titre": livre["titre"], "isbn": livre["isbn"]})

        self.update_student()

        utils.message(
            [("Votre demande d'emprunts a été envoyé avec succès.", "success")]
        )

    def retourner_livre(self) -> None:
        """
        Méthode pour retourner un livre.
        """
        livres_a_rendre = []

        # Si l'étudiant n'a pas emprunté de livres, affiche un message d'erreur
        if not len(self.emprunts):
            utils.message([("Vous n'avez pas emprunté de livres.", "error")])
            return

        print("Livre(s) que vous avez emprunter:")

        for i, emprunt in enumerate(self.emprunts):
            livres_a_rendre.append(
                {"Num": i + 1, "titre": emprunt["titre"], "isbn": emprunt["isbn"]}
            )

        utils.json_to_table(livres_a_rendre, False)

        print("Entrez le numéro du livre que vous souhaitez rendre: ")
        choix = utils.get_input(len(self.emprunts)) - 1

        livre_a_rendre = self.emprunts.pop(choix)

        livre_a_rendre.update(
            {"login": self.login, "nom": self.nom, "prenom": self.prenom}
        )

        self.bibliotheque.retourner_livre(livre_a_rendre)

        self.update_student()

    def regle_7jours(self) -> bool:
        """
        Méthode pour vérifier la règle des 7 jours.

        Returns:
            bool: False si la règle des 7 jours est respectée, True sinon.
        """
        # Appel de la méthode regle_7jours de la classe Bibliotheque avec l'id de l'étudiant
        # Si des infractions ont été trouvées, renvoie True, sinon renvoie False
        return bool(self.bibliotheque.regle_7jours([self.to_dict()]))

    def update_student(self, student=None) -> None:
        """
        Met à jour un étudiant spécifique dans la base de données.

        Args:
            student (dict): L'étudiant à mettre à jour.
        """
        if not student:
            student = self.to_dict()

        self.student_handler.update(student)

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in vars(self)}
