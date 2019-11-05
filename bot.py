import pushover
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER

from medium_coinbase import *
from kraken import *


PUSHOVER_KEY = None
PUSHOVER_SECRET = None
MEDIUM_LOGIN_EMAIL = None
MEDIUM_LOGIN_PASSWORD = None
MAX_SPEND_EUROS = 40000

logging.basicConfig(filename='session.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('chardet.charsetprober').setLevel(logging.INFO)
LOGGER.setLevel(logging.WARNING)
logging.info('Initializing...')


options = Options()
options.add_argument('-headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(chrome_options=options)
driver.implicitly_wait(10)
logging.info('Logging into medium...')
sign_into_medium(driver, MEDIUM_LOGIN_EMAIL, MEDIUM_LOGIN_PASSWORD)


notify = pushover.Client(user_key=PUSHOVER_KEY, api_token=PUSHOVER_SECRET)


thesaurus = {'DASH': ['dash'],
             'XRP':  ['ripple', 'xrp'],
             'ZEC':  ['zec', 'zcash', 'z-cash'],
             'EOS':  ['eos'],
             'XLM':  ['xlm', 'stellar'],
             'XMR':  ['xmr', 'monero'],
             'REP':  ['rep', 'augur'],
             'GNO':  ['gno', 'gnosis']}


def get_priority_coin_to_buy(coin_list):
  """
  return the coin in :coin_list: with the lowest market cap
  and highest leverage available.
  """
  priority = ['REP', 'XMR', 'GNO', 'ZEC', 'DASH', 'XLM', 'EOS', 'XRP']
  sort = [coin for coin in priority if coin in coin_list]
  if sort:
    return sort[0]
  return None


latest_post_url = get_latest_post_url(driver)
logging.info('Latest post has url:' + latest_post_url)
logging.info('Entering main loop...')

while True:

  start = time.time()

  try:
    new_latest_post_url = get_latest_post_url(driver)
  except Exception as e:
    logging.warning('Error requesting latest post :: {}'.format(e))
    continue

  if new_latest_post_url == latest_post_url:  # post isn't different
    continue  # re-check as frequently as possible

  try:
    plaintext_post = scrape_post_to_plaintext(new_latest_post_url)
  except Exception as e:
    logging.info('scrape_post_to_plaintext({}) failed :: {}'\
                 .format(new_latest_post_url, e))
    continue

  latest_post_url = new_latest_post_url
  matches = analyse_post_for_coins_to_buy(plaintext_post, thesaurus)
  coin_to_buy = get_priority_coin_to_buy(matches)

  if coin_to_buy:
    try:
      buy(coin_to_buy, spend=MAX_SPEND_EUROS, multiplier=1.04)
    except Exception as e:
      logging.error('buy({}) aborted - exiting :: {}'.format(coin_to_buy, e))
      break

    notify.send_message('Coinbase listed {}, buy order placed for {}'\
                        .format(str(matches), coin_to_buy))
    logging.info('Coinbase listed {}, buy order placed for {}'\
                 .format(str(matches), coin_to_buy))
    break

  logging.info('New blogpost \'{}\' at {}'\
               .format(latest_post_url, time.time()))
