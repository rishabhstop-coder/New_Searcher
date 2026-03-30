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

# CONFIG

# ==============================

st.set_page_config(layout="wide")
st.title("🔥 Website Revamp Lead Finder (Final)")

SUPABASE_URL = "https://cdtysrgzgfrzwlkeacax.supabase.co"
SUPABASE_KEY = "sb_publishable_BZ-OHKKeOdI3qOiz6MfvqQ_40EZOVlG"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-z]{2,}"

# ==============================

# INPUT

# ==============================

genre = st.text_input("Enter business niche", "dental")
start = st.button("🚀 Start Scanning")

# ==============================

# BLOCKING SYSTEM

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

COMMON_BRANDS = [
"nike","adidas","apple","samsung","tesla",
"netflix","uber","airbnb","spotify"
]

def get_domain(url):
    try:
return urlparse(url).netloc.lower().replace("[www](http://www).", "")
except:
return None

def is_blocked(url):
domain = get_domain(url)
if not domain:
return True

```
for b in BLOCKED_DOMAINS:
    if domain == b or domain.endswith("." + b) or b in domain:
        return True

if any(brand in domain for brand in COMMON_BRANDS):
    return True

if any(x in url for x in ["wixsite.com","wordpress.com","weebly.com","webflow.io"]):
    return True

return False
```

# ==============================

# DORKS

# ==============================

DORKS = [
'"{genre}" "contact us"',
'"{genre}" "call us"',
'"{genre}" "family owned"',
'"{genre}" "since 20"',
'"{genre}" "powered by wordpress"',
'"{genre}" "website under construction"',
'"{genre}" "local business"',
'intitle:"{genre}" "services"',
]

# ==============================

# SUPABASE

# ==============================

def save_lead(data):
try:
supabase.table("leads").upsert(data).execute()
except:
pass

def get_all_leads():
res = supabase.table("leads").select("*").execute()
return pd.DataFrame(res.data)

def mark_clicked(lead_id):
supabase.table("leads").update({"clicked": True}).eq("id", lead_id).execute()

def exists(domain):
res = supabase.table("leads").select("domain").eq("domain", domain).limit(1).execute()
return len(res.data) > 0

# ==============================

# SEARCH

# ==============================

def search_sites():
urls = set()
queries = random.sample(DORKS, len(DORKS))

```
with DDGS() as ddgs:
    for q in queries:
        query = q.format(genre=genre)

        try:
            results = ddgs.text(query, max_results=40)

            for r in results:
                url = r["href"]
                if not is_blocked(url):
                    urls.add(url)

        except:
            pass

        time.sleep(random.uniform(2, 4))

return list(urls)
```

# ==============================

# AUDIT SYSTEM (IMPROVED)

# ==============================

def extract_email(text):
emails = re.findall(EMAIL_REGEX, text)
return emails[0] if emails else ""

def audit(url):
try:
if not url.startswith("http"):
url = "http://" + url

```
    res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text().lower()

    score = 0
    issues = []

    # HTTPS
    if not url.startswith("https"):
        score += 3
        issues.append("No HTTPS")

    # Mobile
    if not soup.find("meta", attrs={"name": "viewport"}):
        score += 4
        issues.append("Not mobile friendly")

    # Old copyright
    if re.search(r"©\s*(200\d|201[0-8])", text):
        score += 3
        issues.append("Outdated copyright")

    # Heavy page
    if len(res.text) > 800000:
        score += 2
        issues.append("Heavy page")

    # Email
    email = extract_email(res.text)
    if not email:
        score += 2
        issues.append("No email")

    # Structure
    if not soup.find("nav"):
        score += 2
        issues.append("No navigation")

    if not soup.find("footer"):
        score += 1
        issues.append("No footer")

    # Tech signals
    if "powered by wordpress" in text:
        score += 2
        issues.append("Old WordPress")

    if "table" in str(soup):
        score += 2
        issues.append("Table layout")

    # UX issues
    if "lorem ipsum" in text:
        score += 5
        issues.append("Dummy content")

    if score < 5:
        return None

    # Priority
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

except:
    return None
```

# ==============================

# MAIN

# ==============================

if start:

```
st.info("Scanning...")

urls = search_sites()
st.write(f"Collected {len(urls)} sites")

new_count = 0

for url in urls:
    data = audit(url)

    if data and not exists(data["domain"]):
        save_lead(data)
        new_count += 1

st.success(f"New Leads Added: {new_count}")
```

# ==============================

# DISPLAY

# ==============================

st.subheader("📊 All Leads")

df = get_all_leads()

if not df.empty:
for i, row in df.iterrows():
col1, col2, col3 = st.columns([3,1,1])

```
    col1.write(f"{row['domain']} | Score: {row['pitch_score']} | {row['priority']}")
    st.caption(f"Issues: {row['issues']}")

    if col2.button("Open", key=row["id"]):
        mark_clicked(row["id"])
        st.write(row["url"])

    col3.write("✅ Clicked" if row["clicked"] else "❌ Not Clicked")
```

else:
st.warning("No leads yet")
