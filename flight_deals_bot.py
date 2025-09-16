import os
import requests
from dotenv import load_dotenv

# Φόρτωση .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
ORIGIN = os.getenv("ORIGIN", "ATH")
DESTINATION = os.getenv("DESTINATION", "BCN")
DEPARTURE_DATE = os.getenv("DEPARTURE_DATE")
RETURN_DATE = os.getenv("RETURN_DATE")
ADULTS = os.getenv("ADULTS", "1")
CURRENCY = os.getenv("CURRENCY", "EUR")

AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

# --------------------------------------------------------------------
# Telegram
# --------------------------------------------------------------------
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print("Telegram error:", e)

# --------------------------------------------------------------------
# Amadeus
# --------------------------------------------------------------------
def get_amadeus_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET,
    }
    r = requests.post(AMADEUS_TOKEN_URL, data=data, timeout=20)
    r.raise_for_status()
    return r.json().get("access_token")

def search_flights(token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": ORIGIN,
        "destinationLocationCode": DESTINATION,
        "departureDate": DEPARTURE_DATE,
        "returnDate": RETURN_DATE,
        "adults": ADULTS,
        "currencyCode": CURRENCY,
        "max": 20,
    }
    r = requests.get(AMADEUS_SEARCH_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

def best_offer(offers):
    best = None
    for o in offers:
        try:
            price = float(o.get("price", {}).get("grandTotal") or 0)
        except Exception:
            continue
        if best is None or price < best:
            best = price
    return best

# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
if __name__ == "__main__":
    try:
        token = get_amadeus_token()
        offers = search_flights(token)
        best = best_offer(offers)

        if best:
            send_telegram_message(f"Lowest price today: €{best}")
            print(f"Lowest price today: €{best}")
        else:
            send_telegram_message("No offers found today.")
            print("No offers found today.")

    except Exception as e:
        print("Error:", e)
        send_telegram_message(f"Error: {e}")
