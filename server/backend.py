import requests
import time

from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import datetime

from transformers import pipeline

import gc
import torch
gc.collect()
torch.cuda.empty_cache()

month_dict = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 
    'June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 
    'November': '11', 'December': '12' 
}

short_month_dict = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 
    'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12' 
}

summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device = 0, truncation = True)

def scrape_mit(n_articles = 10):
    links_mit = []

    n_actual = 0
    k = 0
    while n_actual <= n_articles:
        URL_mit = "https://climate.mit.edu/news?sort_bef_combine=created_DESC&sort_by=created&sort_order=DESC&page=" + str(k)
        page_mit = requests.get(URL_mit)
        soup_mit = BeautifulSoup(page_mit.content, "html.parser")
        results_mit = soup_mit.find_all(class_="field-group-link card-link")
        k += 1


        for i in results_mit:
            try: 
                if ( i.find(class_="pseudo-author").get_text() == "MIT News"):
                    link = i['href']
                    links_mit.append("https://climate.mit.edu" + link)
                    n_actual += 1
            except:
                continue
        
    data_mit = pd.DataFrame(columns=['title', 'content', 'date'])

    def fetch(url):
        response = requests.get(url)
        return response.content

    def convert_date(date):
        date = date.split(" ")
        day = date[1].replace(",", "")
        month = date[0]
        year = date[2]
        month = month_dict[month]
        return year + "-" + month + "-" + day

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch, links_mit[:n_articles]))

    for i in range(n_articles):
        article_soup = BeautifulSoup(results[i], "html.parser")
        for script in article_soup(["script", "style"]):
            script.decompose()
        title = article_soup.find(class_='faux-full-title').get_text()
        date = article_soup.find(class_='type-date').get_text().replace("\n", " ").replace("\xa0", "")
        date = convert_date(date)
        content = article_soup.find(class_='clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item').get_text().replace("\n", " ").replace("\xa0", "")
        content = summarizer(content)[0]['summary_text']
        data_mit = pd.concat([data_mit, pd.DataFrame({'title': [title], 'content': [content], 'date': [date], 'source': ["MIT"], 'url': [links_mit[i]]})], ignore_index=True)

    return data_mit

def scrape_iea(n_articles = 10):
    n_pages = n_articles // 24 + 1
    links_iea = []

    for i in range(1, n_pages+1):
        URL_iea = "https://www.iea.org/news?page=" + str(i)
        page_iea = requests.get(URL_iea)
        soup_iea = BeautifulSoup(page_iea.content, "html.parser")
        results_iea = soup_iea.find_all("article")

        for i in results_iea:
            link = i.find('a')['href']
            links_iea.append("https://www.iea.org/" + link)
        
    data_iea = pd.DataFrame(columns=['title', 'content', 'date'])

    def fetch(url):
        response = requests.get(url)
        return response.content

    def convert_date(date):
        date = date.split(" ")
        day = date[0]
        month = date[1]
        year = date[2]
        month = month_dict[month]
        return year + "-" + month + "-" + day

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch, links_iea[:n_articles]))

    for i in range(n_articles):
        article_soup = BeautifulSoup(results[i], "html.parser")
        for script in article_soup(["script", "style"]):
            script.decompose()
        title = article_soup.find(class_='o-hero-freepage__title f-title-3').get_text()
        date = article_soup.find(class_='o-hero-freepage__meta').get_text().replace("\n", " ").replace("\xa0", "")
        date = convert_date(date)
        content = article_soup.find(class_='m-block m-block--text').get_text().replace("\n", " ").replace("\xa0", "")
        content = summarizer(content)[0]['summary_text']
        data_iea = pd.concat([data_iea, pd.DataFrame({'title': [title], 'content': [content], 'date': [date], 'source': ["IEA"], 'url': [links_iea[i]]})], ignore_index=True)

    return data_iea

def scrape_rn(n_articles = 10):
    n_pages = n_articles // 20 + 1
    links_rn = []

    for i in range(1, n_pages+1):
        URL_rn = "https://www.rechargenews.com/latest?page=" + str(i)
        page_rn = requests.get(URL_rn)
        soup_rn = BeautifulSoup(page_rn.content, "html.parser")
        results_rn = soup_rn.find_all(class_="teaser-body-image")

        for i in results_rn:
            link = i.find('a')['href']
            links_rn.append("https://www.rechargenews.com" + link)
        
    data_rn = pd.DataFrame(columns=['title', 'content', 'date'])

    def fetch(url):
        response = requests.get(url)
        return response.content

    def convert_date(date):
        date = date.split(" ")
        day = date[3]
        month = date[4]
        year = date[5]
        month = month_dict[month]
        return year + "-" + month + "-" + day

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch, links_rn[:n_articles]))

    for i in range(n_articles):
        article_soup = BeautifulSoup(results[i], "html.parser")
        for script in article_soup(["script", "style"]):
            script.decompose()
        title = article_soup.find(class_='fs-xxl fw-bold mb-4 article-title ff-sueca-bold').get_text().replace("\n", " ").replace("\xa0", "")
        date = article_soup.find(class_='pr-3').get_text().replace("\n", " ").replace("\xa0", "")
        date = convert_date(date)
        content = article_soup.find(class_='article-body').get_text().replace("\n", " ").replace("\xa0", "")
        content = summarizer(content)[0]['summary_text']
        data_rn = pd.concat([data_rn, pd.DataFrame({'title': [title], 'content': [content], 'date': [date], 'source': ["Recharge News"], 'url': [links_rn[i]]})], ignore_index=True)

    return data_rn

def scrape_en(n_articles = 10):
    n_pages = n_articles // 20 + 1
    links_en = []

    for i in range(1, n_pages+1):
        URL_en = "https://www.euronews.com/tag/energy?p=" + str(i)
        page_en = requests.get(URL_en)
        soup_en = BeautifulSoup(page_en.content, "html.parser")
        results_en = soup_en.find_all(class_="m-object__title qa-article-title")

        for i in results_en:
            link = i.find('a')['href']
            links_en.append("https://www.euronews.com" + link)
        
    data_en = pd.DataFrame(columns=['title', 'content', 'date'])

    def fetch(url):
        response = requests.get(url)
        return response.content

    def convert_date(date):
        date = date.split(":")
        date[1] = date[1].split(" ")
        date[1] = date[1][0]
        day = date[1].split("/")[0]
        month = date[1].split("/")[1]
        year = date[1].split("/")[2]
        return year + "-" + month + "-" + day

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch, links_en[:n_articles]))

    for i in range(n_articles):
        article_soup = BeautifulSoup(results[i], "html.parser")
        for script in article_soup(["script", "style"]):
            script.decompose()
        title = article_soup.find(class_='c-article-title').get_text().replace("\n", " ").replace("\xa0", "")
        date = article_soup.find(class_='c-article-date').get_text().replace("\n", " ").replace("\xa0", "")
        date = convert_date(date)
        content = article_soup.find(class_='js-responsive-iframes-container').get_text().replace("\n", " ").replace("\xa0", "")
        content = summarizer(content)[0]['summary_text']
        data_en = pd.concat([data_en, pd.DataFrame({'title': [title], 'content': [content], 'date': [date], 'source': ["Euronews"], 'url': [links_en[i]]})], ignore_index=True)

    return data_en

def scrape_mi(n_articles = 10):
    n_pages = n_articles // 5 + 1
    links_mi = []

    for i in range(1, n_pages+1):
        URL_mi = "https://mercomindia.com/archive/page-" + str(i)
        page_mi = requests.get(URL_mi)
        soup_mi = BeautifulSoup(page_mi.content, "html.parser")
        results_mi = soup_mi.find_all(class_="pt-cv-title")

        for i in results_mi:
            link = i.find('a')['href']
            links_mi.append(link)
        
    data_mi = pd.DataFrame(columns=['title', 'content', 'date'])

    def fetch(url):
        response = requests.get(url)
        return response.content

    def convert_date(date):
        date = date.split(" ")
        day = date[2].replace(",", "")
        month = date[1]
        year = date[3]
        month = short_month_dict[month]
        return year + "-" + month + "-" + day

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch, links_mi[:n_articles]))

    for i in range(n_articles):
        article_soup = BeautifulSoup(results[i], "html.parser")
        for script in article_soup(["script", "style"]):
            script.decompose()
        title = article_soup.find("div", {"id": "page-title-text"}).get_text().replace("\n", " ").replace("\xa0", "")
        date = article_soup.find(class_='entry-date').get_text().replace("\n", " ").replace("\xa0", "")
        date = convert_date(date)
        content = article_soup.find(class_='entry-content').get_text().replace("\n", " ").replace("\xa0", "").split("Listen to this article ")[1]
        content = summarizer(content)[0]['summary_text']
        data_mi = pd.concat([data_mi, pd.DataFrame({'title': [title], 'content': [content], 'date': [date], 'source': ["Mercom India"], 'url': [links_mi[i]]})], ignore_index=True)

    return data_mi

def main(n_articles_per_source):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        
        data_mit = executor.submit(scrape_mit, n_articles_per_source)
        data_iea = executor.submit(scrape_iea, n_articles_per_source)
        data_rn = executor.submit(scrape_rn, n_articles_per_source)
        data_en = executor.submit(scrape_en, n_articles_per_source)
        data_mi = executor.submit(scrape_mi, n_articles_per_source)

        
        data_mit = data_mit.result()
        data_iea = data_iea.result()
        data_rn = data_rn.result()
        data_en = data_en.result()
        data_mi = data_mi.result()

    data = pd.concat([data_mit, data_iea, data_rn, data_en, data_mi], ignore_index=True)
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by=['date'], ascending=False)
    data = data.to_dict(orient='records')
    return data

data = main(10)
print(data)