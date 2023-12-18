from dataclasses import dataclass, field
from files import StudentHandler, AdminHandler
from admin import Admin
from etudiant import Etudiant
import utils


@dataclass
class Utilisateur:
    id: int = int()
    nom: str = str()
    prenom: str = str()
    login: str = str()
    mdp: str = str()
    email: str = str()
    suspendu: bool = bool()
    emprunts: list = field(default_factory=list)
    demandes: list = field(default_factory=list)


class Authentification(Utilisateur):
    student_handler: StudentHandler = StudentHandler()
    admin_handler: AdminHandler = AdminHandler()

    def inscription(self, _type="Etudiant") -> "Utilisateur":
        """
        Méthode pour inscrire un utilisateur.

        Returns:
            bool: True si l'inscription a réussi, False sinon.
        """
        # Demande à l'utilisateur de saisir ses informations
        inputs = utils.box_input(
            "Inscription",
            ["Nom", "Prénom", "Créez un mot de passe", "Entrez votre email"],
        )

        # Enregistrement des informations de l'utilisateur
        self.nom = inputs["Nom"].lower()
        self.prenom = inputs["Prénom"].lower()
        self.mdp = inputs["Créez un mot de passe"]
        self.email = inputs["Entrez votre email"]

        # La liste des etudiants dans la base de donnée
        etudiants = self.student_handler.load_data()

        if any(etu["email"] == self.email for etu in etudiants):
            utils.message(
                [("Cet email existe deja\nImpossible de creer le compte.", "error")]
            )
            return None

        self.id = len(etudiants) + 1

        # Création du login de l'utilisateur
        self.login = (self.prenom + self.nom.capitalize() + str(self.id)).replace(" ", "")

        utils.message(
            [
                ("Compte créé avec succès.", "success"),
                (
                    f"Votre login unique est le suivant: {self.login}. Ne le perdez pas !",
                    None,
                ),
            ]
        )

        etudiant = {
            attr: getattr(self, attr) for attr in list(Utilisateur.__annotations__)
        }
        self.student_handler.update(etudiant)

        return Etudiant(etudiant) if _type == "Etudiant" else None

    def connexion(self) -> "Utilisateur":
        """
        Méthode pour connecter un utilisateur.

        Returns:
            bool: True si la connexion a réussi, False sinon.
        """
        # Demande à l'utilisateur de saisir son login et son mot de passe
        inputs = utils.box_input("Connexion", ["Login", "Mot de passe"], [False, True])

        login = inputs["Login"]
        mdp = inputs["Mot de passe"]

        # La liste des admins dans la base de donnée
        admins = self.admin_handler.load_data()

        # Vérifie si l'utilisateur est un administrateur
        for idx, user in enumerate(admins):
            if user["login"] == login and user["mdp"] == mdp:
                utils.message([("Connexion réussie en tant qu'admin.", "success")])
                return Admin(user)

        # La liste des etudiants dans la base de donnée
        etudiants = self.student_handler.load_data()

        # Si l'utilisateur n'est pas un administrateur, vérifie s'il est un étudiant
        for idx, user in enumerate(etudiants):
            if user["login"] == login and user["mdp"] == mdp:
                if user["suspendu"]:
                    utils.message([("Compte suspendu !", "error")])
                    return None

                utils.message([("Connexion réussie en tant qu'etudiant.", "success")])
                return Etudiant(user)

        utils.message([("Identifiant ou mot de passe incorrect!", "error")])
        return None
