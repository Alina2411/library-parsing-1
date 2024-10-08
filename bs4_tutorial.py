from bs4 import BeautifulSoup
import requests


url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
book_url = soup.find('main').find('header').find('h1')
book_text = book_url.text
image_url = soup.find('img', class_='attachment-post-image')['src']
