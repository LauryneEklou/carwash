# CarWash – Application de gestion de station de lavage

Ce projet est une application de gestion d'une station de lavage automobile. Il permet de suivre les services offerts, les clients, les employés, et les réservations de lavage.

## Fonctionnalités principales

- Enregistrement des clients et de leurs véhicules
- Système de réservation avec créneaux horaires
- Suivi des historiques des lavages
- Interface d’administration pour gérer les employés

## Technologies utilisées

- **Backend** : `Django`
- **Frontend** : `HTML-Tailwind CSS`
- **Base de données** : `SQLITE`

## Comment exécuter le projet
# Cloner le dépôt
git clone https://github.com/LauryneEklou/carwash.git

# Accéder au dossier du projet
cd carwash

# (Optionnel) Créer et activer un environnement virtuel
python -m venv env
source env/bin/activate  # Sur Windows : env\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations (initialiser la base de données SQLite)
python manage.py migrate

# (Optionnel) Créer un superutilisateur pour accéder à l’admin
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver

