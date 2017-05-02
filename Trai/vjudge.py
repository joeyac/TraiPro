# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import html5lib
import urllib
import urllib2
import cookielib
import re
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class Vjudge:
    base_url = 'https://vjudge.net'
    problem_url = base_url + '/problem/{oj}-{problem}'
    desc_url = base_url + '/problem/description/{desc_id}?{desc_version}'
    login_url = 'https://vjudge.net/user/login'
    data_url = 'https://vjudge.net/contest/data'
    contest_url = 'https://vjudge.net/contest/{cid}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Ubuntu Chromium/52.0.2743.116 Chrome/52.0.2743.116 Safari/537.36',
        'Origin': "http://acm.hdu.edu.cn",
        'Host': "acm.hdu.edu.cn",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive',
    }

    def __init__(self):
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cookie)
        self.opener = urllib2.build_opener(handler)

    def login(self, user_id, password):
        data = {'username': user_id, 'password': password}
        post_data = urllib.urlencode(data)
        request = urllib2.Request(Vjudge.login_url, post_data, Vjudge.headers)
        response = self.opener.open(request).read()
        if response == 'success':
            return True
        else:
            print(response)
            return False

    def get_contests(self, user_id, password, status='participation', start_id=0):
        """
        :param user_id: vjudge user id
        :type user_id: string
        :param password: password of user
        :type password: string
        :param status: filter status, choice param
        :type status: string
        :param start_id: max exist id of contest
        :type start_id: integer
        :return: list of dict, like
                    [
                    {'contest_id': 1111, 'manager': 'username', 'title': 'contest 2017'},
                    {'contest_id': 1112, 'manager': 'username', 'title': 'contest 2018'},
                    ]
        :rtype: list
        """
        choice = ['mine', 'participation', 'arrangement', 'mygroup', 'favorites', 'follow']
        if status not in choice:
            print 'only accepted following status:', choice
            return
        self.login(user_id, password)
        data = {'order[0][column]': 4, 'order[0][dir]': 'desc', 'start': 0, 'length': -1,
                'category': status, 'running': 0, 'openness': -1}
        post_data = urllib.urlencode(data)
        request = urllib2.Request(Vjudge.data_url, post_data, Vjudge.headers)
        response = self.opener.open(request).read()
        contests = json.loads(response)['data']
        res = []
        # desc
        for ite in contests:
            if ite[0] <= start_id:
                break
            res.append({'contest_id': ite[0], 'title': ite[1], 'manager': ite[5],
                        'start_time': ite[2], 'end_time': ite[3]})
        return res

    def get_contest_info(self, contest_id):
        url = Vjudge.contest_url.format(cid=contest_id)
        page = self.opener.open(url, timeout=5)
        soup = BeautifulSoup(page, 'html5lib')
        text_area = soup.find('textarea')
        json_data = json.loads(text_area.text)
        problem_data = json_data['problems']
        problems = []
        for item in problem_data:
            problems.append({'vid': item['pid'], 'oj': item['oj'], 'pid': item['probNum'], 'title': item['title']})
        return problems

    def get_desc(self, desc_id, desc_version):
        """
        :param desc_id: id of description
        :type desc_id: integer or string
        :param desc_version: version of description
        :type desc_version: integer or string
        :return:    [
                    {'title':'','value':'<div></div>'},
                    {'title':'Input','value': '<div></div>'},
                    ......
                    ]
        :rtype: list of dict, single problem‘s desc,input,output and so on
        """
        url = Vjudge.desc_url.format(desc_id=desc_id, desc_version=desc_version)
        page = self.opener.open(url, timeout=10)
        soup = BeautifulSoup(page, 'html5lib')

        desc = soup.find('div', {'class': 'container'})
        dt = desc.find_all('dt')
        dd = desc.find_all('dd')
        info = []
        for i in range(len(dt)):
            if dd[i].contents:
                info.append({'title': dt[i].text, 'value': dd[i].prettify()[4:-4]})

        return info

    def get_problem_info(self, oj_name, problem_id):
        """
        :param oj_name: oj's name
        :type oj_name: string
        :param problem_id: problem's id
        :type problem_id: string or int
        :return: problem info to show or format html
                 {'Time limit': '1000 ms', 'Memory limit': '32768 kB', 'OS': 'Linux',
                 (optional)('Source':'xxx',)
                 'vid': 121314,
                 'title': hello world
                 'desc': {see return of get_desc},
                 }
        :rtype: dict
        """
        res = {}

        problem_url = Vjudge.problem_url.format(oj=oj_name, problem=problem_id)
        request = urllib2.Request(problem_url)
        page = self.opener.open(request)
        soup = BeautifulSoup(page, 'html5lib')

        dl_class = soup.find('dl', {'class': 'card'})
        dt_class = dl_class.find_all('dt')
        dd_class = dl_class.find_all('dd')
        title = soup.find('h2')

        res['title'] = title.text

        text_area = soup.find('textarea')
        vid = json.loads(text_area.text)['problemId']

        res['vid'] = vid

        for i in range(len(dt_class)):
            res[dt_class[i].text] = dd_class[i].text

        page = self.opener.open(request)
        html = page.read()

        p = re.compile(r'<a href="/problem/description/\d+\?\d+" target="_blank">')

        p_data = p.findall(html)[0]
        len_1 = len('<a href="/problem/description/')
        len_2 = len('" target="_blank">')
        qus = p_data.find('?')
        desc_id = p_data[len_1:qus]
        # print desc_id
        desc_version = p_data[len_1 + len(desc_id) + 1:-len_2]
        # print desc_version
        desc = self.get_desc(desc_id, desc_version)
        res['desc'] = desc
        return res

    @staticmethod
    def get_html(problem_info):
        """
        :param problem_info: return value of function(get_problem_info)
        :type problem_info: dict
        :return format html
        :rtype str
        """
        format_html = ''
        p_title = problem_info['title']
        time_limit = problem_info['Time limit']
        memory_limit = problem_info['Memory limit']
        os = problem_info['OS'] if 'OS' in problem_info else ''

        format_html += '<div style="width:960px;margin:auto"><h1>' + p_title + '</h1></div>'

        format_html += '<div style="width:960px;margin:auto"><span id="crawlSuccess" style="display: inline;' \
                       '"class="crawlInfo"><b>Time Limit:</b><span id="timeLimit"> ' + time_limit + \
                       '</span>&nbsp;&nbsp;&nbsp;&nbsp;<b>Memory Limit:</b><span id="memoryLimit">' + \
                       memory_limit + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<b>64bit IO Format:</b>' \
                                      '<span id="_64IOFormat">' + os + \
                       '</span></span></div><div style="width:960px;margin:auto">'

        for desc in problem_info['desc']:
            content = desc['value']
            if content:
                format_html += '<div style="display: block;"><h2>' + desc['title'] + \
                               '</h2><div class="textBG">' + content + '</div></div>'

        format_html += '</body></html>'
        return format_html


def get_problem(oj_name, problem_id):
    """
    :param oj_name: oj's name
    :type oj_name: string
    :param problem_id: problem's id
    :type problem_id: string or int
    :return: html code and info of certain problem
    :rtype: dict
    """
    try:
        robot = Vjudge()
        robot.login('traipro', 'letter_traipro')
        data = robot.get_problem_info(oj_name, problem_id)
        html = robot.get_html(data)
        return {'vid': data['vid'], 'title': data['title'], 'html': html}
    except Exception as e:
        return {'error': e}

if __name__ == '__main__':
    v = Vjudge()
    v.login('traipro', 'letter_traipro')
    dat = v.get_problem_info('CodeForces','1A')
    print dat

