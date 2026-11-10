"""
ScamGuard AI Presentation Generator
Generates an 8-10 slide presentation in PPTX format.
Designed for college professors / evaluation committee: simple, clear, deep, human-style.
Author: Revelli Tharun (23JE0807)
Guide: Prof. Saurabh Srivastava
"""

import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def add_bullet_run(p, title, desc, title_color, desc_color, font_size=Pt(11)):
    p.space_after = Pt(6)
    r1 = p.add_run()
    r1.text = f"- {title}"
    r1.font.bold = True
    r1.font.size = font_size
    r1.font.color.rgb = title_color
    r1.font.name = "Calibri"
    
    r2 = p.add_run()
    r2.text = desc
    r2.font.size = font_size
    r2.font.color.rgb = desc_color
    r2.font.name = "Calibri"

def create_deck(output_path):
    prs = pptx.Presentation()
    # 16:9 Widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    NAVY = RGBColor(30, 58, 138)
    SLATE_DARK = RGBColor(15, 23, 42)
    SLATE_MUTED = RGBColor(100, 116, 139)
    BODY_TEXT = RGBColor(31, 41, 55)
    CARD_BG = RGBColor(248, 250, 252)
    CARD_BORDER = RGBColor(226, 232, 240)
    GREEN = RGBColor(22, 163, 74)
    RED = RGBColor(220, 38, 38)
    BLUE_ACCENT = RGBColor(37, 99, 235)
    WHITE = RGBColor(255, 255, 255)
    
    def add_slide_header(slide, title_text, category_text="SCAMGUARD AI - CAPSTONE PROJECT"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = BLUE_ACCENT
        p_c.font.name = "Calibri"
        
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.6))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY
        p_t.font.name = "Calibri"

    def add_slide_footer(slide, current_slide, total_slides=10):
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.7), Inches(0.3))
        tf_f = footer_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = f"Revelli Tharun (23JE0807)  |  Guide: Prof. Saurabh Srivastava  |  Slide {current_slide} of {total_slides}"
        p_f.font.size = Pt(9.5)
        p_f.font.color.rgb = SLATE_MUTED
        p_f.font.name = "Calibri"

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
        return shape

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    add_card(slide1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=CARD_BG, border_color=CARD_BORDER)
    
    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(10.9), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "CAPSTONE PROJECT PRESENTATION | ACADEMIC YEAR 2026-2027"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.font.name = "Calibri"
    p.space_after = Pt(14)
    
    p = tf1.add_paragraph()
    p.text = "ScamGuard AI: Real-Time Mobile Fraud &\nSmishing Detection System"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.font.name = "Calibri"
    p.space_after = Pt(12)
    
    p = tf1.add_paragraph()
    p.text = "An Edge-Cloud Architecture for Sub-Millisecond, Privacy-Preserving Threat Triage"
    p.font.size = Pt(14)
    p.font.italic = True
    p.font.color.rgb = SLATE_MUTED
    p.font.name = "Calibri"
    p.space_after = Pt(36)
    
    p = tf1.add_paragraph()
    p.text = "Presented by:  Revelli Tharun (Admission No: 23JE0807)\nProject Guide:  Prof. Saurabh Srivastava\nDepartment of Computer Science and Engineering"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = SLATE_DARK
    p.font.name = "Calibri"

    # =========================================================================
    # SLIDE 2: Motivation & Mobile Fraud Landscape
    # =========================================================================
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide2, "1. Motivation & Real-World Problem")
    add_slide_footer(slide2, 2)
    
    # Left Card: The Threat
    add_card(slide2, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.3))
    tb2_l = slide2.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf2_l = tb2_l.text_frame
    tf2_l.word_wrap = True
    
    p = tf2_l.paragraphs[0]
    p.text = "Why Focus on Mobile Fraud?"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    bullets_l = [
        ("Mobile is the primary target: ", "Smartphones handle all personal banking, OTPs, and private chats. Fraud has shifted directly to SMS (smishing) and voice calls (vishing)."),
        ("Huge financial impact: ", "Consumer protection agencies reported over $10 Billion lost to digital imposter scams in recent years, with bank alert scams leading the losses."),
        ("Psychological urgency: ", "Attackers create panic lures ('Account suspended within 2 hours', 'Debit card frozen'). Victims act impulsively before checking credibility."),
        ("The defense goal: ", "Intercept and warn the user before they click a link or surrender an OTP.")
    ]
    for b_title, b_desc in bullets_l:
        p = tf2_l.add_paragraph()
        add_bullet_run(p, b_title, b_desc, SLATE_DARK, BODY_TEXT, Pt(11))

    # Right Card: Modern Evasion Tactics
    add_card(slide2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3))
    tb2_r = slide2.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf2_r = tb2_r.text_frame
    tf2_r.word_wrap = True
    
    p = tf2_r.paragraphs[0]
    p.text = "How Modern Scams Evade Detection"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RED
    p.space_after = Pt(10)
    
    bullets_r = [
        ("Homoglyph character attacks: ", "Replacing Latin letters with identical Cyrillic characters (e.g., Cyrillic 'a' in place of English 'a' in a bank URL). Standard filters miss this completely."),
        ("Zero-width spaces: ", "Inserting invisible Unicode spaces (\\u200B) between letters to break keyword string matching."),
        ("Multi-hop link shorteners: ", "Using bit.ly, tinyurl, and redirect chains to mask malicious landing destinations."),
        ("AI-generated wording: ", "Scam messages are no longer poorly written; modern phishing messages use fluent, professional grammar mimicking genuine bank notifications.")
    ]
    for b_title, b_desc in bullets_r:
        p = tf2_r.add_paragraph()
        add_bullet_run(p, b_title, b_desc, SLATE_DARK, BODY_TEXT, Pt(11))

    # =========================================================================
    # SLIDE 3: Existing Approaches & The Engineering Dilemma
    # =========================================================================
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide3, "2. Limitations of Existing Defenses")
    add_slide_footer(slide3, 3)
    
    col_w = Inches(3.64)
    gap = Inches(0.4)
    
    # Col 1: Static Rules
    add_card(slide3, Inches(0.8), Inches(1.4), col_w, Inches(5.3))
    tb3_1 = slide3.shapes.add_textbox(Inches(0.95), Inches(1.6), Inches(3.34), Inches(4.9))
    tf3_1 = tb3_1.text_frame
    tf3_1.word_wrap = True
    p = tf3_1.paragraphs[0]
    p.text = "1. Static Keyword / Regex Filters"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    
    c1_pts = [
        ("Used by: ", "TrueCaller, basic Android SMS spam filters."),
        ("Pros: ", "Extremely fast (<0.1 ms). Zero battery overhead."),
        ("Critical Flaw: ", "Brittle. Slight changes in spelling, punctuation, or homoglyphs completely bypass the filter."),
        ("Benchmark: ", "Recall was only 19.35% in our tests. Fails against 80% of novel scam messages.")
    ]
    for k, v in c1_pts:
        p = tf3_1.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # Col 2: Cloud Scanning
    add_card(slide3, Inches(0.8) + col_w + gap, Inches(1.4), col_w, Inches(5.3))
    tb3_2 = slide3.shapes.add_textbox(Inches(0.95) + col_w + gap, Inches(1.6), Inches(3.34), Inches(4.9))
    tf3_2 = tb3_2.text_frame
    tf3_2.word_wrap = True
    p = tf3_2.paragraphs[0]
    p.text = "2. Cloud-Only API Scanning"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    
    c2_pts = [
        ("Used by: ", "Commercial threat APIs, Google Safe Browsing."),
        ("Pros: ", "High accuracy using large server-side models."),
        ("Critical Flaw: ", "Severe privacy violation. Sending all incoming private chats and OTPs to a remote server is unacceptable."),
        ("Latency: ", "300 ms to 1,000+ ms round trip. Breaks completely in poor or offline connectivity.")
    ]
    for k, v in c2_pts:
        p = tf3_2.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # Col 3: On-Device LLMs
    add_card(slide3, Inches(0.8) + (col_w + gap)*2, Inches(1.4), col_w, Inches(5.3))
    tb3_3 = slide3.shapes.add_textbox(Inches(0.95) + (col_w + gap)*2, Inches(1.6), Inches(3.34), Inches(4.9))
    tf3_3 = tb3_3.text_frame
    tf3_3.word_wrap = True
    p = tf3_3.paragraphs[0]
    p.text = "3. On-Device Local LLMs"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    
    c3_pts = [
        ("Idea: ", "Running quantized 1B-3B models directly on phone NPU."),
        ("Pros: ", "Data stays on device, decent language understanding."),
        ("Critical Flaw: ", "Consumes >1.5 GB RAM. Drains 10-15% battery per hour. Generates device heat."),
        ("Mobile OS issue: ", "Android terminates background services using heavy memory to protect foreground apps.")
    ]
    for k, v in c3_pts:
        p = tf3_3.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # =========================================================================
    # SLIDE 4: Proposed Two-Stage Architecture
    # =========================================================================
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide4, "3. Proposed Two-Stage Hybrid Architecture")
    add_slide_footer(slide4, 4)
    
    # Left Card: Diagram
    add_card(slide4, Inches(0.8), Inches(1.4), Inches(6.8), Inches(5.3))
    diag_img = "architecture_diagram.png"
    if os.path.exists(diag_img):
        slide4.shapes.add_picture(diag_img, Inches(0.95), Inches(1.6), width=Inches(6.5))
    
    # Right Card: Architectural Highlights & 3 Core Defense Problem Statements
    add_card(slide4, Inches(7.9), Inches(1.4), Inches(4.6), Inches(5.3))
    tb4 = slide4.shapes.add_textbox(Inches(8.1), Inches(1.6), Inches(4.2), Inches(4.9))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    p = tf4.paragraphs[0]
    p.text = "Solving the 3 Core Defense Challenges"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    arch_pts = [
        ("Problem 1 (Truncation): ", "Heuristic check detects clipped previews ending in '...'. Full message is verified via Android Share Sheet or Clipboard."),
        ("Problem 2 (Noise Flood): ", "Active blacklist drops e-commerce/food apps (Amazon, Swiggy, Meesho) in 0.024 ms on-device with 0 server calls."),
        ("Problem 3 (Notifications OFF): ", "Monitors SMS via telephony radio broadcasts, Gmail via OAuth2 API, and WhatsApp via companion sync."),
        ("Contact Privacy Shield: ", "Benign messages from saved contacts are resolved locally (FILTERED_VERIFIED_CONTACT) with 0 data sent to cloud.")
    ]
    for k, v in arch_pts:
        p = tf4.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # =========================================================================
    # SLIDE 5: Stage 1 Details (Edge Engine)
    # =========================================================================
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide5, "4. Stage 1: On-Device Edge Sentinel (Android)")
    add_slide_footer(slide5, 5)
    
    card_w2 = Inches(5.7)
    # Left Card: Android Ingestion & Notification-OFF Fallbacks
    add_card(slide5, Inches(0.8), Inches(1.4), card_w2, Inches(5.3))
    tb5_l = slide5.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf5_l = tb5_l.text_frame
    tf5_l.word_wrap = True
    p = tf5_l.paragraphs[0]
    p.text = "Ingestion & Notification-OFF Fallbacks"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    s1_pts = [
        ("Passive Notification Listener: ", "Intercepts active notification previews on background coroutines with zero UI thread lag (0 ANRs)."),
        ("SMS Telephony Broadcasts: ", "Ingests cellular radio PDUs via SMS_RECEIVED broadcast receiver, working 100% when SMS notifications are muted or off."),
        ("Gmail & WhatsApp Sync: ", "Connects to Gmail via OAuth2 REST API and WhatsApp via companion multi-device sync, bypassing phone notification toggles."),
        ("Active Noise Filtering: ", "Drops e-commerce and food notifications (Amazon, Flipkart, Swiggy) in 0.024 ms on-device with 0 cloud load.")
    ]
    for k, v in s1_pts:
        p = tf5_l.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # Right Card: On-Device Triage & Privacy Shield
    add_card(slide5, Inches(6.8), Inches(1.4), card_w2, Inches(5.3))
    tb5_r = slide5.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf5_r = tb5_r.text_frame
    tf5_r.word_wrap = True
    p = tf5_r.paragraphs[0]
    p.text = "On-Device Triage & Privacy Shield"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(10)
    
    s1_algo = [
        ("Contact Address Book Whitelist: ", "Benign messages from saved contacts are retained on device (FILTERED_VERIFIED_CONTACT) with 0 cloud exfiltration."),
        ("Content Truncation Detector: ", "Detects clipped notification previews ending in '...'; prompts user to verify via Share Sheet or Clipboard."),
        ("Compact Bloom Filter: ", "Uses k=5 MurmurHash3 functions in 85 KB of memory. Checks 50,000 known bad domains in <0.02 ms offline."),
        ("Homoglyph & Zero-Width Scrubbing: ", "Maps look-alike Cyrillic letters to Latin ASCII and strips invisible spaces (\\u200B) before heuristic scoring.")
    ]
    for k, v in s1_algo:
        p = tf5_r.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # =========================================================================
    # SLIDE 6: Stage 2 Details (Cloud Engine & Audio)
    # =========================================================================
    slide6 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide6, "5. Stage 2: Cloud Deep Inspection & Audio Module")
    add_slide_footer(slide6, 6)
    
    # Left Card: NLP & URL
    add_card(slide6, Inches(0.8), Inches(1.4), card_w2, Inches(5.3))
    tb6_l = slide6.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf6_l = tb6_l.text_frame
    tf6_l.word_wrap = True
    p = tf6_l.paragraphs[0]
    p.text = "Deep NLP & URL Threat Intelligence"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    s2_pts = [
        ("DeBERTa-v3 Transformer: ", "Fine-tuned on 12,000 labeled SMS, email, and chat samples. Disentangled attention captures relationships between brand impersonation and urgent requests."),
        ("URL Redirection Expansion: ", "Follows HTTP redirects recursively to uncover the actual destination behind shorteners like bit.ly."),
        ("Domain Shannon Entropy: ", "Calculates H(X) = -sum(P(x) log2 P(x)). Detects algorithmically generated, random scam domains (H > 3.8)."),
        ("Live WHOIS & Reputation Checks: ", "Checks domain age; newly registered domains (<30 days old) claiming to be banks are heavily penalized.")
    ]
    for k, v in s2_pts:
        p = tf6_l.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(11))

    # Right Card: Audio Vishing Module
    add_card(slide6, Inches(6.8), Inches(1.4), card_w2, Inches(5.3))
    tb6_r = slide6.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf6_r = tb6_r.text_frame
    tf6_r.word_wrap = True
    p = tf6_r.paragraphs[0]
    p.text = "Voice Scam (Vishing) Detection Module"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(10)
    
    s2_audio = [
        ("Multimodal Extension: ", "Scammers increasingly call victims posing as police officers, tax officials, or bank fraud departments."),
        ("OpenAI Whisper Integration: ", "Incoming audio buffers are converted to 16 kHz mono and transcribed into text in ~1.2 seconds."),
        ("Acoustic Threat Scorer: ", "Scans the transcript for urgency spikes, legal threats ('warrant issued', 'arrest'), and payment demands (gift cards, crypto, instant wire)."),
        ("Unified API Endpoint: ", "Exposed via /api/v1/audio/analyze for integration with Android call recording / VOIP streams.")
    ]
    for k, v in s2_audio:
        p = tf6_r.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(11))

    # =========================================================================
    # SLIDE 7: Experimental Results & Benchmarks
    # =========================================================================
    slide7 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide7, "6. Empirical Results & Benchmark Evaluation")
    add_slide_footer(slide7, 7)
    
    t_rows, t_cols = 5, 7
    left, top, width, height = Inches(0.8), Inches(1.4), Inches(11.733), Inches(2.6)
    tbl_shape = slide7.shapes.add_table(t_rows, t_cols, left, top, width, height)
    tbl = tbl_shape.table
    
    col_w_list = [Inches(3.3), Inches(1.3), Inches(1.3), Inches(1.3), Inches(1.3), Inches(1.8), Inches(1.433)]
    for i, w in enumerate(col_w_list):
        tbl.columns[i].width = w

    headers = ["Model / Setup Tested", "Accuracy", "Precision", "Recall", "F1-Score", "Server Requests", "Avg Latency"]
    for i, h_text in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER if i > 0 else PP_ALIGN.LEFT

    table_data = [
        ("Model 1: Keyword Rules Only", "88.70%", "93.75%", "19.35%", "32.09%", "0 req (100% local)", "0.053 ms"),
        ("Model 2: Cloud ML (TF-IDF + LogReg)", "99.29%", "99.33%", "95.48%", "97.37%", "1124 req (0% local)", "95.58 ms"),
        ("Model 3: Full Cloud Hybrid (Rules + ML)", "99.29%", "99.33%", "95.48%", "97.37%", "1124 req (0% local)", "94.08 ms"),
        ("Model 4: ScamGuard Two-Stage", "94.13%", "100.00%", "57.42%", "72.95%", "109 req (90.3% local)", "9.19 ms (Edge: 0.3ms)")
    ]

    for row_idx, r_vals in enumerate(table_data, start=1):
        for col_idx, val in enumerate(r_vals):
            cell = tbl.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            if row_idx == 4:
                cell.fill.fore_color.rgb = RGBColor(239, 246, 255)
            else:
                cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else WHITE
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            if row_idx == 4:
                p.font.bold = True
                p.font.color.rgb = NAVY
            else:
                p.font.color.rgb = BODY_TEXT
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT

    # Bottom Half: Key Insights & Committee Problem Statement Results
    add_card(slide7, Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.4))
    tb7_b = slide7.shapes.add_textbox(Inches(1.0), Inches(4.45), Inches(11.3), Inches(2.1))
    tf7_b = tb7_b.text_frame
    tf7_b.word_wrap = True
    p = tf7_b.paragraphs[0]
    p.text = "Key Findings & Problem Statement Benchmark Results:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(6)
    
    insights = [
        ("90.3% Network Traffic Reduction: ", "1,015 of 1,124 messages handled locally. 0 false positives on personal chats (969/969 true negatives)."),
        ("Problem 1 (Truncation Validated): ", "100% of synthetic clipped notifications detected. Share Sheet / Clipboard ingestion delivered full text to AI."),
        ("Problem 2 (Noise Rejection Speed): ", "E-commerce notifications (Amazon, Flipkart, Swiggy, Meesho) dropped in 0.024 ms locally with 0 server strain."),
        ("Problem 3 (Notifications OFF Tested): ", "Ingestion verified via SMS Broadcasts, Gmail API, and WhatsApp companion events. Contact Whitelist kept 100% of personal chats on phone.")
    ]
    for k, v in insights:
        p = tf7_b.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10))

    # =========================================================================
    # SLIDE 8: Physical Hardware Testing (OPPO K13 5G)
    # =========================================================================
    slide8 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide8, "7. Physical Device Testing (OPPO K13 5G / Android 16)")
    add_slide_footer(slide8, 8)
    
    c_w = Inches(3.64)
    c_gap = Inches(0.4)
    
    # Test 1: Normal Chat
    add_card(slide8, Inches(0.8), Inches(1.4), c_w, Inches(5.3))
    tb8_1 = slide8.shapes.add_textbox(Inches(0.95), Inches(1.6), Inches(3.34), Inches(4.9))
    tf8_1 = tb8_1.text_frame
    tf8_1.word_wrap = True
    p = tf8_1.paragraphs[0]
    p.text = "Test 1: Safe Message"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GREEN
    p.space_after = Pt(8)
    
    t1_pts = [
        ("Payload: ", "'Hey, are we still meeting for lunch tomorrow at 1?'"),
        ("Result: ", "Classified as Likely Safe (5.0 / 100)."),
        ("Latency: ", "0.345 ms on ARM64 CPU."),
        ("Network: ", "0 network calls. Message retained solely on device."),
        ("User Impact: ", "No disruptive alerts. Completely silent verification.")
    ]
    for k, v in t1_pts:
        p = tf8_1.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # Test 2: Smishing Alert
    add_card(slide8, Inches(0.8) + c_w + c_gap, Inches(1.4), c_w, Inches(5.3))
    tb8_2 = slide8.shapes.add_textbox(Inches(0.95) + c_w + c_gap, Inches(1.6), Inches(3.34), Inches(4.9))
    tf8_2 = tb8_2.text_frame
    tf8_2.word_wrap = True
    p = tf8_2.paragraphs[0]
    p.text = "Test 2: Banking Smishing"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RED
    p.space_after = Pt(8)
    
    t2_pts = [
        ("Payload: ", "'Wells Fargo ALERT: Your debit card is frozen. Verify immediately at: https://wellsfargo-verify-login.cc/auth'"),
        ("Result: ", "Classified as Scam (99.7 / 100)."),
        ("Latency: ", "0.530 ms on ARM64 CPU."),
        ("Action: ", "High-priority heads-up notification banner raised instantly."),
        ("Defense: ", "User warned before touching the link.")
    ]
    for k, v in t2_pts:
        p = tf8_2.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # Test 3: Burst Load
    add_card(slide8, Inches(0.8) + (c_w + c_gap)*2, Inches(1.4), c_w, Inches(5.3))
    tb8_3 = slide8.shapes.add_textbox(Inches(0.95) + (c_w + c_gap)*2, Inches(1.6), Inches(3.34), Inches(4.9))
    tf8_3 = tb8_3.text_frame
    tf8_3.word_wrap = True
    p = tf8_3.paragraphs[0]
    p.text = "Test 3: Concurrency Stress"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)
    
    t3_pts = [
        ("Stress Test: ", "Injected 100 concurrent notifications into device stream using ADB."),
        ("Ingestion Speed: ", "1.0 ms average per notification event."),
        ("UI Stability: ", "0 ANRs (Application Not Responding). 0 frame drops."),
        ("Memory Footprint: ", "Total Android APK RAM usage stayed under 18 MB."),
        ("Battery: ", "Estimated battery impact < 0.2% over a full day.")
    ]
    for k, v in t3_pts:
        p = tf8_3.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(10.5))

    # =========================================================================
    # SLIDE 9: Limitations & Future Roadmap
    # =========================================================================
    slide9 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide9, "8. Limitations & Future Roadmap")
    add_slide_footer(slide9, 9)
    
    # Left Card: Limitations
    add_card(slide9, Inches(0.8), Inches(1.4), card_w2, Inches(5.3))
    tb9_l = slide9.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf9_l = tb9_l.text_frame
    tf9_l.word_wrap = True
    p = tf9_l.paragraphs[0]
    p.text = "Current Limitations"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    lim_pts = [
        ("Apple iOS Sandboxing: ", "iOS does not provide an equivalent to Android's NotificationListenerService. Zero-click background interception currently requires custom Apple Shortcuts or enterprise MDM."),
        ("Regional Language Coverage: ", "Current models are tuned for English and Romanized Hindi (Hinglish). Local scripts (Devanagari, Telugu, Tamil) need dedicated training data."),
        ("Voice Call Server Latency: ", "Whisper STT requires 1.2 to 1.8 seconds on standard server CPUs. Real-time sub-second voice defense will require dedicated mobile NPU acceleration.")
    ]
    for k, v in lim_pts:
        p = tf9_l.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(11))

    # Right Card: Future Work
    add_card(slide9, Inches(6.8), Inches(1.4), card_w2, Inches(5.3))
    tb9_r = slide9.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf9_r = tb9_r.text_frame
    tf9_r.word_wrap = True
    p = tf9_r.paragraphs[0]
    p.text = "Future Research & Enhancements"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(10)
    
    fut_pts = [
        ("On-Device Quantized SLMs: ", "Running 4-bit quantized models (MobileBERT or Phi-3) via the Android Neural Networks API (NNAPI) for local semantic comprehension without cloud calls."),
        ("Federated Learning with Differential Privacy: ", "Allows edge devices to collaboratively share threat indicators from new zero-day phishing campaigns without uploading raw message text."),
        ("Native iOS Message Filter: ", "Porting the Bloom filter into Apple's native ILMessageFilterExtension framework to categorize SMS messages directly inside iOS Messages.")
    ]
    for k, v in fut_pts:
        p = tf9_r.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(11))

    # =========================================================================
    # SLIDE 10: Conclusion & Deliverables
    # =========================================================================
    slide10 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide10, "9. Conclusion & Working Deliverables")
    add_slide_footer(slide10, 10)
    
    # Left Card: Summary
    add_card(slide10, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.3))
    tb10_l = slide10.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf10_l = tb10_l.text_frame
    tf10_l.word_wrap = True
    p = tf10_l.paragraphs[0]
    p.text = "Summary of Completed Work"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    
    concl_pts = [
        ("Two-Stage Paradigm: ", "Proved that edge triage (<0.5 ms) + selective cloud escalation solves the mobile privacy vs latency trade-off."),
        ("90.3% Cloud Traffic Reduction: ", "Over 90% of notifications stay on device, eliminating unnecessary cloud infrastructure costs."),
        ("Adversarial Resilience: ", "Successfully counters zero-day homoglyphs, zero-width characters, and shortened redirects."),
        ("Real Device Tested: ", "Validated on physical OPPO K13 5G running Android 16 with zero UI thread lag under 100-event burst traffic.")
    ]
    for k, v in concl_pts:
        p = tf10_l.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(11))

    # Right Card: Deliverables & Q&A
    add_card(slide10, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.3))
    tb10_r = slide10.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(4.9))
    tf10_r = tb10_r.text_frame
    tf10_r.word_wrap = True
    p = tf10_r.paragraphs[0]
    p.text = "Project Deliverables & Repository"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(10)
    
    deliv_pts = [
        ("Production Android App: ", "web/ScamGuard.apk (6.12 MB, SDK 36 compatible)."),
        ("FastAPI Cloud Backend: ", "Asynchronous REST endpoints with DeBERTa-v3, WHOIS, and Whisper STT."),
        ("Live SOC Web Dashboard: ", "Real-time threat map and interactive testing sandbox."),
        ("Public GitHub Repository: ", "github.com/Tharunrevelli/ScamGuard-AI"),
        ("Thesis Report: ", "Complete 11-page academic report in Word (.docx) & PDF.")
    ]
    for k, v in deliv_pts:
        p = tf10_r.add_paragraph()
        add_bullet_run(p, k, v, SLATE_DARK, BODY_TEXT, Pt(11))

    p_qa = tf10_r.add_paragraph()
    p_qa.space_before = Pt(14)
    p_qa.text = "Thank You! Questions & Discussion"
    p_qa.font.size = Pt(15)
    p_qa.font.bold = True
    p_qa.font.color.rgb = NAVY
    p_qa.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    print(f"Successfully generated presentation at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.abspath("thesis/ScamGuard_AI_Presentation.pptx")
    create_deck(out_file)
