import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config.create_tables import create_tables
from app.api.mission_controller import router as mission_router
from app.api.ordre_controller import router as order_router
from app.api.rapport_controller import router as rapport_router
from app.api.financement_controller import router as financement_router
from app.api.justificatif_controller import router as justificatif_router
from app.api.hebergement_controller import router as hebergement_router
from app.api.ligne_budgetaire_controller import router as ligne_budgetaire_router
from app.api.remboursement_controller import router as remboursement_router
from app.api.voyage_controller import router as voyage_router
from app.api.historique_validation_controller import router as historique_validation_router
from app.api.form_submission import router as submission_router
from app.middleware.jwt_check import VerifyInternalJWTMiddleware
from app.middleware.keycloak_token_validation import SimpleKeycloakAuthMiddleware, get_current_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000/', 'http://localhost:3000']
)
# app.add_middleware(SimpleKeycloakAuthMiddleware)

#app.add_middleware(VerifyInternalJWTMiddleware)

routers = [submission_router, mission_router, order_router, rapport_router, financement_router, justificatif_router,
           hebergement_router, ligne_budgetaire_router,remboursement_router, voyage_router, historique_validation_router]

for router in routers:
    app.include_router(router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/profile")
async def get_profile(request: Request):
    """Get user profile - requires authentication"""
    user = get_current_user(request)

    return {
        "message": f"Hello {user['username']}!",
        "user_info": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "roles": user["roles"]
        }
    }


# STEP 4: Your endpoints can now use the new authentication


@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.post("/home")
async def root():
    return {"message": "Hello World"}





