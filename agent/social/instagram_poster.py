"""
SHEtoken Agent — Instagram Weekly Post
========================================
Posts a weekly WEI summary image to @shetoken Instagram.

Instagram Graph API only allows:
  - Posting to your OWN business/creator account
  - Reading your own content
  - NOT reading other users' content

This module:
  1. Generates a weekly report image (berry/gold branded)
  2. Posts it to Instagram with caption + hashtags

Setup:
    1. Convert Instagram to a Business/Creator account
    2. Connect to a Facebook Page
    3. Create a Facebook Developer App
    4. Get Instagram Business Account ID
    5. Generate a long-lived User Access Token
    6. Add IG_ACCESS_TOKEN and IG_BUSINESS_ID to .env

Image: Created using Pillow — no external dependencies
"""
import os, logging, io, tempfile, requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

IG_ACCESS_TOKEN  = os.getenv("IG_ACCESS_TOKEN")
IG_BUSINESS_ID   = os.getenv("IG_BUSINESS_ID")
IG_API_BASE      = "https://graph.facebook.com/v19.0"


def generate_report_image(report: dict) -> bytes:
    """
    Generate a branded weekly report image.
    Returns PNG bytes.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        # Brand colours
        BERRY = (109, 46, 70)
        GOLD  = (201, 168, 76)
        WHITE = (255, 255, 255)
        CREAM = (236, 226, 208)

        img  = Image.new("RGB", (1080, 1080), BERRY)
        draw = ImageDraw.Draw(img)

        # Background gradient effect — simple version
        for y in range(1080):
            alpha = y / 1080
            r = int(BERRY[0] * (1-alpha*0.3))
            g = int(BERRY[1] * (1-alpha*0.3))
            b = int(BERRY[2] * (1-alpha*0.3))
            draw.line([(0,y),(1080,y)], fill=(r,g,b))

        week    = report.get("week","")
        signals = report.get("total_signals", 0)
        crises  = report.get("crisis_count", 0)
        movers  = report.get("top_movers", [])
        pillars = report.get("global_pillar_summary", {})

        # Try to load a font, fall back to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 72)
            body_font  = ImageFont.truetype("arial.ttf", 48)
            small_font = ImageFont.truetype("arial.ttf", 36)
        except Exception:
            title_font = ImageFont.load_default()
            body_font  = title_font
            small_font = title_font

        # SHE token header
        draw.text((80, 80), "$SHE", font=title_font, fill=GOLD)
        draw.text((80, 160), "Women's Empowerment Index", font=body_font, fill=CREAM)
        draw.text((80, 220), f"Weekly Signal Report — {week}", font=small_font, fill=WHITE)

        # Divider line
        draw.line([(80, 280), (1000, 280)], fill=GOLD, width=3)

        # Stats
        y = 320
        stats = [
            (f"{signals}", "Signals Detected"),
            (f"{crises}",  "Crisis Alerts"),
            (f"{movers[0]['geo'] if movers else '—'}", "Top Region"),
        ]
        col_w = 300
        for i, (num, label) in enumerate(stats):
            x = 80 + i * col_w
            draw.text((x, y),    num,   font=title_font, fill=GOLD)
            draw.text((x, y+80), label, font=small_font, fill=CREAM)

        # Top pillar
        y = 560
        if pillars:
            top_p, pd = max(pillars.items(), key=lambda x: abs(x[1]["net_signal"]))
            sig = pd["net_signal"]
            arrow = "▲" if sig > 0 else "▼"
            draw.text((80, y), "Top Pillar Signal:", font=body_font, fill=CREAM)
            draw.text((80, y+60), f"{arrow} {top_p.replace('_',' ').title()}", font=body_font, fill=GOLD)
            draw.text((80, y+120), f"Net: {sig:+.3f}", font=small_font, fill=WHITE)

        # Footer
        draw.line([(80, 920), (1000, 920)], fill=GOLD, width=2)
        draw.text((80, 940), "shetoken.org  |  @ShetokenDAO", font=small_font, fill=GOLD)
        draw.text((80, 990), "SHE GOES UP", font=body_font, fill=GOLD)

        # Save to bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG", quality=95)
        return buf.getvalue()

    except ImportError:
        logger.warning("Pillow not installed — run: pip install Pillow")
        return None
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return None


def build_caption(report: dict) -> str:
    """Build Instagram caption with hashtags."""
    week    = report.get("week","")
    signals = report.get("total_signals",0)
    crises  = report.get("crisis_count",0)
    movers  = report.get("top_movers",[])

    top_geo = movers[0]["geo"] if movers else ""
    crisis_str = f"\n⚠️ {crises} crisis alerts this week" if crises else ""

    caption = (
        f"$SHE Weekly WEI Signal Report — {week}\n\n"
        f"📊 {signals} signals detected across 100+ news sources\n"
        f"🌍 Most active region: {top_geo}{crisis_str}\n\n"
        f"The Women's Empowerment Index tracks real-world progress "
        f"on gender equality across 105 countries — and ties it to "
        f"financial value. When women's conditions improve, $SHE appreciates.\n\n"
        f"She goes up.\n\n"
        f"Link in bio → shetoken.org\n\n"
        f"#SHEtoken #WomenEmpowerment #GenderEquality #WEI "
        f"#ImpactInvesting #ESG #DeFi #Crypto #WomenRights "
        f"#GirlsEducation #ChildMarriage #ReproductiveRights "
        f"#EndGBV #Feminism #India #WestBengal"
    )
    return caption[:2200]   # Instagram caption limit


def post_to_instagram(report: dict) -> bool:
    """Post weekly report image to Instagram."""
    if not IG_ACCESS_TOKEN or not IG_BUSINESS_ID:
        logger.info("Instagram: credentials not set — skipping")
        return False

    # Generate image
    img_bytes = generate_report_image(report)
    if not img_bytes:
        return False

    caption = build_caption(report)

    try:
        # Step 1: Upload image to a temporary URL
        # Instagram requires a publicly accessible URL
        # Simplest: upload to imgbb.com (free, no auth needed for temp)
        imgbb_key = os.getenv("IMGBB_API_KEY")
        if not imgbb_key:
            logger.warning("Instagram: IMGBB_API_KEY needed to host image")
            return False

        import base64
        img_b64 = base64.b64encode(img_bytes).decode()
        upload_resp = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": imgbb_key, "image": img_b64},
            timeout=30
        )
        upload_resp.raise_for_status()
        image_url = upload_resp.json()["data"]["url"]

        # Step 2: Create media container
        container_resp = requests.post(
            f"{IG_API_BASE}/{IG_BUSINESS_ID}/media",
            data={
                "image_url":    image_url,
                "caption":      caption,
                "access_token": IG_ACCESS_TOKEN,
            }
        )
        container_resp.raise_for_status()
        container_id = container_resp.json()["id"]

        # Step 3: Publish
        publish_resp = requests.post(
            f"{IG_API_BASE}/{IG_BUSINESS_ID}/media_publish",
            data={
                "creation_id":  container_id,
                "access_token": IG_ACCESS_TOKEN,
            }
        )
        publish_resp.raise_for_status()

        logger.info(f"Instagram: posted successfully — {publish_resp.json().get('id')}")
        return True

    except Exception as e:
        logger.error(f"Instagram post failed: {e}")
        return False
