import os
import time
import io
import math
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_recording():
    print("Setting up Headless Chrome (1440x900)...")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1440,900')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--force-device-scale-factor=1')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1440, 900)

    frames = []
    durations = []  # ms

    current_cursor = [720, 450]

    def add_frame(cursor_pos=None, duration=150, draw_cursor=True, banner_text=None):
        nonlocal current_cursor
        if cursor_pos is not None:
            current_cursor = [cursor_pos[0], cursor_pos[1]]
        
        png_data = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(png_data)).convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw banner if provided
        if banner_text:
            # Draw sleek HUD badge at bottom center
            badge_w, badge_h = 420, 38
            bx = (img.width - badge_w) // 2
            by = img.height - 60
            draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=19, fill=(19, 19, 20, 225), outline=(189, 157, 255, 180), width=1)
            # Subtle glowing dot
            draw.ellipse([bx + 18, by + 13, bx + 30, by + 25], fill=(189, 157, 255, 255))
            # Text
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
            draw.text((bx + 40, by + 10), banner_text, fill=(255, 255, 255, 240), font=font)

        # Draw glowing animated cursor
        if draw_cursor and current_cursor:
            cx, cy = int(current_cursor[0]), int(current_cursor[1])
            draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(189, 157, 255, 70), outline=(189, 157, 255, 160), width=1)
            draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255, 240), outline=(189, 157, 255, 255), width=2)

        img = Image.alpha_composite(img, overlay)
        frames.append(img.convert("RGB"))
        durations.append(duration)

    def smooth_move_to(target_x, target_y, steps=6, pause_ms=60, banner_text=None):
        start_x, start_y = current_cursor
        for i in range(1, steps + 1):
            t = i / steps
            ease = 3 * t**2 - 2 * t**3
            cur_x = start_x + (target_x - start_x) * ease
            cur_y = start_y + (target_y - start_y) * ease
            add_frame(cursor_pos=[cur_x, cur_y], duration=pause_ms, banner_text=banner_text)

    def smooth_scroll_to(target_y, steps=8, pause_ms=80, banner_text=None):
        current_scroll = driver.execute_script("return window.pageYOffset;")
        diff = target_y - current_scroll
        for i in range(1, steps + 1):
            t = i / steps
            ease = 3 * t**2 - 2 * t**3
            y = current_scroll + diff * ease
            driver.execute_script(f"window.scrollTo(0, {y});")
            add_frame(duration=pause_ms, banner_text=banner_text)

    def safe_click_element(element, banner_text=None):
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
        time.sleep(0.3)
        loc = element.location
        size = element.size
        scroll_y = driver.execute_script("return window.pageYOffset;")
        screen_x = loc['x'] + size['width'] / 2
        screen_y = loc['y'] - scroll_y + size['height'] / 2
        smooth_move_to(screen_x, screen_y, steps=5, banner_text=banner_text)
        add_frame(cursor_pos=[screen_x, screen_y], duration=300, banner_text=banner_text)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(0.5)

    try:
        # ==========================================
        # SCENE 1: LANDING PAGE & SPATIAL OVERVIEW
        # ==========================================
        print("SCENE 1: Landing Page")
        driver.get("https://ncr-property-intelligence-system.vercel.app/")
        time.sleep(3)
        add_frame(cursor_pos=[720, 280], duration=1200, banner_text="Institutional Real Estate Intelligence")

        # Move to live metrics
        smooth_move_to(1100, 240, steps=6, banner_text="18,000+ Active Geospatial Asset Nodes")
        add_frame(duration=900, banner_text="18,000+ Active Geospatial Asset Nodes")

        # Scroll to Spatial Intelligence section
        smooth_scroll_to(420, steps=7, pause_ms=90, banner_text="Real-Time Geospatial Value Mapping")
        add_frame(duration=1100, banner_text="Real-Time Geospatial Value Mapping")

        # Scroll back to cards
        smooth_scroll_to(0, steps=6, pause_ms=80, banner_text="Algorithmic Market Valuation HUD")
        
        # Click Market Analyzer
        market_card = driver.find_element(By.XPATH, "//a[contains(@href, '/dashboard')]")
        safe_click_element(market_card, banner_text="Accessing Market Analyzer Engine...")

        # ==========================================
        # SCENE 2: MARKET ANALYZER / VALUATION HUD
        # ==========================================
        print("SCENE 2: Market Analyzer")
        time.sleep(2.5)
        add_frame(cursor_pos=[720, 220], duration=1000, banner_text="Dynamic ML Price & Yield Predictor")

        # Scroll to form
        smooth_scroll_to(140, steps=5, pause_ms=80, banner_text="Configuring Asset Parameters")

        # Click Scan Valuation button
        scan_btns = driver.find_elements(By.XPATH, "//button[contains(., 'SCAN') or contains(., 'VALUATION') or contains(., 'Estimate')]")
        if scan_btns:
            safe_click_element(scan_btns[-1], banner_text="Executing CatBoost Valuation Pipeline...")
            time.sleep(1.5)

        # Scroll down to Valuation HUD results
        smooth_scroll_to(480, steps=6, pause_ms=90, banner_text="Sub-Second Valuation & ROI Yield HUD")
        add_frame(duration=1400, banner_text="Valuation: ₹2.40 Cr | Yield: 4.8% | Bias: +0.42%")

        # Open View Analysis Modal
        analysis_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Analysis') or contains(., 'Breakdown')]")
        if analysis_btns:
            safe_click_element(analysis_btns[0], banner_text="Opening Micro-Market Risk Breakdown...")
            time.sleep(1.5)
            add_frame(duration=1600, banner_text="Risk Benchmarking & Confidence Distribution")
            
            # Close analysis modal
            close_btns = driver.find_elements(By.XPATH, "//button[contains(., '×') or contains(@class, 'rounded-full')]")
            if close_btns:
                driver.execute_script("arguments[0].click();", close_btns[0])
                time.sleep(0.6)
                add_frame(duration=400, banner_text="Market Analyzer Complete")

        # ==========================================
        # SCENE 3: SPATIAL DISCOVERY & ASSET SEARCH
        # ==========================================
        print("SCENE 3: Geospatial Discovery")
        driver.get("https://ncr-property-intelligence-system.vercel.app/discovery")
        time.sleep(3)
        add_frame(cursor_pos=[720, 200], duration=1100, banner_text="Geospatial Discovery & Proximity Engine")

        # Toggle Advanced filters
        adv_btns = driver.find_elements(By.XPATH, "//button[contains(., 'Advanced')]")
        if adv_btns:
            safe_click_element(adv_btns[0], banner_text="Applying High-Fidelity Filters...")
            time.sleep(0.8)
            add_frame(duration=700, banner_text="Filtering: Gated Community & Metro Link")

        # Scroll down to property assets
        smooth_scroll_to(550, steps=7, pause_ms=90, banner_text="Vectorized Proximity Search (43k+ Assets)")
        add_frame(duration=1200, banner_text="Instant Haversine Distance to Transit Hubs")

        # Find and click first property card to open Deep Dive Drawer
        print("SCENE 4: Property Deep Dive Drawer")
        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer') or (contains(@class, 'group') and contains(@class, 'rounded'))]")
        
        # Click on property listing
        clickable_card = None
        for c in cards:
            if c.size['height'] > 140 and c.size['width'] > 250:
                clickable_card = c
                break
        
        if clickable_card:
            safe_click_element(clickable_card, banner_text="Loading High-Fidelity Asset Deep Dive...")
            time.sleep(2)
            # Showcase Deep Dive drawer
            add_frame(duration=1800, banner_text="Asset Deep Dive: Reconciled Amenities & GPS Sync")

            # Scroll inside deep dive drawer or page
            driver.execute_script("window.scrollBy(0, 200);")
            add_frame(duration=1500, banner_text="AI Similarity Matrix & Yield Optimization")
        else:
            add_frame(duration=1500, banner_text="High-Yield NCR Investment Opportunities")

        # Final wrap frame
        add_frame(duration=1200, banner_text="NCR Property Intelligence | Ready for Production")

    finally:
        driver.quit()

    print(f"Total frames recorded: {len(frames)}")
    if not frames:
        print("Error: No frames were captured.")
        return

    # Resize to clean 960x600 for sharp, lightweight rendering
    target_width = 960
    w, h = frames[0].size
    target_height = int(h * (target_width / w))
    print(f"Resizing {len(frames)} frames to {target_width}x{target_height}...")
    resized_frames = [f.resize((target_width, target_height), Image.Resampling.LANCZOS) for f in frames]

    # 1. High-Performance Animated WebP
    webp_path = os.path.abspath("docs/assets/ncr_property_intelligence_demo.webp")
    print(f"Exporting animated WebP to {webp_path}...")
    resized_frames[0].save(
        webp_path,
        format="WEBP",
        save_all=True,
        append_images=resized_frames[1:],
        duration=durations,
        loop=0,
        quality=88,
        method=4
    )
    print(f"WebP exported: {os.path.getsize(webp_path) / 1024 / 1024:.2f} MB")

    # 2. Optimized Animated GIF Fallback
    gif_path = os.path.abspath("docs/assets/ncr_property_intelligence_demo.gif")
    print(f"Exporting animated GIF to {gif_path}...")
    quantized_frames = [f.quantize(colors=128, method=Image.Resampling.LANCZOS) for f in resized_frames]
    quantized_frames[0].save(
        gif_path,
        format="GIF",
        save_all=True,
        append_images=quantized_frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"GIF exported: {os.path.getsize(gif_path) / 1024 / 1024:.2f} MB")

    # Copy to artifact directory as well
    artifact_dir = r"C:\Users\Asus\.gemini\antigravity-ide\brain\975af42f-2341-496e-9465-277285757a4d"
    artifact_webp = os.path.join(artifact_dir, "ncr_property_intelligence_demo.webp")
    artifact_gif = os.path.join(artifact_dir, "ncr_property_intelligence_demo.gif")
    
    with open(webp_path, 'rb') as f_in, open(artifact_webp, 'wb') as f_out:
        f_out.write(f_in.read())
    with open(gif_path, 'rb') as f_in, open(artifact_gif, 'wb') as f_out:
        f_out.write(f_in.read())
    print("Copied to artifacts directory.")

if __name__ == "__main__":
    create_recording()
