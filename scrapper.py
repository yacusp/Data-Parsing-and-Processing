import requests
import re
from bs4 import BeautifulSoup as bs

_HH_LINK = 'https://hh.ru/search/vacancy'
_SJ_LINK = 'https://russia.superjob.ru/vacancy/search/'
_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 YaBrowser/22.1.4.837 Yowser/2.5 Safari/537.36'}


def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class JobScrapper:
    """Main class."""

    def __init__(self, vacancy):
        """Constructor."""

        self.storage = list()
        self._vacancy = vacancy
        self._parse_vacancy()

    def _parse_vacancy(self):
        """Vacancy parser."""

        self.storage.extend(self._parse_hh())
        self.storage.extend(self._parse_sj())

    def _parse_hh(self):
        """Headhunter parser."""
        vacancies_info = []

        params = {
            'text': self._vacancy,
            'search-input': 'name',
            'page': ''
        }

        req = requests.get(_HH_LINK, params=params, headers=_HEADERS)

        if req.ok:
            soup = bs(req.text, 'html.parser')
            page_block = soup.find('div', {'data-qa': 'pager-block'})
            if not page_block:
                last_page = '1'
            else:
                last_page = int(page_block.find_all('a', {'class': 'bloko-button'})[-2].getText())

        for page in range(0, last_page):
            params['page'] = page
            req = requests.get(_HH_LINK, params=params, headers=_HEADERS)
            if req.ok:
                soup = bs(req.text, 'html.parser')
                vacancies = soup.find('div', {'data-qa': 'vacancy-serp__results'}) \
                    .find_all('div', {'class': 'vacancy-serp-item'})
                for item in vacancies:
                    vacancies_info.append(self._parse_vacancy_hh(item))

        return vacancies_info

    def _parse_vacancy_hh(self, vacancy):
        """Headhunter vacancy parser."""

        vacancy_info = {}

        # vacancy name
        vacancy_name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText().replace(u'\xa0', u' ')
        vacancy_info['vacancy_name'] = vacancy_name

        # vacancy salary
        salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText() \
                .replace(u'\xa0', u'')

            salary = re.split(r'\s|<|>', salary)

            if salary[0] == 'до':
                salary_min = None
                if isint(salary[1]) and isint(salary[2]):
                    salary_max = int("".join([salary[1], salary[2]]))
                    salary_currency = salary[3]
                else:
                    salary_max = int(salary[1])
                    salary_currency = salary[2]
            elif salary[0] == 'от':
                if isint(salary[1]) and isint(salary[2]):
                    salary_min = int("".join([salary[1], salary[2]]))
                    salary_currency = salary[3]
                else:
                    salary_min = int(salary[1])
                    salary_currency = salary[2]
                salary_max = None
            else:
                if isint(salary[0]) and isint(salary[1]):
                    salary_min = int("".join([salary[0], salary[1]]))
                    if isint(salary[3]) and isint(salary[4]):
                        salary_max = int("".join([salary[3], salary[4]]))
                        salary_currency = salary[5]
                    else:
                        salary_max = int(salary[10])
                        salary_currency = salary[4]
                else:
                    salary_min = int(salary[0])
                    if isint(salary[2]) and isint(salary[3]):
                        salary_max = int("".join([salary[2], salary[3]]))
                        salary_currency = salary[4]
                    else:
                        salary_max = int(salary[2])
                        salary_currency = salary[3]

        vacancy_info['salary_min'] = salary_min
        vacancy_info['salary_max'] = salary_max
        vacancy_info['salary_currency'] = salary_currency

        # vacancy link
        vacancy_link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
        vacancy_info['vacancy_link'] = vacancy_link

        # vacancy site
        vacancy_info['site'] = 'hh.ru'

        return vacancy_info

    def _parse_sj(self):
        """Superjob parser."""

        vacancies_info = []

        params = {
            'keywords': self._vacancy,
            'profession_only': '1',
            'page': ''
        }

        req = requests.get(_SJ_LINK, params=params, headers=_HEADERS)

        if req.ok:
            soup = bs(req.text, 'html.parser')
            page_block = soup.find('a', {'class': 'icMQ_'})
        if not page_block:
            last_page = 1
        else:
            page_block = page_block.findParent()
            last_page = int(page_block.find_all('a')[-1].getText())

        for page in range(0, last_page + 1):
            params['page'] = page
            req = requests.get(_SJ_LINK, params=params, headers=_HEADERS)

            if req.ok:
                soup = bs(req.text, 'html.parser')
                vacancy_items = soup.find_all('div', {'class': '_2G0xv'})

                for item in vacancy_items:
                    vacancies_info.append(self._parse_vacancy_sj(item))

        return vacancies_info

    def _parse_vacancy_sj(self, vacancy):
        """Superjob vacancy parser."""

        vacancy_info = {}

        # vacancy name
        vacancy_name = vacancy.find_all('a')
        vacancy_name = vacancy_name[0].getText()
        vacancy_info['vacancy_name'] = vacancy_name

        # vacancy salary
        salary = vacancy.find('span', {'class': '_2Wp8I'}) \
            .findChildren()
        if salary[0].getText() == 'По договорённости':
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary[1].getText().split()
            salary_currency = salary[-1]
            if salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1] + salary[2])
            elif salary[0] == 'от':
                salary_min = int(salary[1] + salary[2])
                salary_max = None
            elif len(salary) == 3:
                salary_min = salary_max = int(salary[0] + salary[1])
            else:
                salary_min = int(salary[0] + salary[1])
                salary_max = int(salary[3] + salary[4])

        vacancy_info['salary_min'] = salary_min
        vacancy_info['salary_max'] = salary_max
        vacancy_info['salary_currency'] = salary_currency

        # vacancy link
        vacancy_link = vacancy.find_all('a')
        if len(vacancy_link) > 1:
            vacancy_link = vacancy_link[-2]['jNMYr GPKTZ _1tH7S']
        else:
            vacancy_link = vacancy_link[0]['jNMYr GPKTZ _1tH7S']
        vacancy_info['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'

        # vacancy site
        vacancy_info['site'] = 'www.superjob.ru'

        return vacancy_info