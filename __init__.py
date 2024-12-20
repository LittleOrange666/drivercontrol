from selenium import webdriver
from time import sleep
from typing import Iterable

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import colorama

coloramainited = False


def initcolorama():
    global coloramainited
    if not coloramainited:
        coloramainited = True
        colorama.init()


def find(source: WebElement | WebDriver, target, by: str = By.CSS_SELECTOR) -> None | WebElement:
    while True:
        try:
            r = source.find_element(by, target)
        except NoSuchElementException:
            return None
        except StaleElementReferenceException:
            return None
        else:
            break
    return r


def find_all(source, target, by: str = By.CSS_SELECTOR) -> list[WebElement]:
    while True:
        try:
            r = source.find_elements(by, target)
        except NoSuchElementException:
            return []
        except StaleElementReferenceException:
            return []
        else:
            break
    return r


def wait(source: WebElement | WebDriver, target, by: str = By.CSS_SELECTOR) -> None | WebElement:
    trycount = 0
    while True:
        try:
            r = source.find_element(by, target)
        except NoSuchElementException:
            trycount += 1
            if trycount > 200:
                return None
            sleep(1)
        except StaleElementReferenceException:
            return None
        else:
            break
    return r


def wait_all(source, target, by: str = By.CSS_SELECTOR) -> list[WebElement]:
    trycount = 0
    while True:
        try:
            r = source.find_elements(by, target)
        except NoSuchElementException:
            trycount += 1
            if trycount > 200:
                return []
            sleep(1)
        except StaleElementReferenceException:
            return []
        else:
            break
    return r


class DriverController:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.initdriver()

    def initdriver(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service = Service(executable_path = ChromeDriverManager().install().replace("THIRD_PARTY_NOTICES.chromedriver","chromedriver.exe")), options=options)
        self.driver.set_page_load_timeout(600)

    def go(self, url: str):
        get_count = 10
        while get_count:
            try:
                self.driver.get(url)
            except:
                sleep(1)
                get_count -= 1
            else:
                return

    def geturl(self):
        return self.driver.current_url

    def js(self, script: str):
        self.driver.execute_script(script)

    def jsfile(self, scriptfilename: str, encode: str | None = None):
        with open(scriptfilename, encoding=encode) as f:
            self.driver.execute_script(f.read())

    def newtab(self, link: str):
        self.js(f"window.open('{link}','_blank');")

    def tryfind(self, targets: Iterable, by: str = By.CSS_SELECTOR) -> None | WebElement:
        r = None
        for target in targets:
            r = self.find(target, by)
            if r is not None:
                return r
        return r

    def find(self, target, by: str = By.CSS_SELECTOR) -> None | WebElement:
        return find(self.driver, target, by)

    def find_all(self, target, by: str = By.CSS_SELECTOR) -> list[WebElement]:
        return find_all(self.driver, target, by)

    def wait(self, target, by: str = By.CSS_SELECTOR) -> None | WebElement:
        return wait(self.driver, target, by)

    def wait_all(self, target, by: str = By.CSS_SELECTOR) -> list[WebElement]:
        return wait_all(self.driver, target, by)
    
    def quit(self):
        self.driver.quit()


class EdgeDriverController(DriverController):
    def __init__(self):
        super().__init__()

    def initdriver(self):
        options = webdriver.EdgeOptions()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Edge(service = Service(executable_path = EdgeChromiumDriverManager().install(), options=options))
        self.driver.set_page_load_timeout(600)

