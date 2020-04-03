import requests
import re
from bs4 import BeautifulSoup
from graphviz import Digraph
from urllib.parse import urlparse

HORIZONTAL_LIMIT = 5
VERTICAL_LIMIT = 5

graph = Digraph()
history = []
paths = [['/2020/03/preserving-optionality/', 0]]

def main():
    while len(paths) > 0:
        [path, depth] = paths.pop()
        scrape_path(path, depth)

    graph.save('output.dot')

def scrape_path(path, depth):
    print(f'{len(paths) + 1} paths remaining.')
    print(f'scraping {path}...')

    page = requests.get('https://fs.blog' + path)
    soup = BeautifulSoup(page.content, 'html.parser')

    history.append(path)

    title = get_title(soup)
    graph.node(path, title)

    links = soup.find_all('a')
    urls = map(lambda link: link.get('href'), links)
    dest_paths = map(filter_and_normalize_url, urls)
    dest_paths = filter(lambda path: path, dest_paths)
    dest_paths = list(dest_paths)
    dest_paths = dest_paths[:min(len(dest_paths), HORIZONTAL_LIMIT)]
    for dest_path in dest_paths:
        queue_path(path, dest_path, depth)

def filter_and_normalize_url(url):
    url = urlparse(url)
    # Filter out non-FS articles
    if url.netloc != 'fs.blog' and url.netloc is not None:
        return None
    # Filter out non-blog-posts
    if not re.match(r'/\d\d\d\d/\d\d', url.path):
        return None
    return url.path

def queue_path(src_path, dest_path, depth):
    if depth > VERTICAL_LIMIT:
        return
    if dest_path is None:
        return
    graph.edge(src_path, dest_path)
    if dest_path in history:
        return
    paths.append([dest_path, depth + 1])


def get_title(soup):
    tags = soup.find_all(class_='entry-title')
    if len(tags) == 0:
        return None
    return tags[0].contents[0]


main()
