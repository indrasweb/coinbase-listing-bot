# Coinbase listing bot

A silly little script that made me a nice bit of change from the summer of 2017 through to spring 2018.

It works as follows:

1. contstantly refresh the coinbase blog checking for new posts
2. if there is a new post, see if it's about them listing a new coin that is already on Kraken
3. calculate the average price (on Kraken) of that coin over the last 2 hours
4. place a limit buy order at ~4% over this price with the maximum leverage available for that coin
5. push a notification to your phone which makes an alarm go off

If there happens to be another *totally rational* crypto bull run, and "the Coinbase effect" takes hold again, this might serve as a template for someone to do something similar. 

It probably needs fixing, I've not touched it in a while. You'll have to fill in some API keys in `kraken.key`, and some other credentials at the top of `bot.py`.
