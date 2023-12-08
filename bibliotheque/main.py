"""
Il s'agit du module principal du système de gestion de bibliothèque. 
Il contient la fonction principale qui est le point d'entrée du programme.
Il gère la boucle principale du programme et dirige l'utilisateur vers les fonctions appropriées en fonction de ses entrées.
"""

import utils
from admin import Admin
from etudiant import Etudiant
from utilisateur import Authentification

from rich.traceback import install
install()

def main() -> None:
    utils.clear()
    utils.message([("Bienvenue à la bibliothèque universitaire !", "bold")], False)

    auth = Authentification()

    while True:
        print("Veuillez choisir (1, 2 ou 3):")
        print("1 - Se connecter.\n2 - S'inscrire.\n3 - Quitter.")
        choix = utils.get_input(3)
        utils.clear()

        if choix == 1:
            utilisateur = auth.connexion()
        elif choix == 2:
            utilisateur = auth.inscription()
        else:
            utils.message([("Au revoir !", None)])
            return

        if isinstance(utilisateur, Admin):
            handle_admin(utilisateur)
        elif isinstance(utilisateur, Etudiant):
            handle_etudiant(utilisateur)

def handle_admin(admin: Admin) -> None:
    """
    Fonction pour gérer les actions de l'admin.

    Args:
        attributes (dict): Les attributs de l'admin.
    """
    while True:
        print(
            "Que souhaitez-vous faire :",
            "1 - Gérer les comptes.",
            "2 - Gérer les livres.",
            "3 - Gérer les emprunts.",
            "4 - Verifier la régle des 7 jours.",
            "5 - Quitter l'interface d'admin.",
            sep="\n",
        )
        gestion = utils.get_input(5)
        utils.clear()

        # Gérer les comptes
        if gestion == 1:
            while True:
                print("Que voulez-vous faire ?")
                print(
                    "1 - Afficher les comptes etudiant.",
                    "2 - Creer un compte etudiant.",
                    "3 - Suspendre un compte etudiant.",
                    "4 - Retourner en arriere",
                    sep="\n",
                )

                choix = utils.get_input(4)
                utils.clear()

                if choix == 4:
                    break

                admin.gerer_comptes(choix)

        # Gérer les livres.
        elif gestion == 2:
            while True:
                print(
                    "Que souhaitez-vous faire :",
                    "1 - Ajouter un livre.",
                    "2 - Supprimer un livre.",
                    "3 - Modifier un livre",
                    "4 - Voir la liste des livres",
                    "5 - Retourner en arriere.",
                    sep="\n",
                )
                choix = utils.get_input(5)
                utils.clear()

                if choix == 5:
                    break
                else:
                    admin.gerer_livres(choix)

        # Gérer les emprunts
        elif gestion == 3:
            admin.gerer_emprunts()
        # verifier la regles des 7 jours
        elif gestion == 4:
            admin.regle_7jours()
        else:
            utils.message([("Vous n'êtes plus admin!", "error")])
            return


def handle_etudiant(etudiant: Etudiant) -> None:
    """
    Fonction pour gérer les actions de l'étudiant.

    Args:
        attributes (dict, optional): Les attributs de l'étudiant. Par défaut None.
    """
    while True:
        while True:
            print(
                "Que souhaitez-vous faire :",
                "1 - Emprunter un livre.",
                "2 - Retourner un livre.",
                "3 - Quitter l'interface étudiant.",
                sep="\n",
            )
            student_choice = utils.get_input(3)
            utils.clear()

            if student_choice == 1:
                etudiant.choisir_livre()
            elif student_choice == 2:
                etudiant.retourner_livre()
            else:
                utils.message([("Vous quittez l'interface étudiant.", "error")])
                return

if __name__ == "__main__":
    main()