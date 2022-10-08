import os

from typing import Literal, Tuple
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class UGDownloader:
    def __init__(
        self,
        username: str,
        password: str,
        directory: str,
        geckopath: str = "geckodriver.exe",
        timeout: float = 0.5,
        order: Literal["rating", "votes"] = "rating"
    ):
        self.username = username
        self.password = password
        self.directory = os.path.abspath(directory)
        self.geckopath = geckopath
        self.timeout = timeout
        self.link = "https://www.ultimate-guitar.com/search.php?title={}+{}&type=500"
        self.order = order

        self.init_driver()

    def init_driver(self) -> None:
        options = Options()
        options.headless = True

        options.set_preference("browser.download.folderList", 2)
        options.set_preference(
            "browser.download.manager.showWhenStarting",
            False
        )
        options.set_preference("browser.download.dir", self.directory)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/octet-stream"
        )

        self.driver = webdriver.Firefox(
            options=options,
            executable_path=self.geckopath
        )

    def close_driver(self) -> None:
        self.driver.close()

    def login(self) -> None:
        # click login button
        self.driver.get("https://www.ultimate-guitar.com/")
        login_btn = self.driver.find_element(
            by="xpath",
            value='//button[@class="rPQkl yDkT4 IxFbd exTWY lTEpj qOnLe QlmHX"]'
        )
        login_btn.click()

        # wait for JS to work
        sleep(self.timeout)

        # send login data
        form = self.driver.find_element(
            by="xpath",
            value='//form[@class=""]'
        )
        form.find_element(by="name", value="username").send_keys(self.username)
        form.find_element(by="name", value="password").send_keys(self.password)
        form.submit()

        sleep(self.timeout)

    def download_tab_by_url(self, url: str) -> None:
        self.login()

        self.driver.get(url)
        form = self.driver.find_element(
            by="xpath",
            value='//form[@action="https://tabs.ultimate-guitar.com/tab/download"]'
        )
        form.submit()
        sleep(self.timeout)

        self.close_driver()

    def get_best_tab_link(
        self,
        artist: str,
        track: str
    ) -> Tuple[str, int, int]:
        link = self.link.format(
            artist.replace(' ', '+'),
            track.replace(' ', '+')
        )
        self.driver.get(link)

        tab_divs = self.driver.find_elements(
            by="xpath",
            value='//div[@class="LQUZJ"]'
        )
        best_tab_link = (None, 0, 0)
        print(len(tab_divs))

        for idx, tab_div in enumerate(tab_divs):
            print(tab_div.tag_name)
            tab_div.screenshot(f"tab_div_{idx}.png")
            tab_type_div = tab_div.find_element(
                by="xpath",
                value='.//div[@class="lIKMM PdXKy"]'
            )
            print(tab_type_div.text)
            tab_type_div.screenshot(f"tab_type_div_{idx}.png")
            if tab_type_div.text.lower().strip() == "guitar pro":
                tab_rating = len(
                    tab_div.find_elements(
                        by='xpath',
                        value='.//div[@class="kd3Q7"]'
                    )
                )
                tab_votes = int(
                    tab_div.find_element(
                        by='xpath',
                        value='.//div[@class="djFV9"]'
                    ).text
                )
                tab_link = tab_div.find_element(
                    by='xpath',
                    value='a[@class="aPPf7 HT3w5 lBssT"]'
                ).href

                if (
                    self.order == "rating" and tab_rating > best_tab_link[1]
                ) or (
                    self.order == "votes" and tab_votes > best_tab_link[2]
                ):
                    best_tab_link = (tab_link, tab_rating, tab_votes)

        return best_tab_link

    def download_tab_by_name(
        self,
        artist: str,
        track: str
    ):
        tab_link, tab_rating, tab_votes = self.get_best_tab_link(
            artist,
            track
        )
        self.download_tab_by_url(tab_link)
