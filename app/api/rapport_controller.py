import datetime
from uuid import UUID
import io
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import rapport_mission_repo, mission_repo
from app.schemas.rapport_schema import RapportCreate, RapportOut
from dependencies import get_db
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from app.services.user_service import SimpleUserService, get_current_user_token

router = APIRouter(prefix="/rapport", tags=["Rapport"])

user_service = SimpleUserService()

@router.get("/")
async def get_rapports(db: AsyncSession = Depends(get_db)):
    rapports = await rapport_mission_repo.get_rapports(db)
    return [
        {
            "id": rapport.id,
            "objective": rapport.objective,
            "proceedings": rapport.proceedings,
            "results achieved": rapport.resultAchieved,
            "key Contacts": rapport.keyContact,
            "interlocutors": rapport.interlocutors,
            "difficulties": rapport.difficulties,
            "recommendations": rapport.recommendations,
            "next Step": rapport.nextStep,
            "isValid" : rapport.isValid,
            "ordre_mission": {
                "id": rapport.ordre_mission.id,
                "debut": rapport.ordre_mission.dateDebut,
                "fin": rapport.ordre_mission.dateFin,
                "user": rapport.ordre_mission.user_id,
                "mission": rapport.ordre_mission.mission_id,
                "accord resposnable": f"order/file/{rapport.ordre_mission.id}/download",
                "createdAt": rapport.ordre_mission.createdAt,
                "updatedAt": rapport.ordre_mission.updatedAt,
            } if rapport.ordre_mission else None,
            "rapport": f"/rapport/download/{rapport.id}"

        } for rapport in rapports
    ]


@router.post("/add", response_model=RapportOut)
async def create_rapport(
        file: UploadFile = File(...),
        ordre_mission_id: UUID = Form(...),
        content: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    rapport = RapportCreate(contenu=content, ordre_mission_id=ordre_mission_id)
    file_data = await file.read() if file else None
    return await rapport_mission_repo.create_rapport(db, rapport, file_data)


@router.post("/create", response_model=RapportOut)
async def create_rapport_mission(rapport: RapportCreate, db: AsyncSession = Depends(get_db)):
    return await rapport_mission_repo.create_rapport(db, rapport)


@router.put("/update-{rapport_id}", response_model=RapportOut)
async def update_rapport(
        rapport_id: UUID,
        rapport_update: RapportCreate,
        db: AsyncSession = Depends(get_db)
):
    db_rapport = await rapport_mission_repo.update_rapport_mission(db, rapport_id, rapport_update)
    if db_rapport is None:
        raise HTTPException(status_code=404, detail="Rapport de mission non trouvé")
    return db_rapport


@router.delete("/delete/{rapport_mission_id}", response_model=RapportOut)
async def delete_rapport(
        rapport_mission_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_rapport_mission = await rapport_mission_repo.delete_rapport(db, rapport_mission_id)
    if db_rapport_mission is None:
        raise HTTPException(status_code=404, detail="Rapport de mission non trouvé")

    return db_rapport_mission

@router.put("/validate/{rapport_mission_id}", response_model=RapportOut)
async def validate_rapport(rapport_mission_id: UUID, db: AsyncSession = Depends(get_db)):
    db_rapport = await rapport_mission_repo.validate_rapport_mission(db, rapport_mission_id)
    if db_rapport is None:
        raise HTTPException(status_code=404, detail="Rapport de mission non trouve")
    return db_rapport

@router.get("/download/{rapport_mission_id}")
async def download_rapport(request:Request,rapport_mission_id: UUID, db: AsyncSession = Depends(get_db)):
    buffer = io.BytesIO()

    db_rapport = await rapport_mission_repo.get_rapport_by_id(db, rapport_mission_id)
    if db_rapport is None:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")

    db_mission = await mission_repo.get_mission_by_id(db, db_rapport.ordre_mission.mission_id)
    current_token = get_current_user_token(request)
    user = await user_service.get_user_by_id(db_rapport.ordre_mission.user_id,current_token)
    print(user)


    if db_mission is None:
        raise HTTPException(status_code=404, detail="Mission associée non trouvée")

    # Define a custom SimpleDocTemplate for the header on every page
    # The header will be added via a PageTemplate
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=4.5 * cm,  # Increased top margin to accommodate header content
        bottomMargin=2.5 * cm
    )

    # Get styles
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=0.5 * cm
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=0.1 * cm
    )

    field_style = ParagraphStyle(
        'FieldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=TA_LEFT
    )

    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceBefore=0.2 * cm,
        spaceAfter=0.3 * cm,
        leftIndent=0.5 * cm
    )

    detail_title_style = ParagraphStyle(
        'DetailTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=TA_LEFT,
        spaceBefore=0.4 * cm,
        spaceAfter=0.2 * cm,
        leftIndent=0.2 * cm
    )

    # --- Page Templates Setup ---
    # Define frames for the header area and the main content area
    # The header frame is positioned at the top of the page.
    # The coordinates are relative to the bottom-left corner of the page.
    header_frame = Frame(
        doc.leftMargin,
        A4[1] - doc.topMargin, # Y position starts at the top margin boundary
        A4[0] - doc.leftMargin - doc.rightMargin,
        doc.topMargin - 0.5 * cm, # Height of the header frame, leaving a small buffer
        leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0,
        showBoundary=0 # Set to 1 for debugging frame boundaries
    )

    # Main content frame, starting below the header area and respecting bottom margin
    content_frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        A4[0] - doc.leftMargin - doc.rightMargin,
        A4[1] - doc.topMargin - doc.bottomMargin, # Height adjusted for both top and bottom margins
        leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0,
        showBoundary=0 # Set to 1 for debugging frame boundaries
    )

    # Function to create header flowables (e.g., logos)
    def create_header_flowables():
        try:
            # Ensure these paths are correct relative to where your app runs
            logo_left = Image('assets/logo2.png', width=4 * cm, height=3.5 * cm)
            logo_right = Image('assets/logo.png', width=4 * cm, height=3.5 * cm)
        except Exception:
            # Fallback if images are not found
            logo_left = Paragraph("<b>LOGO 1</b>", normal_style)
            logo_right = Paragraph("<b>LOGO 2</b>", normal_style)

        header_data = [[logo_left, logo_right]]
        # Use available width for the table
        header_table = Table(header_data, colWidths=[(A4[0] - doc.leftMargin - doc.rightMargin) / 2] * 2)
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        return [header_table]

    # The onPage function for PageTemplate. It receives canvas and document.
    # We use header_frame.addFromList to draw the header content within the header frame.
    def header_on_each_page(canvas, doc):
        header_flowables = create_header_flowables()
        # Add the header flowables to the header_frame.
        # This will draw them within the frame's boundaries.
        header_frame.addFromList(header_flowables, canvas)


    # Page template for all pages.
    # The 'frames' argument lists where the main story content will flow.
    # The 'onPage' argument defines what custom elements are drawn on every page (like the header).
    all_pages_template = PageTemplate(
        id='AllPages',
        frames=[content_frame], # Only content_frame is for the main story flow
        onPage=header_on_each_page # The header is drawn on the canvas for each page
    )

    doc.addPageTemplates([all_pages_template])
    # --- End Page Templates Setup ---

    # 1. Title (this will be part of the main story and flow with content)
    title_text = Paragraph("Rapport de Mission", title_style)
    story.append(title_text)
    story.append(Spacer(1, 0.5 * cm))

    # 2. Personal Information Section
    section_header_data = [["INFORMATIONS PERSONNELLES"]]
    section_header_table = Table(section_header_data, colWidths=[16 * cm])
    section_header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))

    nom_field = Paragraph("<b>Nom :</b>", field_style)
    nom_value = Paragraph(user.get("nom", "Non spécifié"), normal_style)  # ✅

    prenom_field = Paragraph("<b>Prénom :</b>", field_style)
    prenom_value = Paragraph(user.get("prenom", "Non spécifié"), normal_style)  # ✅

    email_field = Paragraph("<b>E-mail :</b>", field_style)
    email_value = Paragraph(user.get("email", "Non spécifié"), normal_style)  # ✅

    personal_data = [
        [nom_field, nom_value],
        [prenom_field, prenom_value],
        [email_field, email_value]
    ]

    personal_table = Table(personal_data, colWidths=[5 * cm, 11 * cm])
    personal_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(section_header_table)
    story.append(personal_table)
    story.append(Spacer(1, 0.5 * cm))

    # 3. Mission Information Section
    mission_header_data = [["INFORMATIONS DE LA MISSION"]]
    mission_header_table = Table(mission_header_data, colWidths=[16 * cm])
    mission_header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))

    mission_title_field = Paragraph("<b>Titre de la mission :</b>", field_style)
    mission_title_value = Paragraph(db_mission.details, normal_style)
    mission_date_field = Paragraph("<b>Date de la mission :</b>", field_style)
    mission_date_value = Paragraph(db_rapport.ordre_mission.dateDebut.isoformat(), normal_style)
    mission_duration_field = Paragraph("<b>Durée/Date de fin :</b>", field_style)
    mission_duration_value = Paragraph(db_rapport.ordre_mission.dateFin.isoformat(), normal_style)

    mission_data = [
        [mission_title_field, mission_title_value],
        [mission_date_field, mission_date_value],
        [mission_duration_field, mission_duration_value]
    ]

    mission_table = Table(mission_data, colWidths=[5 * cm, 11 * cm])
    mission_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(mission_header_table)
    story.append(mission_table)
    story.append(Spacer(1, 0.7 * cm))

    # 4. Mission Details Section
    details_header_data = [["DÉTAILS DE LA MISSION"]]
    details_header_table = Table(details_header_data, colWidths=[16 * cm])
    details_header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))

    story.append(details_header_table)

    sections = [
        ("1- Objectifs de la mission :", db_rapport.objective),
        ("2- Activités réalisées :", db_rapport.proceedings),
        ("3- Résultats obtenus :", db_rapport.resultAchieved),
        ("4- Key Contacts :", db_rapport.keyContact),
        ("5- Interlocuteurs :", db_rapport.interlocutors),
        ("6- Difficultés rencontrées :", db_rapport.difficulties),
        ("7- Recommandations :", db_rapport.recommendations)
    ]

    for title, content in sections:
        section_title = Paragraph(f"<b>{title}</b>", detail_title_style)
        story.append(section_title)

        if content:
            section_content = Paragraph(content, content_style)
            story.append(section_content)
        else:
            section_content = Paragraph("<i>Non renseigné</i>", content_style)
            story.append(section_content)

    # Build PDF
    doc.build(story)

    buffer.seek(0)
    filename = "RapportMission_" + (db_mission.titre or "") + "_" + datetime.datetime.now().strftime(
        "%Y%m%d%H%M%S") + ".pdf"

    return StreamingResponse(
        io.BytesIO(buffer.getvalue()),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(buffer.getvalue()))
        }
    )

@router.post("/validate-report/{reportId}", response_model=RapportOut)
async def validate_report(reportId: UUID, db: AsyncSession = Depends(get_db)):
    rapport_dict = await rapport_mission_repo.validate_rapport_mission(db, rapport_mission_id=reportId)
    if not rapport_dict:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    return RapportOut(**rapport_dict)

