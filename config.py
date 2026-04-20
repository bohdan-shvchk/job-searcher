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
| Signal | Good fit (high score) | Poor fit (score 1-2) |
|---|---|---|
| Role type | Webflow, Shopify, No-code, AI Automation (n8n/Make/Zapier), Web Developer | Frontend Developer requiring React/Angular/Vue, Backend, DevOps, Mobile |
| Tech stack | Webflow, Shopify/Liquid, HTML/CSS/JS, n8n, Make, Zapier, Figma | Python, Java, Angular, React, Vue, Node.js, Ruby, PHP, .NET, C#, Go, Kotlin |
| Company type | Product company, digital agency, startup | Russian market, gambling, adult content |
| Remote | Fully remote | Office-required or hybrid |
| Salary | $2000-3200+/month | Below $2000 |
| Language | Ukrainian or English vacancy | Russian-language vacancy |

IMPORTANT: If the vacancy primarily requires React, Angular, Vue, Python, Java, Ruby, PHP, TypeScript, WordPress or any other technology not listed under "Good fit", score it 1 or 2 regardless of the job title.
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
    "no-code developer",
    "web developer",
    "automation specialist",
]

# Keywords that vacancy titles must contain (at least one)
TITLE_KEYWORDS = [
    "webflow", "shopify", "frontend", "front-end", "front end",
    "web developer", "no-code", "nocode", "html/css",
    "workflow automation", "n8n", "make.com", "zapier",
    "розробник сайтів", "верстальник", "фронтенд",
]

# Keywords that immediately exclude a vacancy if found in the title
EXCLUDE_TITLE_KEYWORDS = [
    # Прямо backend
    "backend", "back-end", "back end",
    # Frontend frameworks — нам не потрібні
    "frontend developer", "front-end developer", "front end developer",
    "react developer", "react dev", "react.js",
    "angular developer", "angular dev", "angularjs",
    "vue developer", "vue dev", "vue.js",
    "next.js developer", "nuxt developer",
    "фронтенд розробник", "фронтенд-розробник",
    # Мови / стеки — нам не потрібні
    "python developer", "python dev", "python/",
    "java ", "java,", "java/", "java developer",
    "ruby ", "ruby developer", "rails",
    ".net", "c#", "asp.net",
    "php developer", "laravel developer", "symfony",
    "typescript developer", "ts developer",
    "wordpress developer", "wordpress dev",
    "golang", "go developer",
    "kotlin developer", "swift developer",
    "c++ ", "c/c++",
    # Інфра / DevOps
    "devops", "sre ", "site reliability",
    # QA
    "qa ", "qа ", "quality assurance", "тестувальник", "автоматизоване тестування",
    # Mobile
    "android", "ios ", "mobile developer", "mobile dev",
    "flutter", "react native",
    # Інше
    "unity", "game dev", "gamedev",
    "embedded", "hardware",
    "data engineer", "data scientist", "machine learning", "ml engineer",
    "blockchain", "solidity", "web3",
    "magento", "drupal",
    "1c ", "1с ",
]

# ============================================================
# 6. JOB BOARD URLS — customize search queries
# ============================================================

SOURCES = {
    "Djinni": {
        "enabled": True,
        "rss_keywords": ["webflow", "shopify", "no-code", "n8n"],
        "link_pattern": r'/jobs/(\d+)-',
    },
    "DOU": {
        "enabled": True,
        "urls": [
            "https://jobs.dou.ua/vacancies/?search=Webflow+Developer",
            "https://jobs.dou.ua/vacancies/?search=Shopify+Developer",
            "https://jobs.dou.ua/vacancies/?search=No-code+Developer",
        ],
        "link_pattern": r'/companies/[^/]+/vacancies/\d+/',
    },
    "Work.ua": {
        "enabled": True,
        "urls": [
            "https://www.work.ua/en/jobs-webflow+developer/",
            "https://www.work.ua/en/jobs-shopify+developer/",
            "https://www.work.ua/en/jobs-no-code+developer/",
        ],
        "link_pattern": r'/en/jobs/\d+/',
    },
    "Robota.ua": {
        "enabled": True,
        "urls": [
            "https://robota.ua/ua/jobs/webflow",
            "https://robota.ua/ua/jobs/shopify",
            "https://robota.ua/ua/jobs/no-code",
        ],
    },
    "HH.ua": {
        "enabled": True,
        "urls": [
            "https://hh.ua/search/vacancy?text=webflow+developer&area=5",
            "https://hh.ua/search/vacancy?text=shopify+developer&area=5",
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
