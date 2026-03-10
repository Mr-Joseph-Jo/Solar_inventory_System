from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import Paragraph
from num2words import num2words
import os
from datetime import datetime


def generate_invoice(invoice_no, company, sale, items, gst_type, output_path):
    """
    invoice_no: string like '0001'
    company: row from company_settings
    sale: row from sales table
    items: list of sale_items joined with inventory
    gst_type: CGST_SGST / IGST / NONE
    output_path: full file path
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # ---- HEADER ----
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 30, company["company_name"])

    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 45, "GST TAX INVOICE")

    # ---- COMPANY DETAILS ----
    y = height - 70
    c.setFont("Helvetica", 9)
    c.drawString(20, y, company["address"] or "")
    y -= 12
    c.drawString(20, y, f"GSTIN: {company['gstin'] or ''}")
    y -= 12
    c.drawString(20, y, f"Phone: {company['phone'] or ''}")

    # ---- INVOICE META ----
    c.drawRightString(width - 20, height - 70, f"Invoice No: {invoice_no}")
    c.drawRightString(
        width - 20,
        height - 85,
        f"Date: {sale['invoice_date'].strftime('%d-%m-%Y')}"
    )

    # ---- BUYER DETAILS ----
    y -= 30
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "Buyer:")
    y -= 12
    c.setFont("Helvetica", 9)
    c.drawString(20, y, sale["buyer_name"])
    y -= 12
    if sale["buyer_address"]:
        c.drawString(20, y, sale["buyer_address"])

    # ---- TABLE HEADER ----
    y -= 30
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "Sl")
    c.drawString(45, y, "Description")
    c.drawString(260, y, "HSN")
    c.drawRightString(310, y, "Qty")
    c.drawRightString(360, y, "Rate")
    c.drawRightString(430, y, "GST")
    c.drawRightString(500, y, "Amount")

    c.line(20, y - 2, width - 20, y - 2)

    # ---- ITEMS ----
    y -= 15
    c.setFont("Helvetica", 9)

    subtotal = 0
    gst_totals = {}  # gst_rate -> amount

    for i, it in enumerate(items, start=1):
        line_amount = it["unit_price"] * it["quantity"]
        subtotal += line_amount

        gst_rate = it["gst_rate"]
        gst_amt = it["cgst_amount"] + it["sgst_amount"] + it["igst_amount"]

        gst_totals[gst_rate] = gst_totals.get(gst_rate, 0) + gst_amt

        c.drawString(20, y, str(i))
        c.drawString(45, y, it["name"])
        c.drawString(260, y, it["hsn_code"] or "")
        c.drawRightString(310, y, str(it["quantity"]))
        c.drawRightString(360, y, f"{it['unit_price']:.2f}")
        c.drawRightString(430, y, f"{gst_rate}%")
        c.drawRightString(500, y, f"{line_amount:.2f}")

        y -= 14

    # ---- TOTALS ----
    y -= 10
    c.line(20, y, width - 20, y)

    y -= 15
    c.drawRightString(430, y, "Subtotal:")
    c.drawRightString(500, y, f"{subtotal:.2f}")

    total_gst = sum(gst_totals.values())
    y -= 14
    c.drawRightString(430, y, "GST:")
    c.drawRightString(500, y, f"{total_gst:.2f}")

    y -= 14
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(430, y, "Grand Total:")
    c.drawRightString(500, y, f"{sale['total_amount']:.2f}")

    # ---- AMOUNT IN WORDS ----
    y -= 25
    c.setFont("Helvetica", 9)
    amt_words = num2words(sale["total_amount"], to="currency", lang="en_IN")
    c.drawString(20, y, f"Amount in words: {amt_words.capitalize()}")

    # ---- BANK DETAILS ----
    y -= 30
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "Bank Details:")
    y -= 12
    c.setFont("Helvetica", 9)
    c.drawString(20, y, f"Bank: {company['bank_name'] or ''}")
    y -= 12
    c.drawString(20, y, f"A/C No: {company['account_no'] or ''}")
    y -= 12
    c.drawString(20, y, f"IFSC: {company['ifsc'] or ''}")

    # ---- FOOTER ----
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 20, 40, "For " + company["company_name"])
    c.drawRightString(width - 20, 25, "Authorised Signatory")

    c.showPage()
    c.save()
