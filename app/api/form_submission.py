import json
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request

from app.middleware.keycloak_token_validation import get_current_user
from app.schemas.data_form import DataForm
from app.schemas.financement_schema import FinancementCreate
from app.schemas.hebergement_schema import HebergementCreate
from app.schemas.mission_schema import MissionCreate
from app.schemas.ordre_mission_schema import OrdreMissionCreate
from app.schemas.voyage_schema import VoyageCreate
from dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import mission_repo, ordre_mission_repo, voyage_repo, financement_repo, hebergement_repo
import logging
import traceback

router = APIRouter(prefix="/form_submission", tags=["form_submission"])

logger = logging.getLogger(__name__)


@router.post("/")
async def form_submission(
        request: Request,
        data: str = Form(...),
        file: UploadFile = File(None),
        db: AsyncSession = Depends(get_db),
):
    logger.info("=== FORM SUBMISSION STARTED ===")

    try:
        # 1. Check user authentication
        logger.info("Checking user authentication...")
        user_id = request.headers.get("X-User-ID")
        logger.info(f"X-User-ID header: {user_id}")

        if not user_id:
            logger.error("No X-User-ID header found")
            raise HTTPException(status_code=401, detail="User not authenticated")

        # 2. Log request details
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Data received: {data[:200]}...")  # First 200 chars
        logger.info(f"File received: {file.filename if file else 'None'}")

        # 3. Parse JSON data
        logger.info("Parsing JSON data...")
        try:
            form_data_dict = json.loads(data)
            logger.info("JSON parsing successful")
            logger.debug(f"Parsed data keys: {list(form_data_dict.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Raw data: {data}")
            raise HTTPException(status_code=400, detail="Invalid JSON data")

        # 4. Create DataForm model
        logger.info("Creating DataForm model...")
        try:
            form_data = DataForm(**form_data_dict)
            logger.info("DataForm model created successfully")
        except Exception as e:
            logger.error(f"DataForm validation error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Form data dict: {form_data_dict}")
            raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

        # 5. Validate required steps
        logger.info("Validating required steps...")
        validation_errors = validate_required_steps(form_data)
        if validation_errors:
            logger.error(f"Validation errors: {validation_errors}")
            raise HTTPException(status_code=400, detail=validation_errors)

        # 6. Process file
        logger.info("Processing file...")
        file_data = None
        if file:
            try:
                file_data = await file.read()
                logger.info(f"File read successfully, size: {len(file_data)} bytes")
            except Exception as e:
                logger.error(f"Error reading file: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

        # 7. Create Mission
        logger.info("Creating mission...")
        if form_data.mission_details.missionId:
            logger.info(f"Using existing mission ID: {form_data.mission_details.missionId}")

            # Fetch existing mission from database
            existing_mission = await mission_repo.get_mission_by_id(db, mission_id=UUID(form_data.mission_details.missionId))
            if not existing_mission:
                raise HTTPException(status_code=404, detail="Existing mission not found")

            # Use existing mission data
            db_mission = existing_mission
            logger.info(f"Using existing mission with ID: {db_mission.id}")
        else :
            try:
                mission_create = MissionCreate(**form_data.mission_details.dict(exclude={'missionId'}))
                db_mission = await mission_repo.create_mission(db, mission_create)
                logger.info(f"New mission created with ID: {db_mission.id}")
            except Exception as e:
                logger.error(f"Error creating mission: {str(e)}")
                logger.error(f"Error type: {type(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error creating mission: {str(e)}")

        # 8. Create Order Mission
        logger.info("Creating order mission...")
        try:
            order_data = form_data.order_details.dict()
            order_data['mission_id'] = db_mission.id
            order_data['user_id'] = user_id
            logger.debug(f"Order data: {order_data}")

            ordre_mission_create = OrdreMissionCreate(**order_data)
            logger.info("OrdreMissionCreate model created")

            db_ordre_result = await ordre_mission_repo.create_ordre_with_verification(
                db, ordre_mission_create, file_data
            )
            logger.info("Order mission creation completed")

            # Check if there was an error with old missions
            if isinstance(db_ordre_result, dict) and "error" in db_ordre_result:
                logger.error(f"Order creation error: {db_ordre_result}")
                raise HTTPException(status_code=400, detail=db_ordre_result["message"])

            db_ordre_mission = db_ordre_result
            logger.info(f"Order mission created with ID: {db_ordre_mission.id}")

        except HTTPException:
            # Re-raise HTTP exceptions as they are already handled
            raise
        except Exception as e:
            logger.error(f"Error creating order mission: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error creating order mission: {str(e)}")

        # 9. Create Travel if included
        if form_data.order_details.includeTravel and form_data.travel_details:
            logger.info("Creating travel details...")
            try:
                travel_data = form_data.travel_details.dict()
                travel_data['ordre_mission_id'] = db_ordre_mission.id
                logger.debug(f"Travel data: {travel_data}")

                voyage_create = VoyageCreate(**travel_data)
                await voyage_repo.create_voyage(db, voyage_create)
                logger.info("Travel details created successfully")
            except Exception as e:
                logger.error(f"Error creating travel: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error creating travel: {str(e)}")

        # 10. Create Accommodation if included
        if form_data.order_details.includeAccommodation and form_data.accommodation_details:
            logger.info("Creating accommodation details...")
            try:
                accommodation_data = form_data.accommodation_details.dict()
                accommodation_data['ordre_mission_id'] = db_ordre_mission.id
                logger.debug(f"Accommodation data: {accommodation_data}")

                hebergement_create = HebergementCreate(**accommodation_data)
                await hebergement_repo.create_hebergement(db, hebergement_create)
                logger.info("Accommodation details created successfully")
            except Exception as e:
                logger.error(f"Error creating accommodation: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error creating accommodation: {str(e)}")

        # 11. Create Financing if included
        if form_data.order_details.includeFinancing and form_data.financing_details:
            logger.info("Creating financing details...")
            try:
                financing_data = form_data.financing_details.dict()
                financing_data['ordre_mission_id'] = db_ordre_mission.id
                logger.debug(f"Financing data: {financing_data}")

                financement_create = FinancementCreate(**financing_data)
                await financement_repo.create_financement(db, financement_create)
                logger.info("Financing details created successfully")
            except Exception as e:
                logger.error(f"Error creating financing: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error creating financing: {str(e)}")

        logger.info("=== FORM SUBMISSION COMPLETED SUCCESSFULLY ===")
        return {
            "success": True,
            "mission_id": str(db_mission.id),
            "ordre_mission_id": str(db_ordre_mission.id),
            "message": "Mission and order created successfully",
            "data": form_data_dict  # Add the original step-based data

        }

    except HTTPException:
        # Re-raise HTTP exceptions (they have proper status codes)
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        logger.error(f"UNEXPECTED ERROR: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def validate_required_steps(form_data: DataForm) -> list:
    """Validate that required steps are present when included"""
    errors = []

    if form_data.order_details.includeTravel and not form_data.travel_details:
        errors.append("Travel details are required when travel is included")

    if form_data.order_details.includeAccommodation and not form_data.accommodation_details:
        errors.append("Accommodation details are required when accommodation is included")

    if form_data.order_details.includeFinancing and not form_data.financing_details:
        errors.append("Financing details are required when financing is included")

    return errors