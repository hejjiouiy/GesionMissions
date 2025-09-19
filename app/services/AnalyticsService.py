from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract, and_, or_, select, join, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import calendar
import logging

from app.models.Mission import Mission
from app.models.ordre_mission import OrdreMission
from app.models.enums.Enums import TypeMission, EtatMission

logger = logging.getLogger(__name__)


class AnalyticsServiceError(Exception):
    """Custom exception for Analytics Service errors"""
    pass


class AnalyticsService:

    def __init__(self, db: AsyncSession):
        if not db:
            raise AnalyticsServiceError("Database session is required but was None")
        self.db = db

    async def _validate_database_connection(self):
        """Validate that database connection is working"""
        try:
            result = await self.db.execute(text("SELECT 1"))
            return result.scalar()
        except Exception as e:
            raise AnalyticsServiceError(f"Database connection failed: {str(e)}")

    async def _validate_models(self):
        """Validate that required models are accessible"""
        try:
            mission_test = await self.db.execute(select(Mission).limit(1))
            ordre_test = await self.db.execute(select(OrdreMission).limit(1))
            logger.info("Models validated successfully")
        except Exception as e:
            raise AnalyticsServiceError(f"Cannot access required models: {str(e)}")

    async def get_missions_by_type(self) -> Dict[str, Any]:
        """Get missions count grouped by type"""
        try:
            logger.info("Starting get_missions_by_type query")
            await self._validate_models()

            query = select(
                Mission.type,
                func.count(Mission.id).label('count')
            ).select_from(
                join(Mission, OrdreMission, Mission.id == OrdreMission.mission_id)
            ).group_by(Mission.type)

            result = await self.db.execute(query)
            query_results = result.fetchall()

            if not query_results:
                logger.warning("No missions found in database")
                return {
                    'labels': ['Aucune donnée'],
                    'datasets': [{
                        'label': 'Nombre de missions',
                        'data': [0],
                        'backgroundColor': ['rgba(128, 128, 128, 0.7)'],
                        'borderColor': ['rgba(128, 128, 128, 1)'],
                        'borderWidth': 1
                    }]
                }

            # Convert enum values to display names
            type_labels = {
                TypeMission.NATIONALE: 'Nationale',
                TypeMission.INTERNATIONALE: 'Internationale',
            }

            labels = []
            data = []

            for row in query_results:
                mission_type = row.type
                count = row.count
                if mission_type is not None:
                    labels.append(type_labels.get(mission_type, str(mission_type)))
                    data.append(int(count) if count else 0)

            if not labels:
                return {
                    'labels': ['Aucune donnée'],
                    'datasets': [{
                        'label': 'Nombre de missions',
                        'data': [0],
                        'backgroundColor': ['rgba(128, 128, 128, 0.7)'],
                        'borderColor': ['rgba(128, 128, 128, 1)'],
                        'borderWidth': 1
                    }]
                }

            logger.info(f"Successfully retrieved {len(labels)} mission types")

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Nombre de missions',
                        'data': data,
                        'backgroundColor': [
                            'rgba(0, 84, 63, 0.7)',
                            'rgba(0, 216, 113, 0.7)',
                            'rgba(90, 126, 118, 0.7)',
                            'rgba(245, 242, 237, 0.7)'
                        ][:len(data)],
                        'borderColor': [
                            'rgba(0, 84, 63, 1)',
                            'rgba(0, 216, 113, 1)',
                            'rgba(90, 126, 118, 1)',
                            'rgba(245, 242, 237, 1)'
                        ][:len(data)],
                        'borderWidth': 1
                    }
                ]
            }

        except Exception as e:
            error_msg = f"Error in get_missions_by_type: {str(e)}"
            logger.error(error_msg)
            raise AnalyticsServiceError(error_msg)

    async def get_budget_by_destination(self) -> Dict[str, Any]:
        """Get total budget grouped by destination"""
        try:
            logger.info("Starting get_budget_by_destination query")
            await self._validate_models()

            query = select(
                func.concat(Mission.ville, ', ', Mission.pays).label('destination'),
                func.sum(Mission.budgetPrevu).label('total_budget')
            ).select_from(
                join(Mission, OrdreMission, Mission.id == OrdreMission.mission_id)
            ).where(and_(
                Mission.ville.isnot(None),
                Mission.pays.isnot(None),
                Mission.budgetPrevu.isnot(None)
            )).group_by(Mission.ville, Mission.pays).order_by(
                func.sum(Mission.budgetPrevu).desc()
            ).limit(10)

            result = await self.db.execute(query)
            query_results = result.fetchall()

            labels = []
            data = []

            for row in query_results:
                destination = row.destination
                budget = row.total_budget
                if destination and budget is not None:
                    labels.append(str(destination))
                    data.append(float(budget))

            if not labels:
                return {
                    'labels': ['Aucune donnée'],
                    'datasets': [{
                        'label': 'Budget (MAD)',
                        'data': [0],
                        'backgroundColor': 'rgba(128, 128, 128, 0.5)',
                        'borderColor': 'rgba(128, 128, 128, 1)',
                        'borderWidth': 1
                    }]
                }

            logger.info(f"Successfully retrieved budget data for {len(labels)} destinations")

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Budget (MAD)',
                        'data': data,
                        'backgroundColor': 'rgba(0, 84, 63, 0.5)',
                        'borderColor': 'rgba(0, 84, 63, 1)',
                        'borderWidth': 1
                    }
                ]
            }

        except Exception as e:
            error_msg = f"Error in get_budget_by_destination: {str(e)}"
            logger.error(error_msg)
            raise AnalyticsServiceError(error_msg)

    async def get_missions_by_month(self) -> Dict[str, Any]:
        """Get missions count by month for current and previous year"""
        try:
            logger.info("Starting get_missions_by_month query")
            await self._validate_models()

            current_year = datetime.now().year
            previous_year = current_year - 1

            # Current year query
            current_year_query = select(
                extract('month', OrdreMission.dateDebut).label('month'),
                func.count(OrdreMission.id).label('count')
            ).where(and_(
                extract('year', OrdreMission.dateDebut) == current_year,
                OrdreMission.dateDebut.isnot(None)
            )).group_by(extract('month', OrdreMission.dateDebut))

            current_year_result = await self.db.execute(current_year_query)
            current_year_data_raw = current_year_result.fetchall()

            # Previous year query
            previous_year_query = select(
                extract('month', OrdreMission.dateDebut).label('month'),
                func.count(OrdreMission.id).label('count')
            ).where(and_(
                extract('year', OrdreMission.dateDebut) == previous_year,
                OrdreMission.dateDebut.isnot(None)
            )).group_by(extract('month', OrdreMission.dateDebut))

            previous_year_result = await self.db.execute(previous_year_query)
            previous_year_data_raw = previous_year_result.fetchall()

            # Initialize arrays with 12 months
            current_year_data = [0] * 12
            previous_year_data = [0] * 12

            # Fill current year data
            for row in current_year_data_raw:
                month = row.month
                count = row.count
                if month is not None and 1 <= int(month) <= 12:
                    current_year_data[int(month) - 1] = int(count) if count else 0

            # Fill previous year data
            for row in previous_year_data_raw:
                month = row.month
                count = row.count
                if month is not None and 1 <= int(month) <= 12:
                    previous_year_data[int(month) - 1] = int(count) if count else 0

            logger.info(f"Successfully retrieved monthly data for {current_year} and {previous_year}")

            return {
                'labels': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                           'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
                'datasets': [
                    {
                        'label': f'Missions en {current_year}',
                        'data': current_year_data,
                        'borderColor': 'rgba(0, 84, 63, 1)',
                        'backgroundColor': 'rgba(0, 84, 63, 0.1)',
                        'tension': 0.4,
                        'fill': True
                    },
                    {
                        'label': f'Missions en {previous_year}',
                        'data': previous_year_data,
                        'borderColor': 'rgba(0, 216, 113, 1)',
                        'backgroundColor': 'rgba(0, 216, 113, 0.1)',
                        'tension': 0.4,
                        'fill': True
                    }
                ]
            }

        except Exception as e:
            error_msg = f"Error in get_missions_by_month: {str(e)}"
            logger.error(error_msg)
            raise AnalyticsServiceError(error_msg)

    async def get_missions_by_status(self) -> Dict[str, Any]:
        """Get missions count grouped by status"""
        try:
            logger.info("Starting get_missions_by_status query")
            await self._validate_models()

            query = select(
                OrdreMission.etat,
                func.count(OrdreMission.id).label('count')
            ).where(
                OrdreMission.etat.isnot(None)
            ).group_by(OrdreMission.etat)

            result = await self.db.execute(query)
            query_results = result.fetchall()

            if not query_results:
                return {
                    'labels': ['Aucune donnée'],
                    'datasets': [{
                        'label': 'Nombre de missions',
                        'data': [0],
                        'backgroundColor': ['rgba(128, 128, 128, 0.7)'],
                        'borderColor': ['rgba(128, 128, 128, 1)'],
                        'borderWidth': 1
                    }]
                }

            # Convert enum values to display names
            status_labels = {
                EtatMission.OUVERTE: 'Ouvertes',
                EtatMission.EN_ATTENTE: 'En cours',
                EtatMission.CLOTUREE: 'Terminées',
                EtatMission.REFUSEE: 'Annulées'
            }

            status_colors = {
                EtatMission.OUVERTE: ('rgba(59, 130, 246, 0.7)', 'rgba(59, 130, 246, 1)'),
                EtatMission.EN_ATTENTE: ('rgba(245, 158, 11, 0.7)', 'rgba(245, 158, 11, 1)'),
                EtatMission.CLOTUREE: ('rgba(16, 185, 129, 0.7)', 'rgba(16, 185, 129, 1)'),
                EtatMission.REFUSEE: ('rgba(239, 68, 68, 0.7)', 'rgba(239, 68, 68, 1)')
            }

            labels = []
            data = []
            background_colors = []
            border_colors = []

            for row in query_results:
                status = row.etat
                count = row.count
                if status is not None:
                    labels.append(status_labels.get(status, str(status)))
                    data.append(int(count) if count else 0)
                    bg_color, border_color = status_colors.get(status,
                                                               ('rgba(128, 128, 128, 0.7)', 'rgba(128, 128, 128, 1)'))
                    background_colors.append(bg_color)
                    border_colors.append(border_color)

            logger.info(f"Successfully retrieved status data for {len(labels)} statuses")

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Nombre de missions',
                        'data': data,
                        'backgroundColor': background_colors,
                        'borderColor': border_colors,
                        'borderWidth': 1
                    }
                ]
            }

        except Exception as e:
            error_msg = f"Error in get_missions_by_status: {str(e)}"
            logger.error(error_msg)
            raise AnalyticsServiceError(error_msg)

    async def get_top_destinations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top destinations by counting ville column"""
        try:
            if limit <= 0 or limit > 100:
                raise ValueError("Limit must be between 1 and 100")

            logger.info(f"Starting get_top_destinations query with limit: {limit}")
            await self._validate_models()

            query = select(
                Mission.ville,
                func.count(OrdreMission.id).label('count')
            ).select_from(
                join(Mission, OrdreMission, Mission.id == OrdreMission.mission_id)
            ).where(
                Mission.ville.isnot(None)
            ).group_by(Mission.ville).order_by(
                func.count(OrdreMission.id).desc()
            ).limit(limit)

            result = await self.db.execute(query)
            query_results = result.fetchall()

            destinations = []
            for row in query_results:
                ville = row.ville
                count = row.count
                if ville and count is not None:
                    destinations.append({
                        'destination': str(ville),
                        'count': int(count)
                    })

            if not destinations:
                destinations = [{'destination': 'Aucune donnée', 'count': 0}]

            logger.info(f"Successfully retrieved {len(destinations)} top destinations")
            return destinations

        except Exception as e:
            logger.error(f"Error in get_top_destinations: {str(e)}")
            raise AnalyticsServiceError(f"Error in get_top_destinations: {str(e)}")

    async def get_recent_missions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent missions by selecting latest orders"""
        try:
            if limit <= 0 or limit > 100:
                raise ValueError("Limit must be between 1 and 100")

            logger.info(f"Starting get_recent_missions query with limit: {limit}")
            await self._validate_models()

            query = select(
                OrdreMission.id,
                OrdreMission.createdAt,
                OrdreMission.dateDebut,
                OrdreMission.dateFin,
                OrdreMission.etat,
                Mission.destination,
                Mission.type,
                Mission.ville,
                Mission.pays
            ).select_from(
                join(OrdreMission, Mission, OrdreMission.mission_id == Mission.id)
            ).where(
                OrdreMission.createdAt.isnot(None)
            ).order_by(OrdreMission.createdAt.desc()).limit(limit)

            result = await self.db.execute(query)
            query_results = result.fetchall()

            # Convert enum values to display names
            type_labels = {
                TypeMission.NATIONALE: 'NATIONALE',
                TypeMission.INTERNATIONALE: 'INTERNATIONALE'
            }

            status_labels = {
                EtatMission.OUVERTE: 'OUVERTE',
                EtatMission.EN_ATTENTE: 'EN_ATTENTE',
                EtatMission.VALIDEE_HIERARCHIQUEMENT: 'VALIDEE_HIERARCHIQUEMENT',
                EtatMission.VALIDEE_BUDGETAIREMENT: 'VALIDEE_BUDGETAIREMENT',
                EtatMission.APPROUVEE: 'APPROUVEE',
                EtatMission.CLOTUREE: 'CLOTUREE',
                EtatMission.REFUSEE: 'REFUSEE'
            }

            missions = []
            for row in query_results:
                try:
                    # Determine destination display
                    destination_display = 'N/A'
                    if row.destination:
                        destination_display = str(row.destination)
                    elif row.ville and row.pays:
                        destination_display = f"{row.ville}, {row.pays}"
                    elif row.ville:
                        destination_display = str(row.ville)

                    missions.append({
                        'id': str(row.id),
                        'destination': destination_display,
                        'type': type_labels.get(row.type, str(row.type)) if row.type else 'N/A',
                        'dateDebut': row.dateDebut.isoformat() if row.dateDebut else None,
                        'dateFin': row.dateFin.isoformat() if row.dateFin else None,
                        'status': status_labels.get(row.etat, str(row.etat)) if row.etat else 'N/A'
                    })
                except Exception as item_error:
                    logger.warning(f"Error processing mission item: {str(item_error)}")
                    continue

            logger.info(f"Successfully retrieved {len(missions)} recent missions")
            return missions

        except Exception as e:
            logger.error(f"Error in get_recent_missions: {str(e)}")
            raise AnalyticsServiceError(f"Error in get_recent_missions: {str(e)}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get general statistics"""
        try:
            logger.info("Starting get_statistics query")
            await self._validate_models()

            # Total missions
            total_query = select(func.count(OrdreMission.id))
            total_result = await self.db.execute(total_query)
            total_missions = total_result.scalar_one_or_none() or 0

            # Missions en cours
            en_cours_query = select(func.count(OrdreMission.id)).where(
                OrdreMission.etat == EtatMission.CLOTUREE
            )
            en_cours_result = await self.db.execute(en_cours_query)
            missions_en_cours = en_cours_result.scalar_one_or_none() or 0

            # Budget total
            budget_query = select(func.sum(Mission.budgetPrevu)).select_from(
                join(Mission, OrdreMission, Mission.id == OrdreMission.mission_id)
            ).where(Mission.budgetPrevu.isnot(None))

            budget_result = await self.db.execute(budget_query)
            budget_total = budget_result.scalar_one_or_none() or 0

            # Moyenne durée (en jours)
            duree_query = select(
                func.avg(OrdreMission.dateFin - OrdreMission.dateDebut)
            ).where(
                and_(OrdreMission.dateDebut.isnot(None),
                     OrdreMission.dateFin.isnot(None))
            )

            duree_result = await self.db.execute(duree_query)
            moyenne_duree_value = duree_result.scalar_one_or_none()
            moyenne_duree = float(moyenne_duree_value) if moyenne_duree_value else 0

            result = {
                'totalMissions': int(total_missions),
                'missionsEnCours': int(missions_en_cours),
                'budgetTotal': float(budget_total),
                'moyenneDuree': round(moyenne_duree, 1)
            }

            logger.info(f"Successfully retrieved statistics: {result}")
            return result

        except Exception as e:
            error_msg = f"Error in get_statistics: {str(e)}"
            logger.error(error_msg)
            raise AnalyticsServiceError(error_msg)

    async def get_all_analytics(self) -> Dict[str, Any]:
        """Get all analytics data"""
        try:
            logger.info("Starting complete get_all_analytics")

            result = {}
            errors = []

            # Execute all analytics methods
            analytics_methods = [
                ('missionsByType', self.get_missions_by_type),
                ('budgetByDestination', self.get_budget_by_destination),
                ('missionsByMonth', self.get_missions_by_month),
                ('missionsByStatus', self.get_missions_by_status),
                ('topDestinations', self.get_top_destinations),
                ('recentMissions', self.get_recent_missions),
                ('statistics', self.get_statistics)
            ]

            for key, method in analytics_methods:
                try:
                    if key in ['topDestinations', 'recentMissions']:
                        result[key] = await method()
                    else:
                        result[key] = await method()
                except Exception as e:
                    logger.error(f"Failed to get {key}: {str(e)}")
                    errors.append(f"{key}: {str(e)}")

                    # Provide fallback data
                    if key == 'statistics':
                        result[key] = {'totalMissions': 0, 'missionsEnCours': 0, 'budgetTotal': 0, 'moyenneDuree': 0}
                    elif key in ['topDestinations', 'recentMissions']:
                        result[key] = []
                    else:
                        result[key] = {'labels': [], 'datasets': []}

            if errors:
                logger.warning(f"Some analytics components failed: {errors}")
                result['_errors'] = errors

            logger.info("Successfully completed comprehensive analytics")
            return result

        except Exception as e:
            error_msg = f"Critical error in get_all_analytics: {str(e)}"
            logger.error(error_msg)
            raise AnalyticsServiceError(error_msg)