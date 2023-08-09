from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table,TableStyle,SimpleDocTemplate,Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def create_pdf(buffer,pharmacy,order):
    pdf = SimpleDocTemplate(
            buffer,
            pagesize = letter,
            rightMargin=10,
            leftMargin=10,
            topMargin=40,
            bottomMargin=25
        )
    
    total = 0
    elems = []

    p_style = ParagraphStyle(name='_',alignment=TA_CENTER,fontSize=12)
    l_style = ParagraphStyle(name="_",fontName="Courier-Bold",fontSize=20,textColor=colors.grey,leftIndent=20,leading=25)
    t_style = ParagraphStyle(name="_",parent=l_style,fontSize=25,textColor=colors.black,alignment=TA_CENTER)
    h_style = ParagraphStyle(name='_',alignment=TA_CENTER,fontName='Courier-Bold',fontSize=14,textColor=colors.white)
    table_style = TableStyle([
         ('VALIGN',(0,0),(-1,-1),'TOP'),
    ])

    order_type = f"{type(order)}".split('.')[2][:-2]
    
    elems.append(Table([[Paragraph(f"{order_type} Inovince",style=t_style)]],spaceAfter=5))
    
    l_table_data = [
        [
        Paragraph(f"Pharmacy:{pharmacy.name}",style=l_style),
        Paragraph(f"OrderID:{order.id}",style=l_style)
        ],
        [
            Paragraph(f"Time:{order.time()}",style=l_style),
            Paragraph(f"")
        ]
    ]

    if order_type == "Sale":
         l_table_data.insert(1,[
        Paragraph(f"Doctor:{order.doctor_name}" if order.doctor_name else "Doctor:",style=l_style),
        Paragraph(f"Coustomer:{order.coustomer_name}" if order.coustomer_name else "Coustomer:",style=l_style)
        ])

    elems.append(Table(l_table_data,colWidths=[5*inch,None],style=table_style,minRowHeights=[0,30,30],spaceAfter=10))
    data = [
        [Paragraph("medicine",style=h_style),
         Paragraph("price",style=h_style),
         Paragraph("quantity",style=h_style),
         Paragraph("total",style=h_style)
         ]
    ]

    for item in order.items.select_related("medicine").all():
            data.append([Paragraph(f"{item.medicine.brand_name}",style=p_style),
                         Paragraph(f"{item.price}",style=p_style),
                         Paragraph(f"{item.quantity}",style=p_style),
                         Paragraph(f"{item.price * item.quantity}",style=p_style)
                         ])
            total += item.price * item.quantity

    table = Table(data,colWidths=[3*inch,1.6*inch,1.2*inch,1.6*inch])

    style = TableStyle([
        ('BACKGROUND', (0,0), (3,0), colors.green),
        ('VALIGN',(0,0),(-0.5,-0.5),'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('LINEBEFORE',(2,1),(2,-1),2,colors.red),
        ('LINEABOVE',(0,2),(-1,2),2,colors.green),
        ('GRID',(0,1),(-1,-1),2,colors.black),
    ])
    table.setStyle(style)
    rowNumb = len(data)
    for i in range(1, rowNumb):
        if i % 2 == 0:
            bc = colors.burlywood
        else:
            bc = colors.beige
        ts = TableStyle(
            [('BACKGROUND', (0,i),(-1,i), bc)]
        )
        table.setStyle(ts)

    elems.append(table)
    l_style.textColor = colors.red
    elems.append(Table([[Paragraph(f"Total: {total}",style=l_style)]],spaceBefore=20))
    pdf.build(elems)