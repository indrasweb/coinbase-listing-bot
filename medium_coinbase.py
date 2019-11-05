import logging
import time

import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException


def sign_into_medium(driver, username, password):
  """
  use :username: and :password: to log into medium - this is needed
  otherwise there is ~1m30s latency before receiving any new post.
  When logged in + javascript on the latency is only ~5s.
  """
  driver.get('https://medium.com/')

  try:
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div[2]/button').click()
  except:
    pass

  driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div[1]/div[2]/div/a[2]').click()
  time.sleep(3)

  driver.find_element_by_class_name('js-googleButton').click()
  time.sleep(3)

  driver.find_element_by_xpath('//*[@id="identifierId"]').send_keys(username)
  driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div/'
                               'div[1]/div/content/span').click()
  time.sleep(3)

  driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/content/'
                               'form/div[1]/div/div[1]/div/div[1]/input').send_keys(password)
  driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div/'
                               'div[1]/div/content/span').click()
  time.sleep(3)

  try:
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div/div[2]/button').click()
  except:
    pass

  try:
    driver.get('https://medium.com/me')
    time.sleep(3)
    name = driver.find_element_by_xpath('/html/body/div/div/section/div[1]/div[2]/div[2]/h1').text
    logging.info('Logged in as {}'.format(name))
  except NoSuchElementException:
    driver.save_screenshot('abort.png')  # haz captcha?
    logging.error('Couldn\'t sign into Medium\nAborting, screenshot saved.')
    exit(1)


def get_latest_post_url(driver):
  """
  return the url of the latest post on the blog
  """
  driver.get('https://blog.coinbase.com/latest')
  a = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[4]/div/div[1]/div/'
                                   'div/div/div/div/div[1]/div/div/div[2]/div/a')
  latest_post_url = a.get_attribute('href')

  return latest_post_url


def scrape_post_to_plaintext(url):
  """
  return plaintext post body from blog.coinbase.com/x url
  """
  browser_header = {'User-Agent': 'Mozilla/5.0'}
  raw = requests.get(url, headers=browser_header)
  soup = BeautifulSoup(raw.text, 'html5lib')

  raw_post_body = soup.find('div', attrs={'class':'section-inner'})
  raw_paragraphs = raw_post_body.find_all('p')
  raw_subtitles = raw_post_body.find_all('h3')
  paragraphs = ''.join([para.text + ' ' for para in raw_paragraphs])
  subtitles = ''.join([subs.text + '\n' for subs in raw_subtitles])

  try:
    title = soup.find('h1').strong.text
  except AttributeError:
    title = soup.find('h1').text

  body = subtitles + '\n\n' + paragraphs
  post = title + '\n\n' + body

  return post


def analyse_post_for_coins_to_buy(plaintext_post, coin_keywords):
  """
  analyse :plaintext_post: string for any words corresponding to
  tokens on Kraken in :coin_keywords:
  I don't need to check if they're delisting something because my
  list of candidate coins precludes coins already listed.
  """
  candidate_coins = []
  lowercase_post = plaintext_post.lower()

  for coin, coin_keywords in coin_keywords.items():
    for keyword in coin_keywords:
      if ' '+keyword+' ' in lowercase_post \
      or '('+keyword+')' in lowercase_post\
      or ' '+keyword+'.' in lowercase_post\
      or ' '+keyword+', ' in lowercase_post:
        candidate_coins.append(coin)

  return candidate_coins
