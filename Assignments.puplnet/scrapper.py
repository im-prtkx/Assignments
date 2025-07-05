# scraper.py

import requests
from bs4 import BeautifulSoup
import re

# List of IITK pages to scrape
urls = [
    "https://www.iitk.ac.in/counsel/",
    "https://voxiitk.com/",
    "https://iitk.ac.in/new/iitk-faculty",
    
]

headers = {"User-Agent": "Mozilla/5.0"}
all_text = []

def clean_text(text):
    # Remove multiple spaces, newline and HTML junk
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'©.*?IIT Kanpur.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(menu|footer|navbar|subscribe|login).*', '', text, flags=re.IGNORECASE)
    return text.strip()

for url in urls:
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, navs, and footers
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        body_text = soup.get_text()
        body_text = clean_text(body_text)
        print(f"✅ Scraped: {url} ({len(body_text)} chars)")
        all_text.append(body_text)

    except Exception as e:
        print(f"❌ Failed: {url}")
        print(e)

# Save to file
with open("cleaned_data.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_text))



