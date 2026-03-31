"""
=== JOB SEARCH CONFIGURATION ===

Edit this file to customize the job search for YOUR profile.
Everything else works automatically.
"""

import os

# ============================================================
# 1. YOUR PROFILE — fill in your details
# ============================================================

PROFILE = {
    "name": "Bohdan",
    "title": "Webflow / Shopify / Frontend Developer",
    "experience_years": 7,
    "salary_min": 2000,
    "salary_max": 3200,
    "remote_only": True,
    "language": "uk",
}

# ============================================================
# 2. WHAT YOU'RE LOOKING FOR
# ============================================================

TARGET = [
    "Webflow Developer, remote full-time",
    "Shopify Developer, remote full-time",
    "Frontend Developer (HTML/CSS/JS), remote",
    "No-code / Low-code Developer",
    "AI Automation Specialist (n8n, Make, Zapier)",
    "Web Developer with SEO experience",
]

NOT_INTERESTED = [
    "Companies working with or for Russia",
    "Vacancies posted in Russian language — Ukrainian or English only",
    "Gambling, adult content, crypto scams",
    "Office-only positions",
    "Junior/intern positions",
    "Outsource sweatshops with no career growth",
]

# ============================================================
# 3. FIT CRITERIA — customize scoring
# ============================================================

FIT_CRITERIA = """
| Signal | Good fit | Poor fit |
|---|---|---|
| Role type | Webflow, Shopify, Frontend, No-code, AI Automation | Backend-only, DevOps, Mobile |
| Company type | Product company, digital agency, startup | Russian market, gambling, adult |
| Remote | Fully remote | Office-required |
| Salary | $2000-3200+/month | Below $2000 |
| Language | Ukrainian or English vacancy | Russian-language vacancy |
"""

# ============================================================
# 4. YOUR KEY EXPERIENCE — for AI matching
# ============================================================

KEY_EXPERIENCE = [
    "7+ years in web development",
    "4 years building websites with Webflow (CMS, interactions, custom code)",
    "2 years Shopify development (themes, custom sections, Liquid)",
    "HTML, CSS, JavaScript, jQuery, TypeScript",
    "SEO optimization — on-page, technical, schema markup",
    "AI automation with n8n, Make, Zapier, Claude Code",
    "UI/UX design in Figma",
    "Team and project management (Jira, ClickUp, Asana, Notion)",
    "SaaS, no-code/low-code tools ecosystem",
]

# ============================================================
# 5. SEARCH KEYWORDS — what to search for on job boards
# ============================================================

SEARCH_KEYWORDS = [
    "webflow developer",
    "shopify developer",
    "frontend developer",
    "no-code developer",
    "web developer",
    "automation specialist",
]

# Keywords that vacancy titles must contain (at least one)
TITLE_KEYWORDS = [
    "webflow", "shopify", "frontend", "front-end", "front end",
    "web developer", "no-code", "nocode", "automation", "html",
    "розробник", "верстальник", "фронтенд",
]

# ============================================================
# 6. JOB BOARD URLS — customize search queries
# ============================================================

SOURCES = {
    "Djinni": {
        "enabled": True,
        "rss_keywords": ["webflow", "shopify", "frontend developer", "no-code", "automation"],
        "link_pattern": r'/jobs/(\d+)-',
    },
    "DOU": {
        "enabled": True,
        "urls": [
            "https://jobs.dou.ua/vacancies/?search=Webflow+Developer",
            "https://jobs.dou.ua/vacancies/?search=Shopify+Developer",
            "https://jobs.dou.ua/vacancies/?search=Frontend+Developer",
            "https://jobs.dou.ua/vacancies/?search=No-code",
        ],
        "link_pattern": r'/companies/[^/]+/vacancies/\d+/',
    },
    "Work.ua": {
        "enabled": True,
        "urls": [
            "https://www.work.ua/en/jobs-webflow+developer/",
            "https://www.work.ua/en/jobs-shopify+developer/",
            "https://www.work.ua/en/jobs-frontend+developer/",
            "https://www.work.ua/en/jobs-automation+specialist/",
        ],
        "link_pattern": r'/en/jobs/\d+/',
    },
    "Robota.ua": {
        "enabled": True,
        "urls": [
            "https://robota.ua/ua/jobs/webflow",
            "https://robota.ua/ua/jobs/shopify",
            "https://robota.ua/ua/jobs/frontend",
            "https://robota.ua/ua/jobs/no-code",
        ],
    },
    "HH.ua": {
        "enabled": True,
        "urls": [
            "https://hh.ua/search/vacancy?text=webflow+developer&area=5",
            "https://hh.ua/search/vacancy?text=shopify+developer&area=5",
            "https://hh.ua/search/vacancy?text=frontend+developer&area=5",
            "https://hh.ua/search/vacancy?text=no-code+developer&area=5",
        ],
    },
}

# ============================================================
# 7. GROQ API KEY (free) — loaded from environment variable
# ============================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ============================================================
# 8. WEB SERVER
# ============================================================

WEB_PORT = int(os.environ.get("PORT", 8080))
WEB_HOST = "0.0.0.0"

# ============================================================
# 9. PAGE TITLE
# ============================================================

PAGE_TITLE = "Вакансії — Webflow / Shopify / Frontend / Automation"
