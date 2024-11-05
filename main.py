from pathvalidate import sanitize_filename
from urllib.parse import urlsplit
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from time import sleep
import requests
import argparse
import os


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_image(url, folder="image_books/"):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status() 
    check_for_redirect(response)
    name_image = urlsplit(url).path.split('/')[-1]
    filepath = os.path.join(folder, name_image)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_txt(url, filename, folder="books/"):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status() 
    check_for_redirect(response)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(response, book_url):
    soup = BeautifulSoup(response.text, 'lxml')
    book_image_url = soup.find('div', class_='bookimage').find('img')['src']
    book_text = soup.find_all('div', class_='texts')
    comments = [comment.find('span', class_='black').text for comment in book_text]
    book_genres =  soup.find('span', class_='d_book').find_all('a')
    title = soup.find('h1').text
    title_book, book_author  = title.split(' :: ')
    genre_book = [genres.text for genres in book_genres]
    image_url = urljoin(book_url, book_image_url)
    book_parameters = {
        "title_book": title_book,
        "book_author": book_author,
        "book_genres": genre_book,
        "image_url": image_url,
        "comments": comments
    }
    return book_parameters


def main():
    parser = argparse.ArgumentParser(
        description='В проекте скачиваются книги, их изображения, а также  описание книг'
    )
    parser.add_argument('--start_id', type=int, help='начальный id книги', default=1)
    parser.add_argument('--end_id', type=int, help='конечный id книги', default=702)
    args = parser.parse_args()
    for number in range(args.start_id, args.end_id ):
        try:
            book_url = f"https://tululu.org/b{number}/"
            response = requests.get(book_url)
            response.raise_for_status() 
            check_for_redirect(response)
            book_parameters = parse_book_page(response, book_url)
            download_image(book_parameters["image_url"])
            url = f"https://tululu.org/txt.php?id={number}"
            filename = book_parameters["title_book".strip()].txt
            download_txt(url, filename)
        except requests.exceptions.HTTPError:
            print("Книга не найдена")
        except requests.exceptions.ConnectionError:
            print("Не удалось подключится к серверу")
            sleep(20)


if __name__ == "__main__":
    main()