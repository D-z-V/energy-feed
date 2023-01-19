import uuid
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from requests_futures.sessions import FuturesSession
from newspaper import Article
import concurrent.futures

req = 0

short_month_dict = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}

def query_search(search_term):
    global req
    req += 1
    links = []
    google_xml = []
    url = 'https://news.google.com/rss/search?q=' + search_term.replace(" ", "%20") + "+&hl=en-US&gl=US&ceid=US%3Aen"
    print(url)
    try:
        google_news = requests.get(url)
        soup = BeautifulSoup(google_news.content, "html.parser")
        for i in soup.find_all("item"):
            links.append(i.find('description').get_text().split('href="')[1].split('"')[0])
            xml_data = {
                "title": i.find('title').get_text(),
                "link": i.find('description').get_text().split('href="')[1].split('"')[0],
                "date": i.find('pubdate').get_text(),
                "source": i.get_text().split('</font>')[1] + " via (Google News)"
            }
            google_xml.append(xml_data)
    except:
        pass

    def convert_date(date):
        date = date.split(" ")
        day = date[1]
        month = date[2]
        year = date[3]
        month = short_month_dict[month]
        return year + "-" + month + "-" + day

    def download_article(url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article
        except:
            pass

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_article, url) for url in links]

        results = []

        for future in as_completed(futures):
            try:
                index = futures.index(future)
                article = future.result()
                title = article.title
                date = convert_date(google_xml[index]['date'])
                text = article.text
                source = google_xml[index]['source']
                image = article.top_image
                url = google_xml[index]['link']
                if text == None:
                    continue
                results.append({
                    "title": title,
                    "date": date,
                    "content": text,
                    "source": source,
                    "image": image,
                    "id": str(uuid.uuid1()),
                    "url": url
                })
            except:
                continue

        return results
    
    except:
        return []