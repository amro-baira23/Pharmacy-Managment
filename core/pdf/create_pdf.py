from .blank_page import blank_page
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

def create_pdf(buffer,data,pharmacy,order_id):
    c = canvas.Canvas(buffer,pagesize=letter)
    c = blank_page(c,pharmacy,order_id)

    c.setFillColorRGB(0,0,1)
    c.setFont("Helvetica", 20)
    line_y=7.9
    total=0
    for items in data:
        row_gap=0.4
        line = line_y
        if len(items[0]) < 25:
            c.drawString(0,line_y*inch,str(items[0] + '.'))
        else:
            c.drawString(0,line_y*inch,str(items[0][:25]))
            line_y -= row_gap
            c.drawString(0,line_y*inch,str(items[0][25:] + '.'))
            line = line_y
            line_y += row_gap
            row_gap = 0.8

        c.drawRightString(4.5*inch,line_y*inch,str(items[1]))
        c.drawRightString(6*inch,line_y*inch,str(items[2]))
        c.drawRightString(7*inch,line_y*inch,str(items[3]))
        c.line(0.01*inch,(line - 0.1)*inch,7.5*inch,(line - 0.1)*inch)
        total=round(total+items[3])
        line_y=line_y-row_gap

    c.setFillColorRGB(1,0,0)
    c.setFont("Times-Bold", 22)
    c.drawRightString(7*inch,0.8*inch,str(float(total)))
    c.showPage()
    c.save()

    return c