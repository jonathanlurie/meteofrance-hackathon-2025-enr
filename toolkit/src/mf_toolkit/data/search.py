import os
import logging
from typing import Optional

from itertools import product

from .config import RCM_DIRECTORY_TEMPLATE


def combinations_from_dict(d):
    """
    Transforme un dictionnaire avec des valeurs listes en une liste de dictionnaires avec toutes les combinaisons possibles.
    Exemple : {a: [1,2], b: 3} -> [{a:1, b:3}, {a:2, b:3}]
    """
    keys = list(d.keys())
    values = [v if isinstance(v, list) else [v] for v in d.values()]
    return [dict(zip(keys, combination)) for combination in product(*values)]


def list_files(type: str, root_dir: Optional[str] = None, **params):
    """
    Liste tous les fichiers dans le répertoire spécifié selon le type et le modèle approprié.
    Arguments :
        type (str) : Type de répertoire ('RCM', 'CPCRCM', etc.)
        **params : Paramètres pour les modèles de chemin
    Retourne :
        List[str] : Liste des chemins de fichiers
    """
    if type == "RCM":
        template = RCM_DIRECTORY_TEMPLATE
        if root_dir is not None:
            template = os.path.join(root_dir, template)
    else:
        logging.warning("Type de chemin inconnu")
        return []
    directories = [template % param_set for param_set in combinations_from_dict(params)]
    files = []
    for directory in directories:
        for root_dir, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root_dir, filename))
    return files
