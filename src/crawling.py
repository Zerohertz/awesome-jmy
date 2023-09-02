import json
import os
import time

import requests
from selenium import webdriver


class download_data:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        )
        self.browser = webdriver.Chrome(options)
        self.webhook = os.environ.get("WEBHOOK")

    def main(self):
        # 산업지원 병역일터 접속
        self.browser.get(
            "https://work.mma.go.kr/caisBYIS/search/byjjecgeomsaek.do?eopjong_gbcd_yn=1&eopjong_gbcd=2"
        )
        # Data Download
        self._xpath_click(
            "/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/span/a",
        )
        time.sleep(30)

    def _xpath_click(self, element):
        element = self.browser.find_element("xpath", element)
        element.click()

    def _send_discord_message(self, content):
        data = {"content": content}
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.webhook, data=json.dumps(data), headers=headers)
        return response
