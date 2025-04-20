from io import BytesIO

from reportlab.pdfgen import canvas


def DocFactory():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, 'pdf')
    p.showPage()
    p.save()
    buffer.seek(0)
    return ('pdf.pdf', buffer.read(), 'application/pdf')
