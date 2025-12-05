# Présentation du projet Energy4Climate

Ce dépôt contient les ressources et le code développés dans le cadre du hackathon Météo-France. L'objectif principal est d'explorer, analyser et valoriser des données climatiques et énergétiques à travers des outils interactifs et des scripts Python.


## Structure du dépôt

- **data/** : Données sources, catalogues, masques et sorties de modèles climatiques (CMCC, IPSL, etc.)
- **frontend/** : Application web (React + Vite) pour la visualisation interactive des indicateurs climatiques et énergétiques
- **toolkit/** : Package Python (voir `toolkit/README.md`) pour le traitement, le calcul d'indicateurs, l'accès et l'export des données climatiques et énergétiques
	- **src/mf_toolkit/climato/** : Calculs d'indicateurs climatiques et énergétiques
	- **src/mf_toolkit/data/** : Téléchargement, recherche, export de données
	- **src/mf_toolkit/tiling/** : Tuilage et conversion géospatiale (Web Mercator)


## Fonctionnalités principales

- Visualisation interactive des indicateurs climatiques et énergétiques (frontend)
- Calcul d'indicateurs climatiques (température, vent, rayonnement, DJU, risque énergétique, etc.)
- Export des données au format GeoTIFF et tuiles cartographiques (SIG/web)
- Analyse de risque énergétique à partir des données climatiques
- Téléchargement, recherche et gestion des données EURO-CORDEX et DRIAS


## Installation & Utilisation

Merci de vous référer aux fichiers suivants pour les instructions détaillées :

- **toolkit/README.md** : Installation, import, et utilisation du package Python `mf_toolkit`
- **frontend/README.md** : Installation et lancement de l'application web

## Contacts & Contributeurs

Projet réalisé lors du hackathon Météo-France 2025 par l'équipe EnR4Climate.

N'hésitez pas à ouvrir des issues ou proposer des améliorations !
