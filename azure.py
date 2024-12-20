from time import sleep, time
import shutil
import os

from drivercontrol import DriverController

default_lang = "zh_TW"

program_folder = os.path.dirname(__file__)


class AzureTTS(DriverController):
    def __init__(self, download_path: str = "C:\\Users\\user\\Downloads"):
        super().__init__()
        self.download_path = download_path
        self.go("https://azure.microsoft.com/zh-cn/products/cognitive-services/text-to-speech/#features")
        self.wait("#ttstext")
        self.jsfile(os.path.join(program_folder,"filesaver.js"), "utf8")
        self.jsfile(os.path.join(program_folder,"azure_speech_download.js"), "utf8")
        sleep(1)
        self.count: int = 0
        self.lang: str = ""
        self.setlang(default_lang)

    def run(self, text: str, output: str):
        self.count += 1
        sleep(1)
        self.js(f"""(function(){{ttstext.value = {repr(text)};
        let evt=document.createEvent('HTMLEvents');
        evt.initEvent('input', true, true);
        ttstext.dispatchEvent(evt);
        }})();
        """)
        filename = str(time()).replace(".", "_")
        self.js(f"filenamer.textContent = {repr(filename)};")
        sleep(0.5)
        self.js(f"playbtn[1].click()")
        #
        while self.wait("#optiondiv+div").text != "下载完成":
            sleep(0.2)
        out = os.path.join(self.download_path, filename + os.path.splitext(output)[-1])
        while not os.path.isfile(out):
            sleep(0.2)
        shutil.move(out, output)

    def setlang(self, lang: str):
        if self.lang != lang:
            self.lang = lang
            sleep(1)
            self.js(f"""
            languageselect.value = '{lang}';
            let evt=document.createEvent('HTMLEvents');
            evt.initEvent('change', true, true);
            languageselect.dispatchEvent(evt);
            """)
            sleep(1)

    def setspeed(self, speed: float):
        value = int((speed - 1) / 100)
        self.js(f"""
        speed.value = {value};
        let evt=document.createEvent('HTMLEvents');
        evt.initEvent('change', true, true);
        speed.dispatchEvent(evt);
        """)
