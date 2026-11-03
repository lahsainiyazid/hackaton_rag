import cloudscraper 
from bs4 import BeautifulSoup
def scrape_bourse_agro()->list[dict[str,str]]:
    url="https://bourseagro.com/prix/casa"
    scraper=cloudscraper.create_scraper()
    response=scraper.get(url)
    response.raise_for_status()
    soup=BeautifulSoup(response.text,"html.parser")
    products=[]
    for row in soup.select("tr[data-nom][data-prix]"):
        products.append({
        "name": row["data-nom"],
        "category": row["data-cat"],
        "price": float(row["data-prix"])
    })
    return products


if __name__=="__main__":
    prods=scrape_bourse_agro()
    print(prods)
