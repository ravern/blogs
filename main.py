import requests
import re
from bs4 import BeautifulSoup
from graphviz import Digraph
from urllib.parse import urlparse

graph = Digraph()
history = []
paths = [['/2020/03/preserving-optionality/', 0]]

def main():
    while len(paths) > 0:
        if len(paths) > 100:
            break
        [path, depth] = paths.pop()
        scrape_path(path, depth)

    graph.render('output.gv')

def scrape_path(path, depth):
    print(f'{len(paths) + 1} paths remaining.')
    print(f'scraping {path}...')

    page = requests.get('https://fs.blog' + path)
    soup = BeautifulSoup(page.content, 'html.parser')

    history.append(path)

    title = get_title(soup)
    graph.node(path, title)

    links = soup.find_all('a')
    for link in links:
        url = link.get('href')
        queue_url(path, url, depth)

def filter_and_normalize_url(url):
    url = urlparse(url)
    # Filter out non-FS articles
    if url.netloc != 'fs.blog' and url.netloc is not None:
        return None
    # Filter out non-blog-posts
    if not re.match(r'/\d\d\d\d/\d\d', url.path):
        return None
    return url.path

def queue_url(src_path, url, depth):
    dest_path = filter_and_normalize_url(url)
    if depth > 2:
        return
    if dest_path is None:
        return
    if dest_path in history:
        return
    paths.append([dest_path, depth + 1])
    graph.edge(src_path, dest_path)


def get_title(soup):
    tags = soup.find_all(class_='entry-title')
    if len(tags) == 0:
        return None
    return tags[0].contents[0]


main()
