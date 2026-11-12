"""
Generate ScamGuard AI Weekly Progress Record Document (.docx & .pdf)
Replicates the exact layout, styling, typography, table structure, and single-page format
of 'thesis/Weekly_Progress_Record_Filled.pdf'.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=40, bottom=40, left=70, right=70):
    """Set padding in dxa (1 pt = 20 dxa)"""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>\n'
        f'  <w:top w:w="{top}" w:type="dxa"/>\n'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>\n'
        f'  <w:left w:w="{left}" w:type="dxa"/>\n'
        f'  <w:right w:w="{right}" w:type="dxa"/>\n'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def create_document():
    doc = docx.Document()
    
    # Page Setup: A4, 0.75 in margins
    section = doc.sections[0]
    section.page_width = Inches(8.27)   # A4 width (210 mm)
    section.page_height = Inches(11.69) # A4 height (297 mm)
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    
    # 1. Document Title: B.Tech Project – Weekly Progress Record
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.paragraph_format.line_spacing = 1.0
    
    run_title = p_title.add_run("B.Tech Project – Weekly Progress Record")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(13)
    run_title.font.bold = True
    
    # 2. Student Metadata Line: Student Name: Revelli Tharun        Admission No.: 23JE0807
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(8)
    p_meta.paragraph_format.line_spacing = 1.0
    p_meta.paragraph_format.tab_stops.add_tab_stop(Inches(6.77), WD_TAB_ALIGNMENT.RIGHT)
    
    run_name = p_meta.add_run("Student Name: Revelli Tharun\t")
    run_name.font.name = "Times New Roman"
    run_name.font.size = Pt(10.5)
    run_name.font.bold = True
    
    run_adm = p_meta.add_run("Admission No.: 23JE0807")
    run_adm.font.name = "Times New Roman"
    run_adm.font.size = Pt(10.5)
    run_adm.font.bold = True
    
    # 3. Weekly Progress Table: 15 rows (1 Header + 14 Weeks), 4 Columns
    entries = [
        ("07/08/2026", "Project allocation and literature survey on mobile social engineering attacks. Analyzed smishing and vishing evasion techniques, adversarial Cyrillic homoglyphs, and zero-width spaces."),
        ("14/08/2026", "Reviewed existing mobile security tools and SMS keyword blockers. Identified core research gaps: high battery/CPU overhead, cloud privacy violations on personal chats, and preview truncation."),
        ("21/08/2026", "Formulated system functional and non-functional requirements. Defined the Mobile Security Trilemma (sub-millisecond triage, zero-knowledge interpersonal privacy, and high ML accuracy)."),
        ("28/08/2026", "Designed two-stage Edge-Cloud Sentinel architecture: Stage 1 on-device edge triage filter and Stage 2 deep cloud transformer NLP forensics. Selected Python FastAPI and Android Kotlin stacks."),
        ("04/09/2026", "Designed and dimensioned space-efficient Bloom filter using MurmurHash3 (k=7 hash functions) to hold 50,000 malicious phishing domains within an 85 KB memory footprint for sub-0.05 ms lookup."),
        ("11/09/2026", "Curated and preprocessed empirical benchmark dataset of 1,124 real-world communication payloads. Formulated feature extraction pipeline and evaluated pre-trained transformer architectures."),
        ("18/09/2026", "Trained and calibrated DeBERTa-v3 and MiniLM models with disentangled attention. Built soft-voting ensemble combining NLP confidence with domain forensics (spoofed brands, risky TLDs)."),
        ("25/09/2026", "Developed asynchronous FastAPI REST microservice (/api/v1/detect, /health). Integrated OpenAI Whisper acoustic transcription pipeline for speech-to-text processing of voice call scam lures."),
        ("01/10/2026", "Built responsive dark-themed SOC web dashboard (localhost:8000) for real-time risk gauges, threat category breakdown radars, token attributions, and live visual defense demonstrations."),
        ("09/10/2026", "Developed native Android client (com.scamguard.app) in Kotlin. Implemented SmsReceiver for telephony broadcasts and NotificationListenerService for passive status-bar message interception."),
        ("16/10/2026", "Implemented Dual-Ingestion paradigm: Android Share Sheet (ACTION_SEND) for authoritative verification and one-tap Clipboard Paste-and-Scan. Integrated local SQLite/Prefs scan history."),
        ("23/10/2026", "Faculty review rebuttal: Engineered automated truncation detection for clipped previews ('...'), and active e-commerce noise blacklist (Amazon, Meesho, Swiggy) achieving 90.3% local request reduction."),
        ("06/11/2026", "Implemented On-Screen Chat Accessibility fallback for Notifications-OFF scenario and Contact Whitelist Privacy Shield. Validated 100-notification concurrent burst queue with 0 ANRs."),
        ("12/11/2026", "Conducted physical hardware benchmarking on OPPO K13 5G (Android 16, 0.24-0.56 ms latency). Finalized thesis report, 11-slide presentation deck with IIT ISM logo, and progress documentation.")
    ]
    
    table = doc.add_table(rows=15, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    
    # Exact column widths matching reference:
    # Col 0 (Date): 0.98 in
    # Col 1 (Work Done): 4.10 in
    # Col 2 (Student Signature): 0.82 in
    # Col 3 (Supervisor signature): 0.87 in
    # Total = 6.77 in
    col_widths = [Inches(0.98), Inches(4.10), Inches(0.82), Inches(0.87)]
    
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width
            
    # Headers
    headers = ["Date", "Work Done", "Student\nSignature", "Supervisor\nsignature"]
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_margins(hdr_cells[i], top=50, bottom=50, left=60, right=60)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(title)
        run.font.name = "Times New Roman"
        run.font.size = Pt(9.5)
        run.font.bold = True
        
    # Data Rows
    for r_idx, (date_str, work_text) in enumerate(entries):
        row_cells = table.rows[r_idx + 1].cells
        
        # Col 0: Date
        c0 = row_cells[0]
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_margins(c0, top=35, bottom=35, left=50, right=50)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.0
        r0 = p0.add_run(date_str)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(9.0)
        r0.font.bold = True
        
        # Col 1: Work Done
        c1 = row_cells[1]
        c1.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_margins(c1, top=35, bottom=35, left=60, right=60)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.05
        r1 = p1.add_run(work_text)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(8.5)
        r1.font.bold = False
        
        # Col 2 & 3: Empty for Signatures
        for c_idx in [2, 3]:
            c = row_cells[c_idx]
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(c, top=35, bottom=35, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            
    out_docx = "thesis/ScamGuard_AI_Weekly_Progress_Record.docx"
    doc.save(out_docx)
    print(f"Successfully generated DOCX: {out_docx}")

if __name__ == "__main__":
    create_document()
