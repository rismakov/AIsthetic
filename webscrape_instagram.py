import pandas as pd

# import selenium
# from selenium import webdriver

from bs4 import BeautifulSoup
import requests


handle = "rebekkah_ism"
url = f'https://www.instagram.com/{handle}/?hl=en'

image_link_class = 'v1Nh3 kIKUG  _bz0w'

def get_insta_posts():
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver.get(url)

    # using soup
    print(url)
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    print(soup)
    sections = soup.find_all(True, {'class': image_link_class})

    print(sections[0])


if __name__ == "__main__": 
    get_insta_posts()   