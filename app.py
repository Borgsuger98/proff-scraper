import streamlit as st
import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

# Brukeragent for å unngå blokkering
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

BASE_URL = "https://www.proff.no/bransjes%C3%B8k/-/{bransjekode}/?q={bransjekode}"

def get_company_links(bransjekode, max_pages=3):
    company_links = []
    
    for page in range(1, max_pages + 1):
        url = BASE_URL.format(bransjekode=bransjekode) + f"&p={page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        
        for link in soup.find_all("a", class_="css-1l6n7rx"):  # Klassenavn kan variere
            href = link.get("href")
            if href and "/selskap/" in href:
                company_links.append("https://www.proff.no" + href)

        time.sleep(2)
    
    return company_links

def scrape_proff(url):
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    def find_text(label):
        tag = soup.find("span", text=label)
        return tag.find_next_sibling("span").text.strip() if tag else "Ukjent"

    name_tag = soup.find("h1")
    name = name_tag.text.strip() if name_tag else "Ukjent"
    orgnr = find_text("Organisasjonsnummer")
    address = find_text("Besøksadresse")
    phone = find_text("Telefon")
    
    return {"Navn": name, "Organisasjonsnummer": orgnr, "Adresse": address, "Telefon": phone, "URL": url}

st.title("Proff.no Scraper")

bransjekode = st.text_input("Skriv inn bransjekode")
if st.button("Start scraping"):
    if bransjekode:
        st.write("Scraper data...")
        company_links = get_company_links(bransjekode)
        
        if not company_links:
            st.error("Fant ingen bedrifter. Prøv en annen bransjekode!")
        else:
            data = []
            for link in company_links:
                info = scrape_proff(link)
                if info:
                    data.append(info)
                time.sleep(2)
            
            df = pd.DataFrame(data)
            st.dataframe(df)
            
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(label="Last ned CSV", data=csv, file_name="bedrifter.csv", mime="text/csv")
    else:
        st.error("Vennligst skriv inn en bransjekode!")
