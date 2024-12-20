from time import sleep
from drivercontrol import DriverController, find, find_all, By, WebElement, Keys, ActionChains


class Messenge:
    __slots__ = ("exist", "element", "context", "accessory", "context_text", "sender")

    def __init__(self, element: WebElement):
        self.exist = True
        self.element: WebElement = element
        self.context: WebElement | None = find(element, '*[class^="markup"]')
        #self.accessory: WebElement | None = find(element, '*[class^="grid"]')
        self.context_text: str = "" if self.context is None else self.context.text
        sender = find(element, '*[class^="headerText"] *[class^="username"]')
        self.sender: str = "unknown" if sender is None else sender.text

    def __bool__(self):
        return self.exist

    def get(self, target, by: str = By.CSS_SELECTOR) -> WebElement | None:
        return find(self.element, target, by)

    #def getaccessories(self) -> list[WebElement]:
    #    if self.accessory is None:
    #        return []
    #    return find_all(self.accessory, "div", By.TAG_NAME)

    def getreactions(self) -> list[WebElement]:
        return find_all(self.element, "*[class^='reactionInner_'] img")


class Discord(DriverController):

    def __init__(self, email: str, password: str, serverid: str, channalid: str, headless=False):
        super(Discord, self).__init__(headless)
        self.go('https://discord.com/channels/' + serverid + '/' + channalid)
        sleep(1)
        noapp: WebElement = self.find("/html/body/div[1]/div[2]/div/div[1]/div/div/div/section/div/button[2]", By.XPATH)
        if noapp is not None:
            noapp.click()
        sleep(3)
        form: WebElement = self.wait("form",By.CSS_SELECTOR)
        find(form, "input[name='email']").send_keys(email)
        find(form, "input[name='password']").send_keys(password)
        find(form, "button[type='submit']").click()
        self.serverid = serverid
        self.channalid = channalid

    def send(self, msg: str) -> bool:
        msger = self.wait("div[role='textbox']",By.CSS_SELECTOR)
        if msger is None:
            return False
        if msg.endswith("\n"):
            msg = msg[:-1]
        msger.send_keys(Keys.NULL)
        for s in msg.split("\n")[:-1]:
            msger.send_keys(s)
            ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        msger.send_keys(msg.split("\n")[-1])
        msger.send_keys("\n")
        return True

    def getmsgs(self, cnt: int = 1):
        # msglist = self.wait('.scrollerInner-2PPAp2')
        msgs = self.wait_all("li", By.TAG_NAME)
        return [Messenge(msg) for msg in msgs[-min(cnt,len(msgs)):]]

    def getmsgs_plain(self, cnt: int = 1):
        # msglist = self.wait('.scrollerInner-2PPAp2')
        msgs = self.wait_all("li", By.TAG_NAME)
        return [msg.text for msg in msgs[-min(cnt,len(msgs)):]]

    def moveto(self, serverid: str, channalid: str | None = None):
        if channalid is None:
            channalid = serverid
            serverid = self.serverid
        self.go('https://discord.com/channels/' + serverid + '/' + channalid)
        self.serverid = serverid
        self.channalid = channalid
        sleep(1)
