import sys
import random
import operator
import pandas as pd
import numpy as np

random.seed(0)

# match 𝑞 to the neighbor with the highest bid
def get_greedy_bid(bids, curr_budget, orig_budget):
  for (advertiser, bid_amt) in bids:
    b = curr_budget[advertiser]
    if (b > bid_amt):
      curr_budget[advertiser] -= bid_amt
      return bid_amt
  return 0


def psi(x):
  return 1 - np.exp(x - 1)

# match 𝑞 to the neighbor 𝑖 that has the largest 𝑏𝑖𝑞 ∗ 𝜓(𝑥𝑢) value
def get_msvv_bid(bids, curr_budget, orig_budget):
  scaled_bids = {}
  for (advertiser, bid_amt) in bids:
    if (curr_budget[advertiser] > 0):
      x = (orig_budget[advertiser] - curr_budget[advertiser])/orig_budget[advertiser]
      psi_x = psi(x)
      scaled_bids[advertiser] = bid_amt * psi_x
          
  scaled_bids = sorted(scaled_bids.items(), key = operator.itemgetter(1), reverse = True)

  if not scaled_bids:
    return -1
  
  (advertiser, scaledBid) = scaled_bids[0]
  
  bids = dict(bids)
  bid = bids[advertiser]
  curr_budget[advertiser] -= bid
  
  return bid

# match 𝑞 to the neighbor with the highest unspent budget.
def get_balance_bid(bids, curr_budget, orig_budget):
  balance = {}
  for (advertiser, bid_amt) in bids:
    if (curr_budget[advertiser] > 0):
      balance[advertiser] = curr_budget[advertiser]
            
  balance = sorted(balance.items(), key = operator.itemgetter(1), reverse = True)
  bids = dict(bids)
  
  if not balance:
    return -1
  
  (adv, bal) = balance[0]
  bid = bids[adv]
  curr_budget[adv] -= bid
  
  return bid

def main(param):
  df = pd.read_csv('bidder_dataset.csv')

  budget = {}
  bids = {}

  for index, row in df.iterrows():
    if row['Advertiser'] not in budget:
      budget[row['Advertiser']] = row['Budget']
    if row['Keyword'] not in bids:
      bids[row['Keyword']] = {}
    bids[row['Keyword']][row['Advertiser']] = row['Bid Value']

  for key, val in bids.items():
    bids[key] = sorted(val.items(), key = operator.itemgetter(1), reverse = True)

  queries = []
  file = open('queries.txt', 'r')
  for line in file:
    queries.append(line.strip())

  epochs = 100
  revenue = 0

  algorithms = {
    'greedy': get_greedy_bid,
    'msvv': get_msvv_bid,
    'balance': get_balance_bid
  }

  for _ in range(epochs):
    random.shuffle(queries)
    copy_budget = dict(budget)
    for q in queries:
      revenue += algorithms[param](bids[q], copy_budget, budget)
  
  revenue = revenue / epochs
  max_rev_possible = sum(budget.values())

  print (revenue)
  print (revenue/ max_rev_possible)



allowed_params = ['greedy', 'msvv', 'balance']

if __name__ == '__main__':
  if len(sys.argv) != 2 or sys.argv[1] not in allowed_params:
    print ('Missing/Invalid Parameter')
  else: 
    main(sys.argv[1])
