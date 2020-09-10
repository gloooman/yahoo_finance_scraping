import os
from sys import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Driver:

    def __init__(self):
        self.driver = self._setup_driver()

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        self.driver.quit()

    def _setup_driver(self):
        options = Options()
        # options.headless = True
        options.add_argument("window-size=1920,1080")
        if platform == "win32":
            driver = webdriver.Chrome(
                executable_path=f"{os.getcwd()}/driver/chromedriver.exe", chrome_options=options
            )
        else:
            driver = webdriver.Remote("http://chromedriver:4444/wd/hub", DesiredCapabilities.CHROME)
        return driver
