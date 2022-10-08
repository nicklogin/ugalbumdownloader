import os
import requests

from typing import List, Literal, Tuple
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


class UGTrackListExtractor:
    def __init__(
        self,
        order: Literal["rating", "votes"] = "rating",
        timeout: float = 0.5
    ):
        self.link = "https://www.ultimate-guitar.com/search.php?title={}+{}&type=500"
        self.order = order
        self.timeout = timeout

    def get_best_tab_link(
        self,
        artist: str,
        track: str
    ) -> Tuple[str, int, int]:
        # в общем, это тоже надо переписать на Selenium'е,
        # а то присылается один JS в ответ :(
        link = self.link.format(
            artist.replace(' ', '+'),
            track.replace(' ', '+')
        )
        parsed_search_page = BeautifulSoup(
            requests.get(link).text,
            "html.parser"
        )
        with open("test_file.html", 'w') as outp:
            outp.write(str(parsed_search_page))
        tab_divs = parsed_search_page.find_all("div", class_="LQUZJ")

        best_tab_link = (None, 0, 0)

        for tab_div in tab_divs:
            tab_type_div = tab_div.find("div", class_="lIKMM PdXKy")
            if tab_type_div.text == "guitar pro":
                tab_rating = str(
                    tab_div.find("div", class_="ecTgD")
                ).count("kd3Q7")
                tab_votes = int(tab_div.find("div", class_="djFV9").text)
                tab_link = tab_div.find(
                    "a",
                    class_="aPPf7 HT3w5 lBssT"
                )["href"]
                if (
                    self.order == "rating" and tab_rating > best_tab_link[1]
                ) or (
                    self.order == "votes" and tab_votes > best_tab_link[2]
                ):
                    best_tab_link = (tab_link, tab_rating, tab_votes)

        return best_tab_link

    def get_tab_links(
        self, artist: str, tracklist: str
    ) -> List[Tuple[str, int, int]]:
        tab_links = []
        for track in tracklist:
            tab_links.append(self.get_best_tab_link(artist, track))
        return tab_links


class UGDownloader:
    def __init__(
        self,
        username: str,
        password: str,
        directory: str,
        geckopath: str = "geckodriver.exe",
        timeout: float = 0.5
    ):
        self.username = username
        self.password = password
        self.directory = os.path.abspath(directory)
        self.geckopath = geckopath
        self.timeout = timeout

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

        self.driver.close()
