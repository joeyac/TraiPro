# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import html5lib
import urllib2


def get_cf_list(page=1):
    """
    :param page: problem page num of codeforces
    :type page: int or str
    :return: dict of problem list and ac number
    :rtype: dict
    """
    url = 'http://codeforces.com/problemset/page/{pid}'.format(pid=page)
    page = urllib2.urlopen(url, timeout=5)
    soup = BeautifulSoup(page, 'html5lib')
    table = soup.find('table', {'class': 'problems'})
    trs = table.find_all('tr')
    data = {}
    for tr in trs[1:]:
        td = tr.find_all('td')
        data[td[0].text.strip()] = td[-1].text.strip()[1:]
    return data


if __name__ == '__main__':
    get_cf_list()