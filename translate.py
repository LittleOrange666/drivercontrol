from time import sleep
from drivercontrol import DriverController, Keys
from selenium.common.exceptions import ElementClickInterceptedException


class Translater(DriverController):
    def __init__(self, source_lang: str, target_lang: str):
        super(Translater, self).__init__()
        self.go(f"https://translate.google.com.tw/?sl={source_lang}&tl={target_lang}&op=translate")
        sleep(2)
        
    def changelang(self, source_lang: str, target_lang: str):
        delete_ele = self.find("button[aria-label='清除原文內容']")
        if delete_ele.is_displayed():
            delete_ele.click()
        self.go(f"https://translate.google.com.tw/?sl={source_lang}&tl={target_lang}&op=translate")
        sleep(2)

    def translate(self, content: str) -> str:
        delete_ele = self.find("button[aria-label='清除原文內容']")
        if delete_ele.is_displayed():
            try:
                delete_ele.click()
            except ElementClickInterceptedException:
                sleep(3)
                try:
                    delete_ele.click()
                except ElementClickInterceptedException:
                    pass
        input_ele = self.find(".er8xn")
        input_ele.send_keys(Keys.NULL)
        input_ele.send_keys(content)
        sleep(0.5)
        wait_ele = self.find(".xsPT1b")
        while wait_ele and wait_ele.is_displayed():
            sleep(0.5)
        output_ele = self.wait(".HwtZe")
        return output_ele.text