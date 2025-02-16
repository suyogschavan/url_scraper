from bs4 import BeautifulSoup
import requests
def scrape_metadata(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        description = soup.find("meta", attrs={"name": "description"})
        keywords = soup.find("meta", attrs={"name": "keywords"})

        return {
            "url": url,
            "title": title,
            "description": description["content"] if description else "No Description",
            "keywords": keywords["content"] if keywords else "No Keywords"
        }
    except:
        return None
    
print(scrape_metadata("https://www.psycopg.org")) # {'url': 'https://www.google.com', 'title': 'Google', 'description': 'No Description', 'keywords': 'No Keywords'}