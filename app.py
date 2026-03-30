import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import pandas as pd
from urllib.parse import urlparse
from ddgs import DDGS
from supabase import create_client

# ==============================
# CONFIG (UNCHANGED)
# ==============================

st.set_page_config(layout="wide")
st.title("🔥 Website Revamp Lead Finder")

SUPABASE_URL = "https://cdtysrgzgfrzwlkeacax.supabase.co"
SUPABASE_KEY = "sb_publishable_BZ-OHKKeOdI3qOiz6MfvqQ_40EZOVlG"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ==============================
# INPUT
# ==============================

genre = st.text_input("Enter business niche", "real estate")
start = st.button("🚀 Start Scanning")

# ==============================
# BLOCKING SYSTEM
# ==============================

BLOCKED_DOMAINS = [
    "facebook","linkedin","instagram","youtube","twitter","x","tiktok",
    "google","bing","yahoo","amazon","flipkart","ebay",
    "indeed","glassdoor","naukri","reddit","quora","pinterest"
]

def get_domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except:
        return None

def is_blocked(url):
    domain = get_domain(url)
    if not domain:
        return True
    return any(b in domain for b in BLOCKED_DOMAINS)

# ==============================
# DORK GENERATION
# ==============================

def generate_dorks(niche):
    return [
        f'"{niche}" "contact us"',
        f'"{niche}" "call us"',
        f'intitle:"{niche}" "services"',
        f'"powered by wordpress" "{niche}"',
        f'inurl:contact "{niche}"',
    ]

# ==============================
# SEARCH
# ==============================

def search_sites(niche):
    urls = set()

    with DDGS() as ddgs:
        for query in generate_dorks(niche):
            try:
                results = ddgs.text(query, max_results=30)
                for r in results:
                    url = r["href"]
                    if not is_blocked(url):
                        urls.add(url)
            except Exception as e:
                st.warning(f"Search error: {e}")

            time.sleep(random.uniform(1, 2))

    return list(urls)

# ==============================
# REQUEST (RETRY SAFE)
# ==============================

def fetch(url):
    for _ in range(2):
        try:
            return requests.get(url, headers=HEADERS, timeout=8)
        except:
            time.sleep(1)
    return None

# ==============================
# AUDIT
# ==============================

def extract_email(text):
    emails = re.findall(EMAIL_REGEX, text)
    return emails[0] if emails else ""

def audit(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url

        res = fetch(url)
        if not res:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text().lower()

        score = 0
        issues = []

        if not url.startswith("https"):
            score += 3
            issues.append("No HTTPS")

        if not soup.find("meta", attrs={"name": "viewport"}):
            score += 4
            issues.append("Not mobile friendly")

        if "lorem ipsum" in text:
            score += 5
            issues.append("Dummy content")

        if "powered by wordpress" in text:
            score += 2
            issues.append("Old WordPress")

        if not soup.find("footer"):
            score += 1
            issues.append("No footer")

        if not soup.find("nav"):
            score += 2
            issues.append("No navigation")

        email = extract_email(res.text)
        if not email:
            score += 2
            issues.append("No email")

        if score < 5:
            return None

        if score >= 9:
            priority = "HIGH"
        elif score >= 6:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return {
            "domain": get_domain(url),
            "url": url,
            "email": email,
            "pitch_score": score,
            "issues": ", ".join(issues),
            "priority": priority,
            "clicked": False
        }

    except Exception as e:
        st.error(f"Audit error: {url} → {e}")
        return None

# ==============================
# DATABASE (UNCHANGED STRUCTURE)
# ==============================

def exists(domain):
    try:
        res = supabase.table("leads").select("domain").eq("domain", domain).limit(1).execute()
        return len(res.data) > 0
    except:
        return False

def save_lead(data):
    try:
        data.setdefault("priority", "MEDIUM")
        data.setdefault("issues", "Auto-generated")
        supabase.table("leads").upsert(data).execute()
    except Exception as e:
        st.error(f"Save error: {e}")

def get_all_leads():
    try:
        res = supabase.table("leads").select("*").execute()
        df = pd.DataFrame(res.data)

        # FIX ALL MISSING COLUMNS HERE (NO MORE KEYERROR EVER)
        for col, default in {
            "domain": "N/A",
            "pitch_score": 0,
            "priority": "UNKNOWN",
            "issues": "Not available",
            "clicked": False
        }.items():
            if col not in df.columns:
                df[col] = default

        return df

    except:
        return pd.DataFrame()

def mark_clicked(lead_id):
    try:
        supabase.table("leads").update({"clicked": True}).eq("id", lead_id).execute()
    except:
        pass

# ==============================
# MAIN
# ==============================

if start:
    st.info("Scanning...")

    urls = search_sites(genre)
    st.write(f"Collected {len(urls)} sites")

    new_count = 0

    for url in urls:
        domain = get_domain(url)

        if not domain or exists(domain):
            continue

        data = audit(url)

        if data:
            save_lead(data)
            new_count += 1

    st.success(f"New Leads Added: {new_count}")

# ==============================
# DISPLAY
# ==============================

st.subheader("📊 All Leads")

df = get_all_leads()

if not df.empty:
    for _, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])

        col1.write(f"{row.get('domain')} | Score: {row.get('pitch_score')} | {row.get('priority')}")
        st.caption(f"Issues: {row.get('issues')}")

        if col2.button("Open", key=row["id"]):
            mark_clicked(row["id"])
            st.write(row.get("url"))

        col3.write("✅ Clicked" if row.get("clicked") else "❌ Not Clicked")

else:
    st.warning("No leads yet")
