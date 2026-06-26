"""PDF generation helpers for completion certificates and payment receipts,
built with reportlab.
"""

import io

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ACCENT = colors.HexColor("#2563EB")
ACCENT_LIGHT = colors.HexColor("#22D3EE")
DARK = colors.HexColor("#0F172A")
GREY = colors.HexColor("#64748B")


def generate_certificate_pdf(student, certificate):
    """Generate a completion certificate PDF and return raw bytes."""
    buffer = io.BytesIO()
    page_size = landscape(A4)
    width, height = page_size
    c = canvas.Canvas(buffer, pagesize=page_size)

    # Border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(4)
    c.rect(20 * mm, 15 * mm, width - 40 * mm, height - 30 * mm)
    c.setStrokeColor(ACCENT_LIGHT)
    c.setLineWidth(1)
    c.rect(24 * mm, 19 * mm, width - 48 * mm, height - 38 * mm)

    # Header
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 45 * mm, "LiG TECHNOLOGY")

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(width / 2, height - 65 * mm, "Certificate of Completion")

    c.setFillColor(GREY)
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 78 * mm, "This certificate is proudly presented to")

    # Student name
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 95 * mm, student.full_name)

    # Description
    c.setFillColor(GREY)
    c.setFont("Helvetica", 12)
    description = (
        f"for successfully completing the Student Industrial Attachment Programme "
        f"in {student.get_department_display()}, including all required modules, "
        f"assignments, and payment obligations."
    )
    text_obj = c.beginText(40 * mm, height - 110 * mm)
    text_obj.setFont("Helvetica", 12)
    text_obj.setLeading(16)
    import textwrap
    for line in textwrap.wrap(description, width=95):
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Footer details
    issue_date = certificate.issued_at.strftime("%B %d, %Y")
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40 * mm, 35 * mm, "Date Issued:")
    c.drawString(40 * mm, 28 * mm, "Certificate ID:")
    c.drawString(40 * mm, 21 * mm, "Student ID:")

    c.setFont("Helvetica", 11)
    c.drawString(70 * mm, 35 * mm, issue_date)
    c.drawString(70 * mm, 28 * mm, certificate.certificate_id)
    c.drawString(70 * mm, 21 * mm, student.student_id)

    # Signature line
    c.setStrokeColor(DARK)
    c.line(width - 95 * mm, 35 * mm, width - 35 * mm, 35 * mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width - 65 * mm, 28 * mm, "LuckyTech Innovation Ground")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width - 65 * mm, 22 * mm, "Programme Director")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_receipt_pdf(student, payment):
    """Generate a payment receipt PDF and return raw bytes."""
    buffer = io.BytesIO()
    page_size = A4
    width, height = page_size
    c = canvas.Canvas(buffer, pagesize=page_size)

    margin = 20 * mm

    # Header bar
    c.setFillColor(ACCENT)
    c.rect(0, height - 30 * mm, width, 30 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, height - 18 * mm, "LiG TECHNOLOGY")
    c.setFont("Helvetica", 11)
    c.drawRightString(width - margin, height - 18 * mm, "Payment Receipt")

    y = height - 45 * mm

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Receipt Details")
    y -= 10 * mm

    rows = [
        ("Receipt / Reference No.", payment.reference),
        ("Student Name", student.full_name),
        ("Student ID", student.student_id),
        ("Amount Paid (GHS)", f"{payment.amount}"),
        ("Payment Channel", payment.channel or "N/A"),
        ("Status", payment.get_status_display()),
        ("Date Paid", payment.paid_at.strftime("%B %d, %Y %H:%M") if payment.paid_at else "N/A"),
        ("Date Recorded", payment.created_at.strftime("%B %d, %Y %H:%M")),
    ]

    c.setFont("Helvetica", 11)
    for label, value in rows:
        c.setFillColor(GREY)
        c.drawString(margin, y, label)
        c.setFillColor(DARK)
        c.drawRightString(width - margin, y, str(value))
        c.setStrokeColor(colors.HexColor("#E2E8F0"))
        c.line(margin, y - 3, width - margin, y - 3)
        y -= 9 * mm

    y -= 5 * mm
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Summary")
    y -= 9 * mm

    c.setFont("Helvetica", 11)
    c.setFillColor(GREY)
    c.drawString(margin, y, f"Total Attachment Fee (GHS)")
    c.setFillColor(DARK)
    c.drawRightString(width - margin, y, f"{student.config.attachment_fee}")
    y -= 9 * mm

    c.setFillColor(GREY)
    c.drawString(margin, y, "Total Paid To Date (GHS)")
    c.setFillColor(DARK)
    c.drawRightString(width - margin, y, f"{student.total_paid}")
    y -= 9 * mm

    c.setFillColor(GREY)
    c.drawString(margin, y, "Outstanding Balance (GHS)")
    c.setFillColor(DARK)
    c.drawRightString(width - margin, y, f"{student.outstanding_balance}")

    # Footer
    c.setFillColor(GREY)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2, 15 * mm,
        f"Generated on {timezone.now().strftime('%B %d, %Y %H:%M')} "
        f"- LuckyTech Innovation Ground Student Portal"
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
