"""
Ce module définit la classe Admin qui représente un utilisateur administrateur dans le système de gestion de la bibliothèque. 
La classe Admin comprend des méthodes pour gérer les comptes des étudiants, les livres, les demandes d'emprunt, etc.
"""
from files import StudentHandler
from bibliotheque import Bibliotheque
from utils import print
import utils, datetime


class Admin:
    student_handler: StudentHandler = StudentHandler()
    bibliotheque: Bibliotheque = Bibliotheque()

    def __init__(self, attributs):
        for attr in attributs:
            setattr(self, attr, attributs[attr])

    def gerer_comptes(self, choix: int) -> None:
        """
        Méthode pour gérer les comptes.

        Args:
            choix (int): Le choix de l'admin.
        """
        if choix == 1:
            self.afficher_etudiants(continuer=True)
        elif choix == 2:
            # To avoid circular imports
            from utilisateur import Authentification

            Authentification().inscription("Admin")
        else:
            self.suspendre_etudiant()

    def afficher_etudiants(
        self, status="all", key=None, value=None, continuer=False
    ) -> None | dict:
        
        # Récupération de la liste des étudiants
        etudiants = self.student_handler.load_data()

        # Filtrage des étudiants en fonction du statut spécifié
        if status == "suspendu":
            etudiants = [etudiant for etudiant in etudiants if etudiant["suspendu"]]
        elif status == "non suspendu":
            etudiants = [etudiant for etudiant in etudiants if not etudiant["suspendu"]]

        # Filtrage des données en fonction de la clé et de la valeur spécifiées
        if key and value:
            etudiants = [
                etudiant for etudiant in etudiants if etudiant.get(key) == value
            ]
        elif key:
            etudiants = [etudiant for etudiant in etudiants if etudiant.get(key)]

        # Affichage de la liste des étudiants
        if not utils.json_to_table(etudiants, continuer):
            return None

        return etudiants

    def suspendre_etudiant(self) -> None:
        """
        Méthode pour suspendre un étudiant.
        """
        etudiants = self.afficher_etudiants("non suspendu")

        # Demande à l'admin de saisir l'id de l'étudiant à suspendre
        id_a_suspendre = utils.int_input("Saisissez l'ID de l'élève à suspendre : ")

        # Parcours de la liste des étudiants
        for etudiant in etudiants:
            # Si l'id de l'étudiant correspond à l'id à suspendre
            if etudiant.get("id") == id_a_suspendre:
                # Suspension de l'étudiant
                etudiant["suspendu"] = True
                self.student_handler.update(etudiant)
                utils.message([("Compte suspendu avec succes.", "success")])
                break
        else:
            utils.message(
                [("Aucun étudiant n'a été trouvé avec l'identifiant donné.", "error")]
            )

    def gerer_emprunts(self) -> None:
        """
        Méthode pour gérer les demandes d'emprunt.
        """
        etudiants = self.afficher_etudiants("non suspendu", "demandes")

        if not etudiants:
            return

        id_etudiant = utils.int_input(
            "Entrez l'ID de l'étudiant dont vous voulez traiter la demande : "
        )
        utils.clear()

        for etudiant in etudiants:
            if etudiant["id"] == id_etudiant:
                # Afficher toutes les demandes de l'étudiant choisi
                utils.json_to_table(etudiant["demandes"], False)

                print("Entrez le numero de la demande que vous voulez traiter : ")
                id_demande = utils.get_input(len(etudiant["demandes"]))

                while True:
                    print(
                        "Que souhaitez-vous faire :",
                        "1 - Accepter la demande.",
                        "2 - Refuser la demande.",
                        "3 - Retourner en arrière.",
                        sep="\n",
                    )
                    choix = utils.get_input(3)
                    utils.clear()

                    if choix == 1:
                        self.accepter_demande(etudiant, id_demande)
                    elif choix == 2:
                        self.refuser_demande(etudiant, id_demande)
                    else:
                        return
                break

    def accepter_demande(self, etudiant, num_demande):
        """
        Méthode pour accepter une demande d'emprunt.

        Args:
            id_etudiant (int): L'étudiant dont la demande doit être acceptée.
            num_demande (int): Numero de la demande à accepter.
        """
        livre = etudiant["demandes"].pop(num_demande - 1)
        livre["date"] = datetime.date.today().isoformat()
        etudiant["emprunts"].append(livre)

        self.bibliotheque.ajouter_exemplaires(livre["isbn"], -1)

        self.student_handler.update(etudiant)

        utils.message([("La demande d'emprunt a été acceptée avec succés.", "success")])

    def refuser_demande(self, etudiant, num_demande):
        """
        Méthode pour refuser une demande d'emprunt.

        Args:
            id_etudiant (int): L'étudiant dont la demande doit être refusée.
            num_demande (int): Numero de la demande à refuser.
        """
        # Supprime la demande de la liste des demandes
        etudiant["demandes"].pop(
            num_demande - 1
        )

        self.student_handler.update(etudiant)

        utils.message([("La demande d'emprunt a été refusée avec succés.", "success")])

    def gerer_livres(self, choix: int) -> None:
        """
        Méthode pour gérer les livres.

        Args:
            choix (int): Le choix de l'admin.
        """
        if choix == 1:
            self.bibliotheque.ajouter_livre()
        elif choix == 2:
            self.bibliotheque.supprimer_livre()
        elif choix == 3:
            self.bibliotheque.modifier_livre()
        elif choix == 4:
            self.bibliotheque.afficher_livres("Admin", True)

    def regle_7jours(self) -> None:
        # Appel de la méthode regle_7jours de Bibliotheque
        infractions = self.bibliotheque.regle_7jours(self.student_handler.load_data())

        # Si des infractions ont été trouvées, affiche les infractions
        if infractions:
            utils.json_to_table(infractions)
        else:
            print("Tous les etudiants respectent la regle des 7 jours.")

        utils.clear(True)
