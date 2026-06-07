import streamlit as st
import re
import time
from playwright.sync_api import sync_playwright

# [CONFIGURATION]
FB_PROFILE_DIR = "./fb_session_data"
TARGET_ROI = 0.20
MIN_PROFIT = 25.00

st.set_page_config(page_title="Flip Finder Pro", layout="wide")

def parse_price(text: str):
    m = re.search(r'[$]\s*([\d,]+(?:\.\d{1,2})?)', text)
    return float(m.group(1).replace(",", "")) if m else None

def get_ebay_value(query: str):
    # Mocking the eBay API lookup
    return 150.00

def analyze_listing(price, ebay_val):
    fees = ebay_val * 0.1325
    total_costs = price + 17
    profit = (ebay_val - fees) - total_costs
    roi = profit / total_costs if total_costs > 0 else 0
    return {"profit": profit, "roi": roi, "worth_it": profit >= MIN_PROFIT and roi >= TARGET_ROI}

# Initialize session state for browser management
if 'p' not in st.session_state:
    st.session_state.p = sync_playwright().start()
    st.session_state.browser = st.session_state.p.chromium.launch_persistent_context(
        user_data_dir=FB_PROFILE_DIR, headless=False
    )
    st.session_state.page = st.session_state.browser.new_page()
    st.session_state.page.goto("https://www.facebook.com/marketplace/")

st.title("Flip Finder Dashboard")
st.sidebar.info("Navigate Facebook in the browser window. The dashboard will analyze the listing as you open it.")

# Analysis area
placeholder = st.empty()

while True:
    current_url = st.session_state.page.url
    if "/marketplace/item/" in current_url:
        try:
            title = st.session_state.page.title()
            body_text = st.session_state.page.inner_text("body")
            price = parse_price(body_text) or 0
            
            ebay_comp = get_ebay_value(title)
            analysis = analyze_listing(price, ebay_comp)
            
            with placeholder.container():
                col1, col2 = st.columns(2)
                col1.metric("Listing Price", f"${price:,.2f}")
                col2.metric("Estimated eBay Value", f"${ebay_comp:,.2f}")
                
                status = "✅ BUY" if analysis['worth_it'] else "❌ PASS"
                st.subheader(f"Decision: {status}")
                st.write(f"**Profit:** ${analysis['profit']:.2f} | **ROI:** {analysis['roi']*100:.1f}%")
        except:
            pass
    
    time.sleep(3)
