# -*- coding: utf-8 -*-
import urllib2
import cookielib
from bs4 import BeautifulSoup
import re


def poj(problem_id):
    url = 'http://poj.org/problem?id={id}'.format(id=problem_id)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Ubuntu Chromium/52.0.2743.116 Chrome/52.0.2743.116 Safari/537.36',
        'Origin': "http://acm.hdu.edu.cn",
        'Host': "acm.hdu.edu.cn",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
    }
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)

    request = urllib2.Request(url)
    page = opener.open(request).read()
    num_p = re.compile(r'\d+')

    p = re.compile(r'Submissions:</b>\s*\d+\s*</td>')
    submission_html = p.findall(page)[0]
    submission_num = num_p.findall(submission_html)[0]

    p = re.compile(r'Accepted:</b>\s*\d+\s*</td>')
    ac_html = p.findall(page)[0]
    ac_num = num_p.findall(ac_html)[0]
    return {'submitted': submission_num, 'accepted': ac_num}


def hdu(problem_id):
    url = 'http://acm.hdu.edu.cn/showproblem.php?pid={id}'.format(id=problem_id)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Ubuntu Chromium/52.0.2743.116 Chrome/52.0.2743.116 Safari/537.36',
        'Origin': "http://acm.hdu.edu.cn",
        'Host': "acm.hdu.edu.cn",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
    }
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)

    request = urllib2.Request(url, headers=headers)
    page = opener.open(request).read()
    num_p = re.compile(r'\d+')

    p = re.compile(r'Total Submission\(s\):\s*\d+')
    submission_html = p.findall(page)[0]
    submission_num = num_p.findall(submission_html)[0]

    p = re.compile(r'Accepted Submission\(s\):\s*\d+')
    ac_html = p.findall(page)[0]
    ac_num = num_p.findall(ac_html)[0]
    return {'submitted': submission_num, 'accepted': ac_num}


def codeforces(problem_id, contest=False):  # problem_id = 124C / 12c
    contest_num = problem_id[:-1]
    problem_char = problem_id[-1:]
    url = 'http://codeforces.com/contest/{num}'
    url = url.format(num=contest_num)
    page = urllib2.urlopen(url, timeout=5)
    soup = BeautifulSoup(page, 'html5lib')
    table = soup.find('table', {'class': 'problems'})
    trs = table.find_all('tr')
    data = {}
    for tr in trs[1:]:
        td = tr.find_all('td')
        data[td[0].text.strip()] = td[-1].text.strip()[1:]
    if contest:
        res = {}
        for item in data:
            res[item] = {'submitted': None, 'accepted': data[item]}
        return res
    else:
        return {'submitted': None, 'accepted': data[problem_char.upper()]}


def get_problem_status(oj, problem_id):
    func = eval(oj.lower())
    return func(problem_id)

if __name__ == '__main__':
    print get_problem_status('poj', '2839')

