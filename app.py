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

genre = st.text_input("Enter business niche", "dental")
start = st.button("🚀 Start Scanning")

# ==============================
# BLOCKING SYSTEM (UNCHANGED LOGIC, CLEANED)
# ==============================

BLOCKED_DOMAINS = [
    "facebook","linkedin","instagram","youtube","twitter","x","tiktok",
    "google","bing","yahoo","microsoft","apple",
    "amazon","flipkart","ebay","alibaba","etsy",
    "yelp","justdial","sulekha","indiamart","tradeindia",
    "yellowpages","manta","angi","houzz","tripadvisor",
    "indeed","glassdoor","naukri",
    "github","stackoverflow","medium",
    "shopify","wix","wordpress.com","webflow","squarespace",
    "g2","capterra","producthunt","clutch","goodfirms",
    "reddit","quora","pinterest"
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
# SMART DORKS (IMPROVED)
# ==============================

def generate_dorks(niche):
    return [
        f'"{niche}" "contact us"',
        f'"{niche}" "call us"',
        f'intitle:"{niche}" "services"',
        f'"{niche}" "family owned"',
        f'"powered by wordpress" "{niche}"',
        f'inurl:contact "{niche}"',
    ]

# ==============================
# SEARCH (FASTER + CLEAN)
# ==============================

def search_sites(niche):
    urls = set()
    dorks = generate_dorks(niche)

    with DDGS() as ddgs:
        for query in dorks:
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
# REQUEST WITH RETRY
# ==============================

def fetch(url):
    for _ in range(2):  # retry twice
        try:
            return requests.get(url, headers=HEADERS, timeout=8)
        except:
            time.sleep(1)
    return None

# ==============================
# AUDIT (SAME STRUCTURE, BETTER LOGIC)
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

        if re.search(r"©\s*(200\d|201[0-8])", text):
            score += 3
            issues.append("Outdated copyright")

        if len(res.text) > 800000:
            score += 2
            issues.append("Heavy page")

        email = extract_email(res.text)
        if not email:
            score += 2
            issues.append("No email")

        if not soup.find("nav"):
            score += 2
            issues.append("No navigation")

        if not soup.find("footer"):
            score += 1
            issues.append("No footer")

        if "powered by wordpress" in text:
            score += 2
            issues.append("Old WordPress")

        if "table" in str(soup):
            score += 2
            issues.append("Table layout")

        if "lorem ipsum" in text:
            score += 5
            issues.append("Dummy content")

        if score < 5:
            return None

        priority = "LOW"
        if score >= 9:
            priority = "HIGH"
        elif score >= 6:
            priority = "MEDIUM"

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
# SUPABASE (UNCHANGED STRUCTURE)
# ==============================

def save_lead(data):
    try:
        data.setdefault("priority", "MEDIUM")
        data.setdefault("issues", "Auto-generated")
        supabase.table("leads").upsert(data).execute()
    except Exception as e:
        st.error(f"Save error: {e}")

def exists(domain):
    try:
        res = supabase.table("leads").select("domain").eq("domain", domain).limit(1).execute()
        return len(res.data) > 0
    except:
        return False

def get_all_leads():
    try:
        res = supabase.table("leads").select("*").execute()
        return pd.DataFrame(res.data)
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
# DISPLAY (UNCHANGED UX)
# ==============================

st.subheader("📊 All Leads")

df = get_all_leads()

if not df.empty:
    if "priority" not in df.columns:
        df["priority"] = "UNKNOWN"

    for _, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])

        col1.write(f"{row['domain']} | Score: {row['pitch_score']} | {row['priority']}")
        st.caption(f"Issues: {row['issues']}")

        if col2.button("Open", key=row["id"]):
            mark_clicked(row["id"])
            st.write(row["url"])

        col3.write("✅ Clicked" if row.get("clicked") else "❌ Not Clicked")

else:
    st.warning("No leads yet")
