import logging
from datetime import date
from io import BytesIO
from typing import Optional
from uuid import UUID

from fastapi import APIRouter,Request, Depends, HTTPException, status, File, UploadFile, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.middleware.keycloak_token_validation import get_current_user
from app.models.enums.Enums import EtatMission
from app.models.ordre_mission import OrdreMission
from app.repositories import ordre_mission_repo,ligne_budgetaire_repo
from app.schemas.historique_validation_schema import HistoriqueValidationCreate
from app.schemas.ordre_mission_schema import OrdreMissionCreate, OrderMissionOut
from app.schemas.validation_data import ValidationData
from app.repositories import historique_validation_repo
from app.services.user_service import get_current_user_token, SimpleUserService
from dependencies import get_db
import magic

router = APIRouter(prefix="/order", tags=["Orders"])

user_service = SimpleUserService()
@router.get("/")
async def get_ordres(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    current_user = get_current_user(request)

    # The roles are directly in current_user, not nested in realm_access
    user_roles = current_user.get("roles", [])  # Changed this line
    allowed_roles = ["CG", "HR", "BPA", "admin"]

    # Check if user has privileged role
    has_privileged_role = any(role in user_roles for role in allowed_roles)

    if has_privileged_role:
        # Get all missions
        orders = await ordre_mission_repo.get_ordres(db)
    else:
        # Get only user's missions
        user_id = current_user.get("id")  # Also changed from "sub" to "id"
        orders = await ordre_mission_repo.get_order_by_userId(db, user_id)

    current_token = get_current_user_token(request)

    return [
        {
            "id": j.id,
            "etat demande": j.etat,
            "Debut": j.dateDebut,
            "Fin": j.dateFin,
            "ligne budgetaire":j.ligne_budgetaire_id,
            "mission": j.mission,
            "financement": j.financement,
            "rapport": j.rapport,
            "user": await user_service.get_user_by_id(j.user_id,current_token),
            "accord de Responsable": f"/file/{j.id}/download"
        } for j in orders
    ]

@router.get("/{order_id}", response_model=OrderMissionOut)
async def get_ordre( order_id: UUID, db: AsyncSession = Depends(get_db)):
    order = await ordre_mission_repo.get_ordre_by_id( db,order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Ordre {order_id} not found")
    return order

@router.post("/add")
async def create_ordre(
    dateDebut: date = Form(...),
    dateFin: date = Form(...),
    mission_id: UUID = Form(...),
    user_id: UUID = Form(...),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    ordre = OrdreMissionCreate(
        dateDebut=dateDebut,
        dateFin=dateFin,
        mission_id=mission_id,
        user_id=user_id,
    )
    file_data = await file.read() if file else None
    return await ordre_mission_repo.create_ordre_with_verification(db, ordre, file_data)

@router.get("/file/{ordre_id}/download")
async def download_file(ordre_id: UUID, db: AsyncSession = Depends(get_db)):
    ordre = await ordre_mission_repo.get_ordre_by_id(db, ordre_id)
    if ordre is None or ordre.accord_respo is None:
        raise HTTPException(status_code=404, detail="File not found")

    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(bytes(ordre.accord_respo))
    extension = file_mime_type.split('/')[-1]

    return StreamingResponse(BytesIO(ordre.accord_respo),
                             media_type=file_mime_type,
                             headers={
                                 "Content-Disposition": f"attachment; filename=ordre_{ordre_id}.{extension}"
                             })

@router.get("/user/{user_id}")
async def get_orders_by_userId(user_id: UUID, db: AsyncSession = Depends(get_db)):
    orders = await ordre_mission_repo.get_order_by_userId(db, user_id)
    if orders is None:
        raise HTTPException(status_code=404, detail="The user has no order yet")
    return [
        {
            "id": j.id,
            "etat demande": j.etat,
            "Debut": j.dateDebut,
            "Fin": j.dateFin,
            "User": j.user_id,
            "mission": j.mission,
            "financement": j.financement,
            "rapport": j.rapport,
            "accord de Responsable": f"/file/{j.id}/download"
        } for j in orders
    ]


@router.put("/update-{ordre_id}", response_model=OrderMissionOut)
async def update_ordre(
    ordre_id: UUID,
    ordre_update: OrdreMissionCreate,
    db: AsyncSession = Depends(get_db)
):
    db_ordre = await ordre_mission_repo.update_ordre_mission(db, ordre_id, ordre_update)
    if db_ordre is None:
        raise HTTPException(status_code=404, detail="Ordre de mission non trouvé")
    return db_ordre

@router.delete("/delete/{ordre_mission_id}", response_model=OrderMissionOut)
async def delete_ordre_mission(
        ordre_mission_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_ordre_mission = await ordre_mission_repo.delete_ordre(db, ordre_mission_id)
    if db_ordre_mission is None:
        raise HTTPException(status_code=404, detail="Ordre de mission non trouvé")

    return db_ordre_mission


@router.api_route("/etat-update/{ordre_mission_id}", methods=["GET", "POST"])
async def update_etat(request: Request, ordre_mission_id: UUID, db: AsyncSession = Depends(get_db),validation_data:Optional[ValidationData]=None):
    method = request.method
    if method == "POST" :
        if validation_data is None:
            raise HTTPException(status_code=403, detail="Please provide Validation Data")


    user_id = request.headers.get("x-user-id")
    user_roles = request.headers.get("x-user-roles", "")

    # Call the business logic function (which can be tested separately)
    try:
        result = await process_etat_update(
            user_id=user_id,
            user_roles=user_roles,
            ordre_mission_id=ordre_mission_id,
            db=db,
            validation_data=validation_data
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur serveur: {str(e)}")



# Updated process_etat_update function
async def process_etat_update(user_id: str, user_roles: str, ordre_mission_id: UUID, db: AsyncSession,
                              validation_data: Optional[ValidationData]):
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non authentifié")

    db_ordre_mission = await ordre_mission_repo.get_ordre_by_id(db, ordre_mission_id)
    if not db_ordre_mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordre de mission non existant")

    # Add logging to debug the current state
    print(f"DEBUG: Current state: {db_ordre_mission.etat}, User roles: {user_roles}")
    print(f"DEBUG: Validation data: {validation_data}")

    # Determine the new state based on current state and user role
    match db_ordre_mission.etat:
        case EtatMission.OUVERTE:
            if str(db_ordre_mission.user_id) == user_id:
                db_ordre_mission.etat = EtatMission.EN_ATTENTE
            else:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Seul le créateur peut soumettre la mission")

        case EtatMission.EN_ATTENTE:
            if "RH" in user_roles:
                db_ordre_mission.etat = EtatMission.VALIDEE_HIERARCHIQUEMENT
            else:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Rôle RH requis pour cette étape")

        case EtatMission.VALIDEE_HIERARCHIQUEMENT:
            if "CG" in user_roles:
                # Handle budget validation
                if not validation_data:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Données de validation budgétaire requises")

                # Validate montant estimé
                if validation_data.montantEstime is None or validation_data.montantEstime <= 0:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                        detail="Montant estimé requis et doit être positif")

                # Update mission order with estimated amount
                db_ordre_mission.montant_alloue = validation_data.montantEstime

                # Handle budget line assignment
                if validation_data.ligneBudgetaireId:
                    # Using existing budget line
                    existing_line = await ligne_budgetaire_repo.get_ligne_budgetaire_by_id(db,
                                                                                           validation_data.ligneBudgetaireId)
                    if not existing_line:
                        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Ligne budgétaire non trouvée")
                    db_ordre_mission.ligne_budgetaire_id = validation_data.ligneBudgetaireId

                elif validation_data.ligneBudgetaire:
                    # Creating new budget line
                    new_line = await ligne_budgetaire_repo.create_ligne_budgetaire(db, validation_data.ligneBudgetaire)
                    db_ordre_mission.ligne_budgetaire_id = new_line.id

                else:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                        detail="Ligne budgétaire ou ID de ligne existante requis")

                db_ordre_mission.etat = EtatMission.VALIDEE_BUDGETAIREMENT
            else:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Rôle CG requis pour validation budgétaire")

        case EtatMission.VALIDEE_BUDGETAIREMENT:
            if "CG" in user_roles:
                db_ordre_mission.etat = EtatMission.APPROUVEE
            else:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Rôle CG requis pour approbation finale")

        # Add explicit cases for other states to avoid the default case
        case EtatMission.APPROUVEE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail="Mission déjà approuvée. Utilisez l'endpoint de rapport.")

        case EtatMission.REFUSEE:
            if "BPA" in user_roles or str(db_ordre_mission.user_id) == user_id:
                db_ordre_mission.etat = EtatMission.OUVERTE
            else:
                raise HTTPException(status.HTTP_403_FORBIDDEN,
                                    detail="Seul le BPA ou le créateur peut rouvrir une mission refusée")

        case EtatMission.CLOTUREE:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail="Mission déjà clôturée. Aucune modification possible.")

        case _:
            # This should help us debug what state is causing the issue
            print(f"ERROR: Unhandled state: {db_ordre_mission.etat} (type: {type(db_ordre_mission.etat)})")
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"État non géré: {db_ordre_mission.etat}. Contactez l'administrateur.")

    # Database operations
    try:
        await db.commit()
        await db.refresh(db_ordre_mission)
        print(f"DEBUG: Database committed successfully. New state: {db_ordre_mission.etat}")
    except Exception as e:
        print(f"ERROR: Database operation failed: {str(e)}")
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur base de données: {str(e)}")

    # Create history record with validation data
    try:
        db_hv = HistoriqueValidationCreate(
            user_id=UUID(user_id),
            role=user_roles,
            ordre_mission_id=ordre_mission_id,
            etat=db_ordre_mission.etat,
        )
        await historique_validation_repo.create_historiqueValidation(db, db_hv)
        print("DEBUG: History record created successfully")
    except Exception as e:
        print(f"ERROR: History creation failed: {str(e)}")
        # Don't fail the whole operation if history fails
        pass

    # Build response carefully to avoid field errors
    try:
        response_data = {
            "id": db_ordre_mission.id,
            "financement": db_ordre_mission.financement,
            "Debut": db_ordre_mission.dateDebut,
            "Fin": db_ordre_mission.dateFin,
            "etat de mission": db_ordre_mission.etat,
            "User": db_ordre_mission.user_id,
            "mission": db_ordre_mission.mission,
            "rapport": db_ordre_mission.rapport if hasattr(db_ordre_mission, 'rapport') else [],
            "accord de Responsable": f"/file/{db_ordre_mission.id}/download",
        }

        # Add optional fields only if they exist
        if hasattr(db_ordre_mission, 'montant_alloue') and db_ordre_mission.montant_alloue is not None:
            response_data["montant_estime"] = db_ordre_mission.montant_alloue

        if hasattr(db_ordre_mission, 'ligne_budgetaire_id') and db_ordre_mission.ligne_budgetaire_id is not None:
            response_data["ligne_budgetaire_id"] = db_ordre_mission.ligne_budgetaire_id

        print(f"DEBUG: Response data prepared: {response_data}")
        return response_data

    except Exception as e:
        print(f"ERROR: Response preparation failed: {str(e)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur préparation réponse: {str(e)}")