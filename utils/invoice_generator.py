"""
Generates a GST invoice PDF matching the Green INN Solutions template.
Items are numbered dynamically — no blank filler rows.
Supports: mode of payment, destination, vehicle no, driver name, discount.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from num2words import num2words


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def _style(name, **kw):
    defaults = dict(fontName="Helvetica", fontSize=8, leading=10,
                    spaceAfter=0, spaceBefore=0)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

BOLD   = "Helvetica-Bold"
NORMAL = "Helvetica"

S_TITLE  = _style("title",  fontName=BOLD,   fontSize=12, alignment=TA_CENTER, leading=14)
S_SUB    = _style("sub",    fontName=NORMAL, fontSize=8,  alignment=TA_CENTER)
S_LABEL  = _style("label",  fontName=BOLD,   fontSize=8)
S_NORMAL = _style("normal", fontName=NORMAL, fontSize=8)
S_RIGHT  = _style("right",  fontName=NORMAL, fontSize=8,  alignment=TA_RIGHT)
S_CENTER = _style("center", fontName=NORMAL, fontSize=8,  alignment=TA_CENTER)
S_BOLDC  = _style("boldc",  fontName=BOLD,   fontSize=8,  alignment=TA_CENTER)
S_BOLDR  = _style("boldr",  fontName=BOLD,   fontSize=8,  alignment=TA_RIGHT)
S_SUBTITLE_BOX = _style("subbox", fontName=BOLD, fontSize=9, alignment=TA_CENTER,
                         borderPadding=2)


def _grid():
    return [
        ("BOX",           (0, 0), (-1, -1), 0.5,  colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 0.25, colors.black),
        ("FONTNAME",      (0, 0), (-1, -1), NORMAL),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def generate_invoice(invoice_no, company, sale_data, resolved_items, gst_applied, gst_rate_list=None,
                     output_path=None):
    """
    invoice_no     : str  e.g. 'SOL-A3F9C2B14D08'
    company        : dict from company_settings
    sale_data      : dict — subtotal, gst_amount, total_amount, buyer_name,
                     buyer_address, payment_mode, destination, vehicle_no,
                     driver_name, discount
    resolved_items : list of dicts, each with keys:
                     item, qty, unit_price, gst_rate, line_base, line_gst, line_total
    gst_applied    : bool
    gst_rate_list  : list of floats from gst_rates table (sorted asc)
    """
    if gst_rate_list is None:
        gst_rate_list = [0, 2.5, 6, 9, 14, 18, 28]
    if output_path is None:
        year = datetime.now().year
        output_path = os.path.join("invoices", str(year), f"{invoice_no}.pdf")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    L = R = T = B = 10 * mm
    PAGE_W, PAGE_H = A4
    cw = PAGE_W - L - R

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=L, rightMargin=R, topMargin=T, bottomMargin=B,
    )

    story = []
    co_name  = company.get("company_name", "")
    co_gstin = company.get("gstin", "")
    inv_date = datetime.now().strftime("%d-%m-%Y")

    payment_mode = sale_data.get("payment_mode", "")
    destination  = sale_data.get("destination",  "")
    vehicle_no   = sale_data.get("vehicle_no",   "")
    driver_name  = sale_data.get("driver_name",  "")
    buyer_name   = sale_data.get("buyer_name",   "")
    buyer_addr   = sale_data.get("buyer_address","")
    discount     = float(sale_data.get("discount", 0) or 0)

    # -----------------------------------------------------------------------
    # 1. Header
    # -----------------------------------------------------------------------
    # Company header block — matches template exactly
    story.append(Paragraph(co_name, S_TITLE))
    if company.get("address"):
        story.append(Paragraph(company["address"], S_SUB))
    if company.get("phone"):
        story.append(Paragraph(f"Mobile – {company['phone']}", S_SUB))
    if co_gstin:
        story.append(Paragraph(f"GSTIN/UIN:  {co_gstin}", S_SUB))
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph("GST  INVOICE", S_SUBTITLE_BOX))
    story.append(Spacer(1, 2 * mm))

    # -----------------------------------------------------------------------
    # 2. Meta table
    # -----------------------------------------------------------------------
    meta_cols = [cw*0.26, cw*0.22, cw*0.16, cw*0.18, cw*0.18]

    meta_data = [
        [Paragraph(co_name, S_LABEL),
         Paragraph("INVOICE No.:-", S_LABEL), Paragraph(invoice_no, S_NORMAL),
         Paragraph("Date :-", S_LABEL),       Paragraph(inv_date, S_NORMAL)],

        ["",
         Paragraph("Delivery Note :-", S_LABEL), "",
         Paragraph("Mode of Payment :-", S_LABEL), Paragraph(payment_mode, S_NORMAL)],

        ["",
         Paragraph("Buyer's Order No.:-", S_LABEL), "",
         Paragraph("Date :-", S_LABEL), ""],

        ["",
         Paragraph("Dispatch Document No.:-", S_LABEL), "",
         Paragraph("Date :-", S_LABEL), ""],

        ["",
         Paragraph("Dispatch through :-", S_LABEL), "",
         Paragraph("Destination :-", S_LABEL), Paragraph(destination, S_NORMAL)],

        [Paragraph("<b>Consignee</b>", S_LABEL),
         Paragraph("Buyer (if other than consignee)  Same  <b>GSTIN/UIN</b>", S_LABEL),
         "",
         Paragraph("Vehicle no:-", S_LABEL), Paragraph(vehicle_no, S_NORMAL)],

        [Paragraph(buyer_name, S_NORMAL),
         "", "",
         Paragraph("Driver's Name:-", S_LABEL), Paragraph(driver_name, S_NORMAL)],

        [Paragraph(buyer_addr, S_NORMAL),
         "", "",
         Paragraph("Others if any:-", S_LABEL), ""],

        [Paragraph(f"<b>GSTIN/UIN:-</b>  {co_gstin}", S_NORMAL),
         "", "", "", ""],
    ]

    meta_style = _grid() + [
        ("SPAN", (1, 5), (2, 5)),
        ("SPAN", (1, 6), (2, 6)),
        ("SPAN", (1, 7), (2, 7)),
        ("SPAN", (0, 8), (4, 8)),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EEEEEE")),
        ("FONTNAME",   (0, 0), (0, 0), BOLD),
    ]

    story.append(Table(meta_data, colWidths=meta_cols,
                       style=TableStyle(meta_style)))
    story.append(Spacer(1, 1 * mm))

    # -----------------------------------------------------------------------
    # 3. Line items
    # -----------------------------------------------------------------------
    total_amt  = float(sale_data.get("total_amount", 0))

    items_list = []
    for sl, r in enumerate(resolved_items, start=1):
        items_list.append({
            "sl":         sl,
            "name":       r["item"].get("name", ""),
            "hsn":        r["item"].get("hsn_code", "") or "",
            "unit_price": r["unit_price"],
            "qty":        r["qty"],
            "g_value":    r["line_base"],
            "gst_rate":   r["gst_rate"],
            "gst_amount": r["line_gst"],
            "line_total": r["line_total"],
        })

    gst_amount = sum(r["line_gst"]  for r in resolved_items)
    g_value    = sum(r["line_base"] for r in resolved_items)
    final_total = round(total_amt - discount, 2)

    ic = [cw*0.05, cw*0.28, cw*0.10, cw*0.09,
          cw*0.05, cw*0.11, cw*0.08, cw*0.12, cw*0.12]

    item_rows = [[
        Paragraph("Sl N",                 S_BOLDC),
        Paragraph("Description of Goods", S_BOLDC),
        Paragraph("HSN/SAC",              S_BOLDC),
        Paragraph("Amount",               S_BOLDC),
        Paragraph("Qty",                  S_BOLDC),
        Paragraph("G. Value",             S_BOLDC),
        Paragraph("GST%",                 S_BOLDC),
        Paragraph("Tax Amount",           S_BOLDC),
        Paragraph("Amount",               S_BOLDC),
    ]]

    for it in items_list:
        item_rows.append([
            Paragraph(str(it["sl"]),             S_CENTER),
            Paragraph(it["name"],                S_NORMAL),
            Paragraph(it["hsn"],                 S_CENTER),
            Paragraph(f"{it['unit_price']:.2f}", S_RIGHT),
            Paragraph(str(it["qty"]),            S_CENTER),
            Paragraph(f"{it['g_value']:.2f}",    S_RIGHT),
            Paragraph(f"{it['gst_rate']:.0f}%",  S_CENTER),
            Paragraph(f"{it['gst_amount']:.2f}", S_RIGHT),
            Paragraph(f"{it['line_total']:.2f}", S_RIGHT),
        ])

    # Discount row — only shown if discount > 0
    n_data = len(items_list)
    extra_rows = 0
    if discount > 0:
        item_rows.append([
            "", Paragraph("Round Off", S_NORMAL), "", "", "", "", "", "",
            Paragraph(f"-{discount:.2f}", S_RIGHT),
        ])
        extra_rows = 1

    # Total row
    item_rows.append([
        "", Paragraph("<b>Total</b>", S_BOLDC), "", "", "",
        Paragraph(f"{g_value:.2f}",    S_BOLDR),
        "",
        Paragraph(f"{gst_amount:.2f}", S_BOLDR),
        Paragraph(f"{final_total:.2f}", S_BOLDR),
    ])

    items_style = _grid() + [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDDDDD")),
        ("FONTNAME",   (0, 0), (-1, 0), BOLD),
        ("SPAN", (0, n_data + extra_rows + 1), (1, n_data + extra_rows + 1)),  # Total label
    ]
    if discount > 0:
        items_style += [
            ("SPAN", (0, n_data + 1), (1, n_data + 1)),  # Discount label
            ("TEXTCOLOR", (8, n_data + 1), (8, n_data + 1), colors.HexColor("#DC2626")),
        ]

    story.append(Table(item_rows, colWidths=ic,
                       style=TableStyle(items_style)))
    story.append(Spacer(1, 1 * mm))

    # -----------------------------------------------------------------------
    # 4. Amount in words
    # -----------------------------------------------------------------------
    try:
        words = num2words(int(final_total), lang="en_IN").upper()
    except Exception:
        words = ""

    story.append(Table(
        [[Paragraph(
            f"<b>Total Amount Chargeable in INR (in words) –</b>  {words} ONLY",
            S_NORMAL)]],
        colWidths=[cw], style=TableStyle(_grid())
    ))
    story.append(Spacer(1, 1 * mm))

    # -----------------------------------------------------------------------
    # 5. GST breakdown — per rate across all items
    #    gst_rate_list comes from DB (gst_rates table), already sorted ascending
    # -----------------------------------------------------------------------
    gst_rates = [str(r) for r in sorted(gst_rate_list)]
    n_rates   = len(gst_rates)

    gst_by_rate = {}
    if gst_applied:
        for r in resolved_items:
            key = float(r["gst_rate"])
            gst_by_rate[key] = gst_by_rate.get(key, 0) + r["line_gst"]

    def igst_val(r):
        amt = gst_by_rate.get(float(r), 0)
        return f"{amt:.2f}" if amt else ""

    def cgst_val(r):
        amt = gst_by_rate.get(float(r), 0)
        return f"{amt/2:.2f}" if amt else ""

    label_w = cw * 0.12
    rate_w  = (cw - label_w) / n_rates

    gst_rows = [
        [""] + [Paragraph("GST %", S_BOLDC)] + [""] * (n_rates - 1),
        [""] + [Paragraph(r, S_CENTER) for r in gst_rates],
        [Paragraph("IGST", S_LABEL)] + [Paragraph(igst_val(r), S_CENTER) for r in gst_rates],
        [Paragraph("CGST", S_LABEL)] + [Paragraph(cgst_val(r), S_CENTER) for r in gst_rates],
        [Paragraph("SGST", S_LABEL)] + [Paragraph(cgst_val(r), S_CENTER) for r in gst_rates],
        [Paragraph("CESS", S_LABEL)] + [""] * n_rates,
        [""]                         + [""] * n_rates,
    ]

    gst_style = _grid() + [
        ("SPAN",       (1, 0), (n_rates, 0)),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#EEEEEE")),
    ]

    story.append(Table(gst_rows, colWidths=[label_w] + [rate_w]*n_rates,
                       style=TableStyle(gst_style)))
    story.append(Spacer(1, 1 * mm))

    # -----------------------------------------------------------------------
    # 6. Bank details + signatory
    # -----------------------------------------------------------------------
    bank_text = (
        f"Company's Bank Details  Bank Name : {company.get('bank_name','')}"
        f"   A/c No : {company.get('account_no','')}<br/>"
        f"IFS Code : {company.get('ifsc','')}   "
        f"Branch : {company.get('branch','')}   "
        f"PIN Code : {company.get('pin_code','')}"
    )

    story.append(Table(
        [[Paragraph(bank_text, S_NORMAL),
          Paragraph(f"<b>For {co_name}</b>", S_RIGHT)]],
        colWidths=[cw*0.6, cw*0.4], style=TableStyle(_grid())
    ))
    story.append(Table(
        [[Paragraph("SUBJECT TO THRISSUR JURISDICTION", S_NORMAL),
          Paragraph("<b>Authorised Signatory</b>", S_RIGHT)]],
        colWidths=[cw*0.6, cw*0.4], style=TableStyle(_grid())
    ))
    story.append(Spacer(1, 2 * mm))

    # -----------------------------------------------------------------------
    # 7. Footer
    # -----------------------------------------------------------------------
    story.append(Paragraph(
        "This is a computer generated invoice&nbsp;&nbsp;&nbsp;&nbsp;E &amp; OE",
        S_CENTER
    ))

    doc.build(story)
    return output_path
