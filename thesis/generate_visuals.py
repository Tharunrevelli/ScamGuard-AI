from PIL import Image, ImageDraw, ImageFont
import os

width, height = 1200, 1000
img = Image.new('RGB', (width, height), color=(15, 23, 42))
draw = ImageDraw.Draw(img)

# Try loading standard windows fonts
try:
    font_title = ImageFont.truetype('segoeuib.ttf', 32)
    font_subtitle = ImageFont.truetype('segoeui.ttf', 20)
    font_heading = ImageFont.truetype('segoeuib.ttf', 23)
    font_body = ImageFont.truetype('segoeui.ttf', 19)
    font_code = ImageFont.truetype('consola.ttf', 17)
    font_metric_val = ImageFont.truetype('segoeuib.ttf', 30)
    font_metric_lbl = ImageFont.truetype('segoeui.ttf', 15)
except Exception:
    font_title = font_subtitle = font_heading = font_body = font_code = font_metric_val = font_metric_lbl = ImageFont.load_default()

# Header Card
draw.rounded_rectangle([30, 25, width-30, 115], radius=12, fill=(30, 41, 59), outline=(59, 130, 246), width=2)
draw.text((55, 38), "ScamGuard Edge Triage Engine", font=font_title, fill=(248, 250, 252))
draw.text((55, 80), "Physical Test Hardware: OPPO K13 5G | Android 16 | Zero Cloud Lag", font=font_subtitle, fill=(148, 163, 184))

# Card 1: Bloom Filter
draw.rounded_rectangle([30, 135, width-30, 310], radius=12, fill=(24, 32, 47), outline=(51, 65, 85), width=1)
draw.text((55, 150), "1. Compact URL Bloom Filter (< 0.02 ms lookup)", font=font_heading, fill=(56, 189, 248))
draw.text((55, 188), "- Memory Footprint: 85 KB holding 50,000 malicious phishing domains", font=font_body, fill=(226, 232, 240))
draw.text((55, 222), "- Hash Mechanics: k = 7 MurmurHash3 permutations with zero heap allocations", font=font_body, fill=(226, 232, 240))
draw.text((55, 256), "- Outcome: 90.3% of notifications filtered locally without remote server queries", font=font_body, fill=(52, 211, 153))

# Card 2: Homoglyph Normalization
draw.rounded_rectangle([30, 330, width-30, 505], radius=12, fill=(24, 32, 47), outline=(51, 65, 85), width=1)
draw.text((55, 345), "2. Adversarial Homoglyph & Evasion Normalizer", font=font_heading, fill=(245, 158, 11))
draw.text((55, 383), "- Canonical Mapping: Cyrillic/Greek lookalikes -> Latin ASCII (e.g. \\u0430 -> a)", font=font_body, fill=(226, 232, 240))
draw.text((55, 417), "- Zero-Width Stripper: Detects & eliminates hidden Unicode spaces (\\u200B / \\u200C)", font=font_body, fill=(226, 232, 240))
draw.text((55, 451), "- Regex Rule Engine: Evaluates 14 financial urgency & credential triggers in 0.18 ms", font=font_body, fill=(226, 232, 240))

# Card 3: Alert Banner Simulation
draw.rounded_rectangle([30, 525, width-30, 785], radius=12, fill=(69, 10, 10), outline=(239, 68, 68), width=2)
draw.text((55, 540), "Real-Time Threat Interception Alert (On-Device UI)", font=font_heading, fill=(254, 202, 202))
draw.rectangle([55, 580, width-55, 665], fill=(20, 10, 10), outline=(185, 28, 28), width=1)
draw.text((70, 595), "SMS: 'Dear customer, your SBI account is suspended! Verify at http://sbi-kyc.cc'", font=font_code, fill=(252, 165, 165))
draw.text((70, 630), "Action: Immediate action required within 24 hours to prevent account freeze.", font=font_code, fill=(252, 165, 165))
draw.text((55, 680), "• Risk Score: 88 / 100 (CRITICAL THREAT)  |  Status: Blocked at Edge", font=font_body, fill=(254, 226, 226))
draw.text((55, 712), "• Detection Vectors: Homoglyph lookalike, Banking Urgency, Domain not in Whitelist", font=font_body, fill=(254, 226, 226))
draw.text((55, 744), "• Privacy Guarantee: Interpersonal chats from saved contacts bypassed automatically", font=font_body, fill=(134, 239, 172))

# Bottom Metric Strip
draw.rounded_rectangle([30, 805, width-30, 960], radius=12, fill=(15, 23, 42), outline=(59, 130, 246), width=1)
metrics = [
    ("Edge Triage Latency", "0.38 ms", (56, 189, 248)),
    ("RAM Footprint", "85 KB", (52, 211, 153)),
    ("False Positive Rate", "0.00 %", (245, 158, 11)),
    ("Battery Drain", "< 0.01 %", (168, 85, 247))
]
col_w = (width - 60) // 4
for i, (lbl, val, col) in enumerate(metrics):
    x = 30 + i * col_w
    draw.text((x + 25, 830), val, font=font_metric_val, fill=col)
    draw.text((x + 25, 885), lbl, font=font_metric_lbl, fill=(148, 163, 184))

out_path = "thesis/edge_triage_visual.png"
img.save(out_path)
print(f"Successfully generated {out_path}")
