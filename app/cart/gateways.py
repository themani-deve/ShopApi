import requests
from core import settings


class ZarinpalGateway:
    def __init__(self, amount, description=None, callback_url=None, authority_token=None):
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID
        self.amount = f"{amount}0"
        self.description = description
        self.callback_url = callback_url
        self.authority_token = authority_token

        if settings.ZARINPAL_SANDBOX:
            self.gateway_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
            self.startpay_url = "https://sandbox.zarinpal.com/pg/StartPay/"
            self.verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        else:
            self.gateway_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
            self.startpay_url = "https://www.zarinpal.com/pg/StartPay/"
            self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"

    def verify_payment(self, authority):
        data = {
            "merchant_id": self.merchant_id,
            "amount": self.amount,
            "authority": authority,
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(self.verify_url, json=data, headers=headers)
        res_data = response.json()

        if res_data.get("data") and res_data["data"].get("code") == 100:
            return {
                "success": True,
                "ref_id": res_data["data"]["ref_id"],
                "message": "پرداخت موفق بود ✅",
            }
        else:
            return {
                "success": False,
                "errors": res_data.get("errors", {}),
                "message": "پرداخت تایید نشد ❌",
            }

    @property
    def send_request(self):
        data = {
            "merchant_id": self.merchant_id,
            "amount": self.amount,
            "callback_url": self.callback_url,
            "description": self.description,
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(self.gateway_url, json=data, headers=headers)
        res_data = response.json()

        if res_data.get("data") and res_data["data"].get("code") == 100:
            authority = res_data["data"]["authority"]
            return {
                "success": True,
                "url": self.startpay_url + authority,
                "authority": authority,
            }
        else:
            return {
                "success": False,
                "errors": res_data.get("errors", {}),
            }
