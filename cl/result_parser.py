from requests import request as req
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_and_parse(url):
    return parse_results(get_query_result(url))


def get_query_result(url):
    result = req("get", url)
    if result.status_code == 200:
        return result.content.decode('utf-8', 'ignore')

    raise Exception("error fetching url {}, {}".format(url, result.status_code))


def parse_results(raw_html):
    """
    Parse the html retrieved from the best site on the internet.
    :param raw_html:
    :return: List of map of interesting traits of the page.
    """
    results = []
    soup = BeautifulSoup(raw_html, "html5lib")
    rows = soup.find('ul', 'rows').find_all('li', 'result-row')
    for row in rows:
        url = row.a['href']
        try:
            price = row.find('span', class_='result-price').get_text()
            price = int(price[1:])
        except:
            price = -1
        timestamp = row.find('time', class_='result-date').get('datetime')
        id = int(row.p.a['data-id'])
        hood_attr = row.find('span', class_='result-hood')
        place = ""
        if hood_attr is not None:
            place = hood_attr.get_text()[2:-1]
        create_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        title = row.find_all('a')[1].get_text()
        results.append(
            {'url': url, 'id': id, 'create_time': create_date, 'title': title, 'price': price, 'place': place})
    return results


def format_time(dt):
    return datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')


def get_current_time():
    return format_time(datetime.now())

get_and_parse('https://sfbay.craigslist.org/search/mca?query=honda+rebel+500')