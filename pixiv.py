import json
import os
import re
import shutil
from threading import Thread
from time import sleep

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from termcolor import colored

from drivercontrol import find, wait_all, find_all, initcolorama, DriverController


class Pixiv(DriverController):
    class filemover(Thread):
        __slots__ = ("source", "target")

        def __init__(self, source: str, target: str):
            super().__init__()
            self.source: str = source
            self.target: str = target

        def run(self) -> None:
            while not os.path.isfile(self.source):
                sleep(1)
            sleep(10)
            for _ in range(10):
                try:
                    shutil.move(self.source, self.target)
                except PermissionError:
                    sleep(5)
                else:
                    print(f"moved {self.source} to {self.target}")
                    return
            print(f"can't moved {self.source} to {self.target}")

    class Stat:
        __slots__ = ("start", "end", "nextend", "filename")

        def __init__(self, filename):
            self.filename = filename
            self.start = None
            self.end = None
            self.nextend = None
            if os.path.isfile(filename):
                with open(filename) as f:
                    dat = json.load(f)
                    if "start" in dat:
                        self.start = dat["start"]
                    if "end" in dat:
                        self.end = dat["end"]
                    if "nextstart" in dat:
                        self.nextend = dat["nextstart"]

        def complete(self) -> None:
            self.end = self.nextend
            self.start = None
            self.nextend = None

        def update(self, link: str) -> None:
            if self.nextend is None:
                self.nextend = link
            self.start = link

        def save(self) -> None:
            with open(self.filename, "w") as f:
                dat = {"start": self.start, "end": self.end, "nextend": self.nextend}
                json.dump(dat, f, indent=2, separators=(", ", ": "))
                print(colored("stat saved", "green"))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.save()

        def __str__(self):
            return f"<{__name__}.Stat filename={self.filename} start={self.start} end={self.end} nextend={self.nextend}>"

    def __init__(self, targetfolder: str, pid: str):
        super(Pixiv, self).__init__()
        self.targetfolder = targetfolder
        self.pid = pid
        self.stat: Pixiv.Stat = Pixiv.Stat(os.path.join(targetfolder, "stat.json"))
        initcolorama()

    def init(self, email: str, password: str):
        self.go('https://www.pixiv.net/login.php?ref=wwwtop_accounts_index')
        form = self.wait_all("form")[0]
        inputs = find_all(form, "input")
        inputs[-2].send_keys(email)
        inputs[-1].send_keys(password)
        input("請完成登入後按Enter...")
        sleep(1)

    def dodownload(self, link: str, name: str):
        # img.click()
        filename = f"{name}_{link[link.rfind('/') + 1:]}"
        filename = re.sub('[/\\"\\\'*;?\\[\\]()~!${}>#@&| \\t\\n\\\\]', "", filename)
        full_filename = os.path.abspath(os.path.join(self.targetfolder, filename))
        print(f"try to download {filename} from {link}")
        the_script = f"""
(function () {{
    var img = new Image();
    img.onload = function() {{
        var canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        var base64 = canvas.toDataURL();
        var a = document.createElement('a');
        a.href = base64;
        a.download = '{filename}';
        a.click();
        window.setTimeout(window.close,5000);
    }}
    img.src = '{link}';
    img.setAttribute('crossOrigin', 'Anonymous');
}})();
"""
        self.newtab(link)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(0.5)
        self.js(the_script)
        Pixiv.filemover(os.path.join("C:\\Users\\USER\\Downloads", filename), full_filename).start()
        print(f"downloaded {filename}")

    def download(self, target: str):
        self.go(target)
        print(f"downloading {target}")
        figcaption: WebElement = self.wait("figcaption")
        h1: None | WebElement = self.find("figcaption h1")
        name: str = "無題" if h1 is None else h1.text
        area: WebElement = self.wait("#root main section figure>div")
        counter: WebElement = find(area, "span")
        countertext: str = "1/1" if counter is None else counter.text
        count: int = int(countertext[countertext.find("/") + 1:])
        img: WebElement = find(area, "a")
        if img is not None:
            if count > 1:
                img.click()
                sleep(1)
                area = self.wait("#root main section figure>div")
                imgs: list[WebElement] = wait_all(area, "a")
                for link in [theimg.get_attribute("href") for theimg in imgs]:
                    self.dodownload(link, name)
            else:
                self.dodownload(img.get_attribute("href"), name)
            self.driver.switch_to.window(self.driver.window_handles[0])
        else:
            print(f"{target} can't be downloaded")

    def run(self):
        os.system("color")
        startlink = self.stat.start
        endlink = self.stat.end
        with self.stat:
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.go(f"https://www.pixiv.net/users/{self.pid}/bookmarks/artworks?p=1")
            sleep(1)
            page = 1
            nxturl = ""
            oldlink = self.geturl()
            running = startlink is None
            all_links: list[str] = []
            while page == 1 or nxturl != oldlink:
                if page > 1:
                    self.go(nxturl)
                    oldlink = nxturl
                print(f"reading page {page}")
                if running and page == 1:
                    print(colored("started downloading", "green"))
                ul: WebElement = self.wait("#root section ul")
                nxtbtn: WebElement = self.find_all("#root nav a")[-1]
                nxturl = nxtbtn.get_attribute("href")
                els: list[WebElement] = ul.find_elements(By.CSS_SELECTOR, "ul a")
                links = [s for s in (e.get_attribute("href") for e in els) if "artworks" in s]
                truelinks = []
                for l in links:
                    if (len(truelinks) == 0 or truelinks[-1] != l) and l not in all_links:
                        truelinks.append(l)
                all_links.extend(truelinks)
                for link in truelinks:
                    if endlink is not None and link == endlink:
                        running = False
                        self.stat.complete()
                        print(colored("ended downloading", "green"))
                    if not running:
                        if link == startlink:
                            running = True
                            print(colored("started downloading", "green"))
                        else:
                            continue
                    self.stat.update(link)
                    try:
                        self.download(link)
                    except WebDriverException:
                        sleep(10)
                        self.download(link)
                page += 1
            with open("data.json", "w") as datafile:
                json.dump({"artworks": all_links}, datafile, indent=2, separators=(", ", ": "))
            print(colored("run complete", "green"))
