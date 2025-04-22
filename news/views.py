# #news/views.py

# from django.shortcuts import render
# import requests
# from bs4 import BeautifulSoup
# from newspaper import Article
# from django.core.cache import cache
# import math
# import time

# HEADERS = {"User-Agent": "Mozilla/5.0"}

# def fetch_hindu_articles():
#     url = "https://www.thehindu.com/news/national/"
#     response = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     articles = []

#     for link in soup.find_all('a', href=True):
#         href = link['href']
#         if "/news/national/" in href and href.endswith(".ece"):
#             try:
#                 article = Article(href)
#                 article.download()
#                 article.parse()
#                 articles.append({
#                     'title': article.title,
#                     'content': article.text,
#                     'url': href,
#                     'source': "The Hindu",
#                     'read_time': math.ceil(len(article.text.split()) / 200)
#                 })
#             except:
#                 continue
#             if len(articles) >= 10:
#                 break
#     return articles


# def fetch_indian_express_articles():
#     url = "https://indianexpress.com/section/india/"
#     response = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = []

#     for link_tag in soup.find_all('a', href=True):
#         href = link_tag['href']
#         if href.startswith("https://indianexpress.com/article/india/") and href.endswith("/"):
#             try:
#                 article = Article(href)
#                 article.download()
#                 article.parse()
#                 articles.append({
#                     'title': article.title,
#                     'content': article.text,
#                     'url': href,
#                     'source': "Indian Express",
#                     'read_time': math.ceil(len(article.text.split()) / 200)
#                 })
#             except Exception as e:
#                 print(f"Failed to fetch IE article: {href} - {e}")
#                 continue
#             if len(articles) >= 10:
#                 break
#     return articles


# def fetch_toi_articles():
#     url = "https://timesofindia.indiatimes.com/briefs"
#     response = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = []

#     briefs_section = soup.find_all('div', class_='brief_box')

#     for brief in briefs_section[:10]:
#         try:
#             title_tag = brief.find('h2')
#             title = title_tag.text.strip() if title_tag else "No title"

#             link_tag = brief.find('a', href=True)
#             link = f"https://timesofindia.indiatimes.com{link_tag['href']}" if link_tag else "#"

#             article = Article(link)
#             article.download()
#             article.parse()

#             articles.append({
#                 'title': article.title,
#                 'content': article.text,
#                 'url': link,
#                 'source': "Times of India",
#                 'read_time': math.ceil(len(article.text.split()) / 200)
#             })
#         except Exception as e:
#             continue
#     return articles


# def fetch_all_articles():
#     cached_articles = cache.get('all_news_articles')
#     if cached_articles:
#         print("✅ Loaded from cache")
#         return cached_articles

#     print("⏳ Fetching fresh articles")
#     hindu = fetch_hindu_articles()
#     ie = fetch_indian_express_articles()
#     toi = fetch_toi_articles()

#     all_articles = hindu + ie + toi
#     cache.set('all_news_articles', all_articles, 1800)  # Cache for 30 minutes (1800 seconds)
#     return all_articles


# def home(request):
#     start = time.time()
#     all_articles = fetch_all_articles()
#     end = time.time()
#     print(f"Time taken: {end - start:.2f} seconds")
#     return render(request, 'news/home.html', {'articles': all_articles})


# news/views.py

from django.shortcuts import render
from bs4 import BeautifulSoup
from newspaper import Article
from django.core.cache import cache
import asyncio
import aiohttp
import math
import time



HEADERS = {"User-Agent": "Mozilla/5.0"}

# Async function to fetch page HTML
async def fetch_html(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()

# Async version of The Hindu fetcher
async def fetch_hindu_articles(session):
    articles = []
    url = "https://www.thehindu.com/news/national/"
    try:
        html = await fetch_html(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if "/news/national/" in href and href.endswith(".ece"):
                try:
                    article = Article(href)
                    article.download()
                    article.parse()
                    articles.append({
                        'title': article.title,
                        'content': article.text,
                        'url': href,
                        'source': "The Hindu",
                        'read_time': math.ceil(len(article.text.split()) / 200)
                    })
                except:
                    continue
                if len(articles) >= 10:
                    break
    except Exception as e:
        print(f"Failed to fetch Hindu: {e}")
    return articles


# Async version of Indian Express fetcher
async def fetch_indian_express_articles(session):
    articles = []
    url = "https://indianexpress.com/section/india/"
    try:
        html = await fetch_html(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            if href.startswith("https://indianexpress.com/article/india/") and href.endswith("/"):
                try:
                    article = Article(href)
                    article.download()
                    article.parse()
                    articles.append({
                        'title': article.title,
                        'content': article.text,
                        'url': href,
                        'source': "Indian Express",
                        'read_time': math.ceil(len(article.text.split()) / 200)
                    })
                except:
                    continue
                if len(articles) >= 10:
                    break
    except Exception as e:
        print(f"Failed to fetch IE: {e}")
    return articles


# Async version of TOI fetcher
async def fetch_toi_articles(session):
    articles = []
    url = "https://timesofindia.indiatimes.com/briefs"
    try:
        html = await fetch_html(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        briefs = soup.find_all('div', class_='brief_box')
        for brief in briefs[:10]:
            try:
                title_tag = brief.find('h2')
                title = title_tag.text.strip() if title_tag else "No title"

                link_tag = brief.find('a', href=True)
                link = f"https://timesofindia.indiatimes.com{link_tag['href']}" if link_tag else "#"

                article = Article(link)
                article.download()
                article.parse()

                articles.append({
                    'title': article.title,
                    'content': article.text,
                    'url': link,
                    'source': "Times of India",
                    'read_time': math.ceil(len(article.text.split()) / 200)
                })
            except:
                continue
    except Exception as e:
        print(f"Failed to fetch TOI: {e}")
    return articles


# Wrapper to run all scrapers concurrently
async def scrape_all_sources():
    async with aiohttp.ClientSession() as session:
        hindu_task = fetch_hindu_articles(session)
        ie_task = fetch_indian_express_articles(session)
        toi_task = fetch_toi_articles(session)

        results = await asyncio.gather(hindu_task, ie_task, toi_task)
        all_articles = results[0] + results[1] + results[2]
        return all_articles


def fetch_all_articles():
    cached = cache.get('all_news_articles')
    if cached:
        print("✅ Loaded from cache")
        return cached

    print("⏳ Fetching async fresh articles")
    all_articles = asyncio.run(scrape_all_sources())
    cache.set('all_news_articles', all_articles, 1800)  # 30 minutes
    return all_articles


def home(request):
    start = time.time()
    all_articles = fetch_all_articles()
    end = time.time()
    print(f"Time taken: {end - start:.2f} seconds")
    return render(request, 'news/home.html', {'articles': all_articles})
