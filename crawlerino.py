"""Simple Python 3 web crawler, to be extended for various uses.

Prerequisites:
pip install requests
pip install beautifulsoup4
"""
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse
import bs4
import requests

#------------------------------------------------------------------------------
def crawler(startpage, maxpages=100, singledomain=True):
    """Crawl the web starting from specified page.

    1st parameter = URL of starting page
    maxpages = maximum number of pages to crawl
    singledomain = whether to only crawl links within startpage's domain
    """

    pagequeue = deque() # queue of pages to be crawled
    pagequeue.append(startpage)
    crawled = [] # list of pages already crawled
    domain = urlparse(startpage).netloc if singledomain else None

    pages = 0 # number of pages succesfully crawled so far
    failed = 0 # number of links that couldn't be crawled

    while pages < maxpages and pagequeue:
        url = pagequeue.popleft() # get next page to crawl (FIFO queue)

        # read the page
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema):
            print("*FAILED*:", url)
            failed += 1
            continue
        if not response.headers['content-type'].startswith('text/html'):
            continue # don't crawl non-HTML content

        # process the page
        crawled.append(url)
        pages += 1
        if pagehandler(url, response):
            # get the links from this page and add them to the crawler queue
            links = getlinks(url, response, domain)
            for link in links:
                if link not in crawled and link not in pagequeue:
                    pagequeue.append(link)

    print('{0} pages crawled, {1} links failed.'.format(pages, failed))

#------------------------------------------------------------------------------
def getlinks(pageurl, pageresponse, domain):
    """Returns a list of links from from this page to be crawled.

    pageurl = URL of this page
    pageresponse = page content; response object from requests module
    domain = domain being crawled (None to return links to *any* domain)
    """
    soup = bs4.BeautifulSoup(pageresponse.text, "html.parser")

    # get target URLs for all links on the page
    links = [a.attrs.get('href') for a in soup.select('a[href]')]

    # remove fragment identifiers
    links = [urldefrag(link)[0] for link in links]

    # remove any empty strings
    links = [link for link in links if link]

    # if it's a relative link, change to absolute
    links = [link if bool(urlparse(link).netloc) else urljoin(pageurl, link) \
        for link in links]

    # if only crawing a single domain, remove links to other domains
    if domain:
        links = [link for link in links if urlparse(link).netloc == domain]

    return links

#------------------------------------------------------------------------------
def pagehandler(pageurl, pageresponse):
    """Function to be customized for processing of a single page.

    pageurl = URL of this page
    pageresponse = page content; response object from requests module

    Return value = whether or not this page's links should be crawled.
    """
    print('Crawling:', pageurl)
    return True

#------------------------------------------------------------------------------
# if running standalone, crawl some Microsoft pages as a test
if __name__ == "__main__":
    from timeit import default_timer
    START = default_timer()
    crawler('http://www.microsoft.com', maxpages=10, singledomain=True)
    END = default_timer()
    print('Elapsed time (seconds) = ' + str(END-START))
