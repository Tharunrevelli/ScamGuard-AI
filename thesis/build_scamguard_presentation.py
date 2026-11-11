"""
ScamGuard AI Presentation Builder
Clones the exact reference template from 'CSE Department Scheduler  Ayan Das.pptx'
preserves all background graphics, typography, IIT (ISM) Dhanbad branding,
and replaces all placeholders and diagram slots with ScamGuard AI capstone project content.
"""

import os
import shutil
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def update_text_frame(shape, text, font_size=None, bold=None, color=None):
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    tf.word_wrap = True
    
    # Store original font attributes if possible
    orig_font_name = None
    orig_font_size = None
    orig_font_bold = None
    orig_color = None
    if tf.paragraphs and tf.paragraphs[0].runs:
        r0 = tf.paragraphs[0].runs[0]
        orig_font_name = r0.font.name
        orig_font_size = r0.font.size
        orig_font_bold = r0.font.bold
        if r0.font.color and r0.font.color.type == 1:
            orig_color = r0.font.color.rgb
            
    # Clear and set new text
    paragraphs = text.split("\n")
    tf.text = "" # clears text
    
    for idx, p_text in enumerate(paragraphs):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = p_text
        if orig_font_name:
            run.font.name = orig_font_name
        if font_size:
            run.font.size = font_size
        elif orig_font_size:
            run.font.size = orig_font_size
        if bold is not None:
            run.font.bold = bold
        elif orig_font_bold is not None:
            run.font.bold = orig_font_bold
        if color:
            run.font.color.rgb = color
        elif orig_color:
            run.font.color.rgb = orig_color

def replace_picture_blob(slide, picture_shape, new_image_path):
    if not os.path.exists(new_image_path):
        return
    blip = picture_shape._element.xpath('.//a:blip')[0]
    rEmbed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    part = slide.part.related_part(rEmbed)
    with open(new_image_path, 'rb') as f:
        part._blob = f.read()

def build_presentation():
    ref_path = "thesis/CSE Department Scheduler  Ayan Das.pptx"
    out_pptx = "thesis/ScamGuard_AI_Presentation.pptx"
    logo_path = "thesis/iit_ism_logo.jpg"
    arch_diagram_path = "architecture_diagram.png"
    edge_visual_path = "thesis/edge_triage_visual.png"
    
    shutil.copyfile(ref_path, out_pptx)
    prs = pptx.Presentation(out_pptx)
    print(f"Loaded {len(prs.slides)} slides from template.")
    
    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides[0]
    update_text_frame(s1.shapes[1], "ScamGuard AI", font_size=Pt(36), bold=True)
    update_text_frame(s1.shapes[2], "Real-Time Mobile Fraud & Smishing Detection System", font_size=Pt(18), bold=True)
    update_text_frame(s1.shapes[3], "Presented By:", font_size=Pt(14), bold=True)
    update_text_frame(s1.shapes[4], "Revelli Tharun (23JE0807)", font_size=Pt(15), bold=True)
    update_text_frame(
        s1.shapes[6],
        "Under the guidance of: Prof. Saurabh Srivastava\nDepartment of Computer Science and Engineering | IIT (ISM) Dhanbad\nAcademic Year 2026 – 2027",
        font_size=Pt(13),
        bold=False
    )
    
    # =========================================================================
    # SLIDE 2: Motivation & Problem Statement
    # =========================================================================
    s2 = prs.slides[1]
    update_text_frame(s2.shapes[13], "Motivation & Problem Statement")
    update_text_frame(
        s2.shapes[14],
        "Smartphones are now the primary gateway for personal banking, OTPs, and private chats. "
        "Cybercriminals heavily target mobile users via social engineering (smishing & vishing) causing billions in losses. "
        "Traditional keyword filters fail against modern evasion, while cloud-only scanners leak private conversations."
    )
    update_text_frame(s2.shapes[4], "Modern Evasion", bold=True)
    update_text_frame(s2.shapes[5], "Attackers use Cyrillic homoglyphs ('а' vs 'a'), zero-width spaces, and redirect chains to bypass standard regex filters.")
    update_text_frame(s2.shapes[6], "The Mobile Trilemma", bold=True)
    update_text_frame(s2.shapes[7], "Balancing sub-millisecond triage latency, 100% user privacy, and high detection accuracy on battery-limited phones.")
    update_text_frame(s2.shapes[8], "Panic Urgency", bold=True)
    update_text_frame(s2.shapes[9], "High-pressure alerts ('Account locked within 2 hours') trick victims into acting impulsively before verifying credibility.")
    
    # =========================================================================
    # SLIDE 3: Our Solution & Objectives
    # =========================================================================
    s3 = prs.slides[2]
    update_text_frame(s3.shapes[10], "Our Solution & Objectives")
    update_text_frame(
        s3.shapes[1],
        "An ultra-low-latency edge-cloud sentinel architecture combining on-device fast triage with deep cloud transformer NLP."
    )
    update_text_frame(s3.shapes[3], "Triage: Sub-millisecond on-device edge filter (<0.5 ms) using Bloom filters.")
    update_text_frame(s3.shapes[5], "Protect: 100% zero-knowledge local storage for private interpersonal chats.")
    update_text_frame(s3.shapes[7], "Deep Analysis: Cloud DeBERTa-v3 NLP ensemble + recursive URL redirect forensics.")
    update_text_frame(s3.shapes[9], "Multimodal: OpenAI Whisper speech-to-text for voice scam (vishing) detection.")
    
    # Replace diagram picture on right half of Slide 3 (Shape 11, id=95)
    if os.path.exists(arch_diagram_path):
        replace_picture_blob(s3, s3.shapes[11], arch_diagram_path)
        
    # =========================================================================
    # SLIDE 4: Technology Stack
    # =========================================================================
    s4 = prs.slides[3]
    update_text_frame(s4.shapes[21], "Technology Stack")
    update_text_frame(s4.shapes[6], "Android SDK", bold=True)
    update_text_frame(s4.shapes[7], "Kotlin & Jetpack Coroutines for background sentinel & telephony broadcasts.")
    update_text_frame(s4.shapes[8], "FastAPI", bold=True)
    update_text_frame(s4.shapes[9], "Asynchronous Python 3.11+ REST microservice with sub-50ms cloud endpoints.")
    update_text_frame(s4.shapes[10], "Transformers", bold=True)
    update_text_frame(s4.shapes[11], "Fine-tuned DeBERTa-v3 & MiniLM models with disentangled attention.")
    update_text_frame(s4.shapes[12], "Whisper ASR", bold=True)
    update_text_frame(s4.shapes[13], "Acoustic transcription engine for voice call scam (vishing) triage.")
    update_text_frame(s4.shapes[14], "Bloom Filters", bold=True)
    update_text_frame(s4.shapes[15], "85 KB memory footprint holding 50,000 domains via MurmurHash3.")
    
    # =========================================================================
    # SLIDE 5: System Architecture: Event Pipeline
    # =========================================================================
    s5 = prs.slides[4]
    update_text_frame(s5.shapes[15], "System Architecture: Event Pipeline")
    update_text_frame(s5.shapes[3], "1. Incoming Message\nIntercepted via NotificationListener or SMS Broadcast")
    update_text_frame(s5.shapes[6], "2. Stage 1 Edge Triage\nScans Bloom filter, homoglyphs & rules in <0.5 ms")
    update_text_frame(s5.shapes[7], "Risk Score < 25")
    update_text_frame(s5.shapes[10], "3. Privacy Gate\nSafe personal chats stay 100% on phone (0 network calls)")
    update_text_frame(s5.shapes[12], "4. Cloud Escalation\nAmbiguous/high-risk payloads sent with PII redaction")
    update_text_frame(s5.shapes[14], "5. DeBERTa-v3 Inference\nReturns calibrated 0-100 risk score & warning alert")
    
    # =========================================================================
    # SLIDE 6: Key Feature: Three Defense Problems Solved
    # =========================================================================
    s6 = prs.slides[5]
    update_text_frame(s6.shapes[13], "Key Feature: Three Defense Problems Solved")
    update_text_frame(s6.shapes[4], "1. Content Truncation", bold=True)
    update_text_frame(
        s6.shapes[5],
        "Detects clipped notification previews ending in '...'. Full message is verified via Android Share Sheet (ACTION_SEND) or Clipboard Paste-and-Scan."
    )
    update_text_frame(s6.shapes[6], "2. E-Commerce Noise Rejection", bold=True)
    update_text_frame(
        s6.shapes[7],
        "Active blacklist drops shopping/food notifications (Amazon, Flipkart, Swiggy, Meesho) in 0.024 ms locally on device with 0 server strain."
    )
    update_text_frame(s6.shapes[8], "3. Notifications OFF & Privacy", bold=True)
    update_text_frame(
        s6.shapes[9],
        "Monitors SMS via telephony broadcasts, Gmail via OAuth2 API, and WhatsApp via companion sync. Contact Whitelist keeps private chats on phone."
    )
    
    # =========================================================================
    # SLIDE 7: Key Feature: Real-Time Edge Triage & Heuristics
    # =========================================================================
    s7 = prs.slides[6]
    update_text_frame(s7.shapes[9], "Key Feature: Real-Time Edge Triage & Heuristics")
    update_text_frame(s7.shapes[2], "Compact Bloom filter (85 KB memory, 50,000 domains) checks URLs in <0.02 ms.")
    update_text_frame(s7.shapes[4], "Homoglyph normalizer maps Cyrillic/Greek look-alikes back to Latin ASCII.")
    update_text_frame(s7.shapes[6], "Zero-width space stripper (\\u200B) uncovers hidden malicious keywords.")
    update_text_frame(s7.shapes[8], "Instant UI warning banner displayed on phone if threat score >= 25.")
    
    # Replace the old scheduler screenshot on right half of Slide 7 (Shape 10, id=176)
    if os.path.exists(edge_visual_path):
        replace_picture_blob(s7, s7.shapes[10], edge_visual_path)
    
    # =========================================================================
    # SLIDE 8: Core App Functionality
    # =========================================================================
    s8 = prs.slides[7]
    update_text_frame(s8.shapes[13], "Core App Functionality")
    update_text_frame(s8.shapes[4], "Background Sentinel", bold=True)
    update_text_frame(
        s8.shapes[5],
        "Passive Android NotificationListenerService and telephony receiver running on background coroutines with zero UI thread lag (0 ANRs)."
    )
    update_text_frame(s8.shapes[6], "Dual-Ingestion Channels", bold=True)
    update_text_frame(
        s8.shapes[7],
        "System Share Sheet ('Share to ScamGuard') and one-tap 'Paste & Scan' for authoritative, unclipped message verification."
    )
    update_text_frame(s8.shapes[8], "Multimodal Vishing & SOC", bold=True)
    update_text_frame(
        s8.shapes[9],
        "Whisper speech-to-text audio pipeline for phone call scams + live SOC web dashboard (localhost:8000) with real-time risk scores."
    )
    
    # =========================================================================
    # SLIDE 9: Results & Impact (Empirical Benchmarks)
    # =========================================================================
    s9 = prs.slides[8]
    update_text_frame(s9.shapes[13], "Results & Impact (Empirical Benchmarks)")
    update_text_frame(s9.shapes[4], "90.3% Request Reduction", bold=True)
    update_text_frame(
        s9.shapes[5],
        "Handled 1,015 of 1,124 test messages locally on device. 0 false positives on personal chats (969/969 true negatives)."
    )
    update_text_frame(s9.shapes[6], "Sub-Millisecond Speed", bold=True)
    update_text_frame(
        s9.shapes[7],
        "Edge screening takes 0.24 ms to 0.53 ms on physical ARM64 hardware (OPPO K13 5G / Android 16) with 0 UI frame drops."
    )
    update_text_frame(s9.shapes[8], "99.29% Hybrid Accuracy", bold=True)
    update_text_frame(
        s9.shapes[9],
        "Cloud transformer ensemble achieves 99.29% accuracy and 97.37% F1-score on confirmed scam and phishing payloads."
    )
    
    # =========================================================================
    # SLIDE 10: Future Enhancements
    # =========================================================================
    s10 = prs.slides[9]
    update_text_frame(s10.shapes[10], "Future Enhancements")
    update_text_frame(s10.shapes[4], "On-Device Quantized SLMs", bold=True)
    update_text_frame(
        s10.shapes[5],
        "Deploy 4-bit quantized MobileBERT or Phi-3 via Android Neural Networks API (NNAPI) for 100% on-device semantic parsing."
    )
    update_text_frame(s10.shapes[6], "Federated Learning", bold=True)
    update_text_frame(
        s10.shapes[7],
        "Decentralized threat learning with differential privacy so devices learn novel zero-day phishing lures without sharing raw chats."
    )
    update_text_frame(s10.shapes[8], "Apple iOS Extension", bold=True)
    update_text_frame(
        s10.shapes[9],
        "Port Bloom filters to Apple's native ILMessageFilterExtension for native zero-latency SMS classification in iOS Messages."
    )
    
    # =========================================================================
    # SLIDE 11: Thank You & Discussion
    # =========================================================================
    s11 = prs.slides[10]
    update_text_frame(s11.shapes[1], "Thank You", font_size=Pt(38), bold=True)
    update_text_frame(
        s11.shapes[2],
        "Questions & Answers\n\n"
        "Candidate: Revelli Tharun (23JE0807)\n"
        "Project Guide: Prof. Saurabh Srivastava\n"
        "Department of Computer Science and Engineering\n"
        "Indian Institute of Technology (Indian School of Mines), Dhanbad\n"
        "Academic Year 2026 – 2027",
        font_size=Pt(15),
        bold=False
    )
    
    # Adjust Thank You layout coordinates so it doesn't collide
    s11.shapes[1].top = Inches(2.35)
    s11.shapes[1].height = Inches(1.2)
    s11.shapes[2].top = Inches(3.75)
    s11.shapes[2].height = Inches(3.2)
    
    # =========================================================================
    # ADD IIT (ISM) LOGO TO ALL INNER SLIDES (Slide 2 - 10) & Slide 11
    # =========================================================================
    if os.path.exists(logo_path):
        for idx in range(1, 10):
            slide = prs.slides[idx]
            # Top right corner logo
            slide.shapes.add_picture(logo_path, Inches(12.2), Inches(0.35), width=Inches(0.8), height=Inches(0.8))
            
        # Centered logo above Thank You on Slide 11
        s11.shapes.add_picture(logo_path, Inches(5.86), Inches(0.6), width=Inches(1.6), height=Inches(1.55))
        
    prs.save(out_pptx)
    print(f"Successfully generated ScamGuard presentation: {out_pptx}")

if __name__ == "__main__":
    build_presentation()
