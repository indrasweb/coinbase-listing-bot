import logging
import time
from math import floor

import krakenex


kraken = krakenex.API()
kraken.load_key('kraken.key')

assets = {'XRP': {'pd': 5, 'vd': 8, 'dumb_name': 'XXRPZEUR'},
          'REP': {'pd': 3, 'vd': 8, 'dumb_name': 'XREPZEUR', 'leverage': 2},
          'ZEC': {'pd': 3, 'vd': 8, 'dumb_name': 'XZECZEUR'},
          'XMR': {'pd': 2, 'vd': 8, 'dumb_name': 'XXMRZEUR', 'leverage': 2},
          'EOS': {'pd': 4, 'vd': 8, 'dumb_name': 'EOSEUR'},
          'XLM': {'pd': 6, 'vd': 8, 'dumb_name': 'XXLMZEUR'},
          'GNO': {'pd': 2, 'vd': 8, 'dumb_name': 'GNOEUR'},
          'DASH': {'pd': 3, 'vd': 8, 'dumb_name': 'DASHEUR'}}


def round_down(n, d):
  """
  return n, rounded down to d decimal places
  """
  d = int('1' + ('0' * d))
  return floor(n * d) / d


def get_price(coin, attempts=5):
  """
  Return average price of :coin: on Kraken over the last 120 minutes,
  trying :attempts: times to get OHLC ticks from Kraken.
  """
  query_data = {'pair': '{}EUR'.format(coin),
                'since': int(time.time()-60*120)}

  for attempt in range(attempts):

    try:
      response = kraken.query_public('OHLC', query_data)
      ticks = response['result'][assets[coin]['dumb_name']]
      avg = sum([float(t[4]) for t in ticks]) / len(ticks)
      return avg

    except Exception as e:
      logging.error('Exception in get_price({}) :: {}'.format(coin, e))
      continue

  raise Exception('After {} attempts get_price({}) aborted'\
                  .format(attempts, coin))


def buy(coin, spend, multiplier, attempts=5):
  """
  Place buy order on Kraken for :coin: using euro :spend: with
  maximum available leverage, paying :multiplier: more than average
  over the last 120 minutes. Tries :attempts: times before dying.
  """
  price = get_price(coin) * multiplier
  volume = spend / price
  round_price = str(round_down(price, assets[coin]['pd']))
  round_vol = str(round_down(volume, assets[coin]['vd']))
  order_data = {'pair': '{}EUR'.format(coin), 'type': 'buy',
                'ordertype': 'limit', 'price': round_price,
                'volume': round_vol}
  if 'leverage' in assets[coin]:
    order_data['leverage'] = assets[coin]['leverage']
    order_data['volume'] *= assets[coin]['leverage']

  for attempt in range(attempts):

    try:
      response = kraken.query_private('AddOrder', order_data)
      logging.info(response)
      if not response['error']:
        return

    except Exception as e:
      logging.error('Exception in get_price({}) :: {}'.format(coin, e))
      continue

  raise Exception('After {} attempts buy({}) aborted'.format(attempts, coin))
