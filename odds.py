import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")
BOOKS = ["fanduel", "draftkings", "bet365"]
SPORT = "upcoming"
REGION = "us"
MARKET = "h2h"

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "bookmakers": ",".join(BOOKS)
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return f"Error fetching odds: {res.text}"
    return res.json()

def detect_arbitrage(data):
    arbs = []
    for game in data:
        outcomes = {}
        for book in game.get("bookmakers", []):
            for market in book.get("markets", []):
                for outcome in market.get("outcomes", []):
                    name = outcome["name"]
                    price = outcome["price"]
                    if name not in outcomes or price > outcomes[name]["price"]:
                        outcomes[name] = {"price": price, "book": book["title"]}
        if len(outcomes) >= 2:
            inv_sum = sum([1 / (out["price"] / 100 + 1) for out in outcomes.values()])
            if inv_sum < 1:
                profit = round((1 - inv_sum) * 100, 2)
                arbs.append({
                    "teams": game["teams"],
                    "commence_time": game["commence_time"],
                    "outcomes": outcomes,
                    "profit": profit
                })
    return arbs
