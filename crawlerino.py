"""Simple Python 3 web crawler, to be extended for various uses.

Prerequisites:
pip install requests
pip install beautifulsoup4
"""
import bs4
import requests
import re
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

def crawler(startpage, maxpages=100, singledomain=True):
    """Crawl the web starting from specified page.

    1st parameter = starting page url
    maxpages = maximum number of pages to crawl
    singledomain = whether to only crawl links within startpage's domain
    """

    pagequeue = deque() # queue of pages to be crawled
    pagequeue.append(startpage)
    crawled = [] # list of pages already crawled
    domain = urlparse(startpage).netloc # for singledomain option

    pages = 0 # number of pages succesfully crawled so far
    failed = 0 # number of pages that couldn't be crawled

    while pages < maxpages and pagequeue:
        url = pagequeue.popleft() # get next page to crawl (FIFO queue)

        try:
            response = requests.get(url)
        except:
            print("*FAILED*:", url)
            failed += 1

        if not response.headers['content-type'].startswith('text/html'):
            continue # don't crawl non-HTML links

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        print('Crawling:', url)
        pages += 1
        crawled.append(url)

        # PROCESSING CODE GOES HERE:
        # do something interesting with this page

        # get target URLs for all links on the page
        links = [a.attrs.get('href') for a in soup.select('a[href]')]
        # remove fragment identifiers
        links = [urldefrag(link)[0] for link in links]
        # remove any empty strings
        links = list(filter(None,links))
        # if it's a relative link, change to absolute
        links = [link if bool(urlparse(link).netloc) else urljoin(url,link) for link in links]
        # if singledomain=True, remove links to other domains
        if singledomain:
            links = [link for link in links if (urlparse(link).netloc == domain)]

        # add these links to the queue (except if already crawled)
        for link in links:
            if link not in crawled and link not in pagequeue:
                pagequeue.append(link)

    print('{0} pages crawled, {1} pages failed to load.'.format(pages, failed))


# if running standalone, crawl some Microsoft pages as a test
if __name__ == "__main__":
    crawler('http://www.microsoft.com', maxpages=30, singledomain=True)
