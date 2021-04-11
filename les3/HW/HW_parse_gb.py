from urllib.parse import urljoin
from typing import Callable
from HW_database.database import Database
import requests
import bs4
import datetime as dt


class GeekbrainsParse:

    def __init__(self, start_url, db: Database):
        self.db = db
        self.start_url = start_url
        self.tasks = []
        self.got_tasks = set()

    def get_response_from(self, url) -> requests.Response:
        return requests.get(url)

    def get_soup_from(self, url):
        return bs4.BeautifulSoup(self.get_response_from(url).text, 'lxml')

    def get_task(self, url, callback: Callable) -> Callable:
        def task():
            return callback(url)

        if not url in self.got_tasks:
            self.got_tasks.add(url)
            return task
        return lambda: None

    def add_tasks(self, urls: set, callback: Callable):
        for url in urls:
            self.tasks.append(self.get_task(url, callback))

    def parse_page(self, url):
        soup = self.get_soup_from(url)  # Поставил здесь, чтобы таски занимали меньше места (или выхлоп маленький?)
        pages = soup.find('ul', attrs={'class': 'gb__pagination'}).find_all('a')
        tasks_from_pages = set(urljoin(url, page.attrs.get('href')) for page in pages)
        self.add_tasks(tasks_from_pages, self.parse_page)
        posts = soup.find_all('div', attrs={'class': 'post-item event'})
        tasks_from_posts = set(urljoin(url, post.find('a').attrs.get('href')) for post in posts)
        self.add_tasks(tasks_from_posts, self.parse_post)

    def parse_post(self, url):
        soup = self.get_soup_from(url)
        return {
            'post_data': {
                'id': soup.find('comments').attrs.get('commentable-id'),
                'url': url,
                'post_title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'img_url': soup.find('img').attrs['src'],
                'post_date': dt.datetime.fromisoformat(soup.find('time').attrs['datetime'][:-6])
            },
            'author_data': {
                'id': soup.find('div', attrs={'itemprop': 'author'}).parent.attrs.get('href')[7:],
                'name': soup.find('div', attrs={'itemprop': 'author'}).text
            },
            'tags': [{'name': cat.text, 'url': urljoin(url, cat.attrs['href'])}
                     for cat in soup.find_all('a', attrs={'class': 'small'})],
            'comments': self.get_post_comments(soup.find('comments').attrs.get('commentable-id'))
        }

    def get_post_comments(self, post_id):
        url = f'https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc'
        response = self.get_response_from(url)
        return response.json()

    def run(self):
        self.tasks.append(self.get_task(self.start_url, self.parse_page))
        self.got_tasks.add(self.start_url)  # чтобы потом не смотреть впутсую первую страницу
        for task in self.tasks:
            task_result = task()
            if task_result:
                self.db.create_post(task_result)


if __name__ == '__main__':
    database = Database("sqlite:///HW_gb.db")
    url_to_parse = 'https://gb.ru/posts'
    gb_parser = GeekbrainsParse(url_to_parse, database)
    gb_parser.run()
