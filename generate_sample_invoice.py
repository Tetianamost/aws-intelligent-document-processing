#!/usr/bin/env python3
"""
Generate a simple filled invoice as a PDF using reportlab.
Run with: python3 generate_sample_invoice.py
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER
except ImportError:
    print("Installing required packages...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "--user", "--break-system-packages"])
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER

def create_filled_invoice():
    """Create a filled invoice with realistic data"""
    filename = "sample_documents/filled-invoice.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Company header
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    story.append(Paragraph("CloudTech Solutions Inc.", title_style))
    story.append(Paragraph("123 Tech Boulevard, San Francisco, CA 94105", 
                          ParagraphStyle('center', alignment=TA_CENTER, fontSize=10)))
    story.append(Paragraph("Phone: (555) 123-4567 | Email: billing@cloudtech.com", 
                          ParagraphStyle('center', alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice title
    story.append(Paragraph("<b>INVOICE</b>", 
                          ParagraphStyle('inv', fontSize=18, alignment=TA_CENTER, spaceAfter=20)))
    
    # Invoice details
    invoice_data = [
        ['Invoice Number:', 'INV-2024-001234'],
        ['Invoice Date:', 'December 15, 2024'],
        ['Due Date:', 'January 15, 2025'],
        ['Customer ID:', 'CUST-5678']
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 3*inch])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Bill to
    story.append(Paragraph("<b>Bill To:</b>", styles['Heading3']))
    bill_to = """
    Acme Corporation<br/>
    456 Business Park Drive<br/>
    New York, NY 10001<br/>
    Attn: John Smith, CFO<br/>
    john.smith@acmecorp.com
    """
    story.append(Paragraph(bill_to, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Items table
    story.append(Paragraph("<b>Services Provided:</b>", styles['Heading3']))
    items_data = [
        ['Description', 'Quantity', 'Rate', 'Amount'],
        ['AWS Cloud Infrastructure Setup', '1 project', '$5,000.00', '$5,000.00'],
        ['Senior DevOps Consulting', '80 hours', '$175.00/hr', '$14,000.00'],
        ['Database Migration Services', '40 hours', '$150.00/hr', '$6,000.00'],
        ['Security Audit & Implementation', '1 project', '$3,500.00', '$3,500.00'],
        ['24/7 Monitoring Setup', '1 month', '$2,000.00', '$2,000.00'],
    ]
    
    items_table = Table(items_data, colWidths=[3*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Totals
    totals_data = [
        ['', '', 'Subtotal:', '$30,500.00'],
        ['', '', 'Tax (8.875%):', '$2,706.88'],
        ['', '', 'Total Amount Due:', '$33,206.88'],
    ]
    
    totals_table = Table(totals_data, colWidths=[3*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
        ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#E74C3C')),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Payment terms
    story.append(Paragraph("<b>Payment Terms:</b>", styles['Heading3']))
    terms = """
    Payment is due within 30 days of invoice date. Please remit payment via:<br/>
    • Wire Transfer: Bank of America, Account #987654321, Routing #026009593<br/>
    • Check: Payable to "CloudTech Solutions Inc."<br/>
    • ACH: Contact billing@cloudtech.com for details<br/><br/>
    Late payments subject to 1.5% monthly interest charge.
    """
    story.append(Paragraph(terms, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("<i>Thank you for your business!</i>", 
                          ParagraphStyle('footer', fontSize=10, alignment=TA_CENTER, textColor=colors.grey)))
    
    doc.build(story)
    print(f"✅ Created: {filename}")
    print("This invoice contains:")
    print("  - Company information and contact details")
    print("  - Invoice metadata (number, dates, customer ID)")
    print("  - Bill-to information")
    print("  - Itemized services table with 5 line items")
    print("  - Subtotal, tax, and total calculations")
    print("  - Payment terms and instructions")

if __name__ == "__main__":
    import os
    os.makedirs("sample_documents", exist_ok=True)
    create_filled_invoice()
