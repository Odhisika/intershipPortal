"""Small wrapper around the Paystack API for initializing and verifying
transactions. Uses the `requests` library and the secret key configured
in settings.PAYSTACK_SECRET_KEY.
"""

import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(email, amount_ghs, reference, callback_url):
    """
    Initialize a Paystack transaction.
    amount_ghs: amount in Ghana Cedis (will be converted to pesewas).
    Returns the parsed JSON response from Paystack, or an error dict.
    """
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    payload = {
        "email": email,
        "amount": int(round(amount_ghs * 100)),  # convert GHS to pesewas
        "currency": "GHS",
        "reference": reference,
        "callback_url": callback_url,
    }
    try:
        response = requests.post(url, json=payload, headers=_headers(), timeout=15)
        return response.json()
    except requests.RequestException as exc:
        return {"status": False, "message": str(exc)}


def verify_transaction(reference):
    """
    Verify a Paystack transaction by reference.
    Returns the parsed JSON response from Paystack, or an error dict.
    """
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    try:
        response = requests.get(url, headers=_headers(), timeout=15)
        return response.json()
    except requests.RequestException as exc:
        return {"status": False, "message": str(exc)}
