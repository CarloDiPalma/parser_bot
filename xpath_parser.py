import os

import requests
from urllib.request import urlopen
from lxml import etree

path = os.getcwd()


def parse(url, xpath):
    headers = {'Content-Type': 'text/html', }
    response = requests.get(url, headers=headers)
    html = response.text
    with open('parse.html', 'w', encoding="utf-8") as f:
        f.write(html)

    local = 'file:///' + path + '/parse.html'
    response = urlopen(local)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(response, htmlparser)
    price = tree.xpath(xpath)
    print(price)
    if isinstance(price, list):
        price = str(price)

    return price
