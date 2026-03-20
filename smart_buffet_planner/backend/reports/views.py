from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from events.models import Event
import io


def build_pdf(event):
    pdf_io = io.BytesIO()
    doc = SimpleDocTemplate(pdf_io, pagesize=A4,
                             rightMargin=2*cm, leftMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Title style
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=22, textColor=colors.HexColor('#1e3a5f'),
                                  spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#4a6fa5'),
                                     spaceAfter=4, alignment=TA_CENTER)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'],
                                    fontSize=13, textColor=colors.HexColor('#1e3a5f'),
                                    spaceBefore=12, spaceAfter=6)
    normal = styles['Normal']

    # Header
    story.append(Paragraph("Smart Buffer Planner", title_style))
    story.append(Paragraph("Professional Buffet Planning Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 0.3*inch))

    # Event Details
    story.append(Paragraph("Event Details", section_style))
    event_data = [
        ['Event Name', event.name],
        ['Event Type', event.get_event_type_display()],
        ['Event Date', str(event.event_date)],
        ['Guest Count', str(event.guest_count)],
        ['Venue', event.venue or 'N/A'],
        ['Safety Buffer', f"{event.buffer_percentage}%"],
        ['Status', event.get_status_display()],
    ]
    t = Table(event_data, colWidths=[4*cm, 12*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    # Menu & Calculations
    story.append(Paragraph("Menu & Quantity Calculations", section_style))
    items = event.menu_items.select_related('dish__category').all()

    menu_data = [['Dish', 'Category', 'Qty/Person', 'Total Qty', 'With Buffer', 'Cost']]
    total_cost = 0
    for item in items:
        menu_data.append([
            item.dish.name,
            item.dish.category.name,
            f"{item.effective_qty_per_person} {item.dish.unit}",
            f"{float(item.total_quantity):.1f}",
            f"{float(item.total_quantity_with_buffer):.1f}",
            f"${float(item.total_cost):.2f}",
        ])
        total_cost += float(item.total_cost)

    menu_data.append(['', '', '', '', 'TOTAL', f"${total_cost:.2f}"])

    t2 = Table(menu_data, colWidths=[4.5*cm, 3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0fe')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (1, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))

    # Budget Summary
    story.append(Paragraph("Budget Estimation", section_style))
    cost_per_guest = total_cost / event.guest_count if event.guest_count else 0
    buf_pct = float(event.buffer_percentage)
    waste_pct = buf_pct * 0.6
    waste_risk = 'Low' if waste_pct < 8 else ('Medium' if waste_pct < 15 else 'High')

    budget_data = [
        ['Total Catering Cost', f"${total_cost:.2f}"],
        ['Cost Per Guest', f"${cost_per_guest:.2f}"],
        ['Estimated Waste %', f"{waste_pct:.1f}%"],
        ['Waste Risk Level', waste_risk],
        ['Safety Buffer Applied', f"{buf_pct}%"],
    ]
    t3 = Table(budget_data, colWidths=[8*cm, 8*cm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.3*inch))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Generated by Smart Buffer Planner | Reduce Waste, Plan Smart",
                             ParagraphStyle('Footer', parent=normal, fontSize=8,
                                            textColor=colors.grey, alignment=TA_CENTER)))

    doc.build(story)
    pdf_io.seek(0)
    return pdf_io


class EventReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        user = request.user
        try:
            if user.is_staff or user.role == 'admin':
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, user=user)
        except Event.DoesNotExist:
            return HttpResponse('Event not found', status=404)

        pdf_buffer = build_pdf(event)
        filename = f"buffet_plan_{event.name.replace(' ', '_')}_{event.event_date}.pdf"
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
