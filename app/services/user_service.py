# user_service_simple.py - Créez ce fichier dans vos microservices

import os
import httpx
import logging
from fastapi import HTTPException
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class SimpleUserService:
    """
    Service simple pour récupérer les données utilisateurs
    """

    def __init__(self):
        self.gateway_url = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

    async def get_user_by_id(self, user_id: str, current_user_token: str) -> Optional[Dict]:
        """
        Récupérer un utilisateur par son ID

        Args:
            user_id: ID Keycloak de l'utilisateur
            current_user_token: Token de l'utilisateur actuel

        Returns:
            Dict avec les informations utilisateur ou None si non trouvé
        """

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.gateway_url}/users/{user_id}",
                    headers={"Authorization": f"Bearer {current_user_token}"}
                )

                if response.status_code == 404:
                    logger.debug(f"Utilisateur {user_id} non trouvé")
                    return None

                if response.status_code == 403:
                    logger.warning(f"Accès refusé pour l'utilisateur {user_id}")
                    return None

                if response.status_code != 200:
                    logger.error(f"Erreur {response.status_code} pour utilisateur {user_id}")
                    return None

                user_data = response.json()
                logger.debug(f"✅ Utilisateur {user_id} récupéré")
                return user_data

        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur {user_id}: {str(e)}")
            return None

    async def get_user_name(self, user_id: str, current_user_token: str) -> str:
        """
        Récupérer juste le nom d'un utilisateur

        Returns:
            Nom complet ou "Utilisateur inconnu"
        """

        user_data = await self.get_user_by_id(user_id, current_user_token)

        if not user_data:
            return "Utilisateur inconnu"

        full_name = user_data.get("full_name", "")
        if full_name:
            return full_name

        return user_data.get("username", "Utilisateur inconnu")


# Helper pour extraire le token
def get_current_user_token(request) -> str:
    """
    Extraire le token de l'utilisateur actuel
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    raise HTTPException(status_code=401, detail="No token available")