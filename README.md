# 🔥 Website Revamp Lead Finder

An intelligent lead generation tool that discovers outdated or poorly built websites and identifies businesses that may benefit from a website redesign or digital upgrade.

---

## 🚀 Overview

This tool automates the process of finding potential clients by:

* Searching for niche-specific business websites
* Filtering out large platforms and irrelevant domains
* Auditing websites for technical and UX issues
* Scoring and prioritizing leads
* Storing and tracking leads using Supabase

---

## ✨ Features

* 🔍 Smart search using dork queries
* 🚫 Advanced filtering system (blocks major platforms & directories)
* 🧠 Website audit engine with issue detection
* 📊 Lead scoring & priority classification
* 📬 Email extraction
* 🗂️ Persistent database (Supabase)
* ✅ Click tracking for reviewed leads

---

## 🛠️ Tech Stack

* Python
* Streamlit
* BeautifulSoup
* DuckDuckGo Search (DDGS)
* Supabase

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/rishabhstop-coder.git
cd rishabhstop-coder
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables

Create a `.env` file:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 4. Run the app

```bash
streamlit run New_Search.py
```

---

## 🗄️ Database Schema

Create a `leads` table in Supabase:

| Column      | Type              |
| ----------- | ----------------- |
| id          | int (primary key) |
| domain      | text              |
| url         | text              |
| email       | text              |
| pitch_score | int               |
| issues      | text              |
| priority    | text              |
| clicked     | boolean           |

---

## 🧠 How Scoring Works

Websites are evaluated based on:

* HTTPS availability
* Mobile responsiveness
* Outdated content signals
* Missing structure (nav/footer)
* Performance indicators
* UX issues (dummy content, old layouts)

Higher score = better lead opportunity.

---

## 📌 Use Cases

* Web development agencies
* Freelancers
* Lead generation specialists
* Digital marketing agencies

---

## ⚡ Future Improvements

* LinkedIn scraping for decision-makers
* Email validation system
* Automated outreach generation
* CRM/export integration
* Multi-engine search support

---

## ⚠️ Disclaimer

This project is intended for ethical and professional lead generation only. Ensure compliance with applicable data and outreach regulations.

---

## 👤 Author

Rishabh Patel
