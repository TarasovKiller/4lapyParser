import requests
from bs4 import BeautifulSoup
import bs4
import os
from urllib.parse import urljoin
import json
from typing import Iterable, List


def get_page_products(items: list) -> Iterable[dict]:
    for item in items:
        productid = item.attrs['data-productid']
        product_articul = item.attrs['data-product-articul']

        card_info = item.find('div', class_='b-common-item__info-center-block')
        a = card_info.find("a")

        pattern = r"[\s]*(\w.*\w)[\s]*"

        brand = a.select_one('span.b-clipped-text span span')
        name = name = brand.find_next_sibling('span')
        brand = brand.text.strip()
        name = name.text.strip()

        href = a['href']
        href = urljoin("https://4lapy.ru/", href)

        price = card_info.find("span", class_='js-price-block').text

        yield {productid: {"brand": brand, "name": name, "href": href, "price": price}}


def get_page(session: requests.Session, page: int) -> (bs4.element.Tag, Iterable[dict]):
    params = {
        'section_id': '87',
        'sort': 'popular',
        'page': '',
        'partial': 'Y',
        'popup': 'false',
        'isShowFilter': 'false',
    }
    params['page'] = page
    response = session.get(
        'https://4lapy.ru/catalog/koshki/kogtetochki/', params=params)

    bs = BeautifulSoup(response.text, "html.parser")
    items = bs.find_all('div', class_='b-common-item--catalog-item')

    products = get_page_products(items)

    button = bs.find(class_='b-pagination__item--next')

    return button.find("a"), products


def run(session: requests.Session) -> List[dict]:
    page = 1
    products = []
    while True:
        print(page)
        flag, data = get_page(session, page=page)
        for product in data:
            products.append(product)
        if flag is None:
            break
        page += 1
    return products


def set_city(session: requests.Session, code: str) -> None:
    data = {
        'code': code
    }

    response = session.post(
        'https://4lapy.ru/ajax/user/city/set/', data=data)


def main():
    session = requests.Session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }
    session.headers.update(headers)

    # 'code': '0000073738',  # Москва
    print("Set Moscow Geo")
    set_city(session, "0000073738")
    moscow_products = run(session)

    # 'code': '0000103664',  # Санкт - Петербург
    print("Set Saint-Petersburg Geo")
    set_city(session, "0000073738")
    piter_products = run(session)

    result = [{"Moscow": moscow_products, "Saint-Petersburg": piter_products}]
    json_data = json.dumps(result, ensure_ascii=False)

    with open('data.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)


if __name__ == '__main__':
    main()
