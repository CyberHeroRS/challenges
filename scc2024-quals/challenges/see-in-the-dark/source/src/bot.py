import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager


def visit(theme, url):
    service = Service(executable_path=GeckoDriverManager().install())
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.binary_location = "/usr/bin/firefox"
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("http://localhost:2000")
    driver.add_cookie({"name": "theme", "value": theme})
    driver.add_cookie(
        {
            "name": "flag",
            "value": os.environ["FLAG"],
            "httpOnly": True,
        }
    )
    driver.get(url)
    time.sleep(1)
    driver.quit()
