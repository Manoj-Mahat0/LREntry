from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def generate_payment_status_pdf(statuses):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Watermark across the page
    def draw_watermark():
        c.saveState()
        c.setFont("Helvetica-Bold", 40)
        c.setFillColorRGB(0.8, 0.8, 0.8)
        c.setFillAlpha(0.06)
        for x in range(0, int(width), 200):
            for y in range(0, int(height), 150):
                c.saveState()
                c.translate(x, y)
                c.rotate(45)
                c.drawCentredString(0, 0, "SYSTAIO")
                c.restoreState()
        c.restoreState()

    # Header with watermark
    def draw_header():
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.rect(0, 0, width, height, fill=1)

        draw_watermark()

        # Company Info
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.white)
        c.drawCentredString(width / 2, height - 50, "Systaio Logistics Pvt. Ltd.")

        c.setFont("Helvetica", 11)
        c.drawCentredString(width / 2, height - 70, "12/7B, Ring Road, Industrial Area, Delhi - 110041")
        c.drawCentredString(width / 2, height - 85, "Contact: +91-9876543210 | Email: support@systaio.com")

        # Divider line
        c.setLineWidth(1)
        c.setStrokeColor(colors.grey)
        c.line(40, height - 100, width - 40, height - 100)

        # Report Title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.yellow)
        c.drawCentredString(width / 2, height - 120, "Payment Status Report")

    # Footer with page number
    def draw_footer():
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.white)
        c.drawCentredString(width / 2, 30, f"Page {c.getPageNumber()}")
        c.drawCentredString(width / 2, 15, "© 2025 Systaio Logistics Pvt. Ltd.")

    draw_header()

    y = height - 160
    padding_x = 60

    for idx, item in enumerate(statuses, start=1):
        box_height = 100

        # Simulate drop shadow by drawing dark rectangle behind
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.roundRect(42, y - box_height + 8, width - 80, box_height, radius=10, fill=1)

        # Yellow Card
        c.setFillColor(colors.yellow)
        c.setStrokeColor(colors.orange)
        c.setLineWidth(1)
        c.roundRect(40, y - box_height + 10, width - 80, box_height, radius=10, fill=1)

        # Header
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(padding_x, y, f"{idx}. Bill No: {item['bill_no']}")

        # Content
        c.setFont("Helvetica", 10)
        y -= 20
        c.drawString(padding_x, y, "LR Number")
        c.drawString(padding_x + 110, y, f": {item['lr_no']}")

        y -= 15
        c.drawString(padding_x, y, "Transport Name")
        c.drawString(padding_x + 110, y, f": {item['transport_name']}")

        y -= 15
        # Payment Status with colored label
        c.drawString(padding_x, y, "Payment Status")
        status_color = colors.green if item['payment_status'].lower() == 'paid' else colors.red
        c.setFillColor(status_color)
        c.drawString(padding_x + 110, y, f": {item['payment_status']}")

        y -= 15
        c.setFillColor(colors.black)
        c.drawString(padding_x, y, "Net Payable")
        c.drawString(padding_x + 110, y, f": Rs. {item['net_payable']}")

        y -= 15
        c.drawString(padding_x, y, "Created At")
        date_str = item['created_at'].split('T')[0]
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        c.drawString(padding_x + 110, y, f": {formatted_date}")

        y -= 30

        # Page break
        if y < 120:
            draw_footer()
            c.showPage()
            draw_header()
            y = height - 160

    draw_footer()
    c.save()
    buffer.seek(0)
    return buffer
