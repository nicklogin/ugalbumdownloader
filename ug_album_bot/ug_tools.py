import os

import ug_album_bot.div_classes as div_classes
from ug_album_bot.exceptions import CannotSreenshotException
from ug_album_bot.exceptions import NoTabsFoundException
from ug_album_bot.exceptions import CannotLoginException

from typing import Literal, Tuple
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


class UGDownloader:
    def __init__(
        self,
        username: str,
        password: str,
        directory: str,
        geckopath: str = "geckodriver.exe",
        timeout: float = 0.5,
        order: Literal["rating", "votes", "rank_sum"] = "rating"
    ):
        # print(f"The order is {order}")
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

    def screenshot(self, filename: str) -> None:
        if self.driver.save_screenshot(
            os.path.join(
                os.getcwd(),
                filename
            )
        ):
            return
        else:
            raise CannotSreenshotException("Unable to screenshot")

    def login(self) -> None:
        # click login button
        self.driver.get("https://www.ultimate-guitar.com/")
        login_btn = self.driver.find_element(
            by="xpath",
            value=f'//button[@class="{div_classes.LOGIN_BUTTON_CLASS}"]'
        )
        login_btn.click()

        # wait for JS to work
        sleep(self.timeout)

        # send login data
        form = self.driver.find_element(
            by="xpath",
            value=f'//form[@class="{div_classes.LOGIN_FORM_CLASS}"]'
        )
        form.find_element(by="name", value="username").send_keys(self.username)
        form.find_element(by="name", value="password").send_keys(self.password)
        form.submit()

        sleep(self.timeout)

        # check that login succeeded
        if "Incorrect password" in self.driver.page_source:
            raise CannotLoginException(
                "Unable to login to ultimate-guitar.com - Please try again later"
            )

    def download_tab_by_url(self, url: str) -> None:
        self.login()

        self.driver.get(url)
        sleep(self.timeout)
        # self.screenshot("download_page.png")

        form = self.driver.find_element(
            by="xpath",
            value='//form[@action="https://tabs.ultimate-guitar.com/tab/download"]'
        )
        # form.screenshot("download_form.png")
        form.submit()
        sleep(self.timeout)

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
            value=f'//div[@class="{div_classes.TAB_DIV_CLASS}"]'
        )
        best_tab_link = (None, 0, 0)
        tab_links_to_weigh = []

        # self.screenshot("search_results.png")

        # print(len(tab_divs))

        if len(tab_divs):
            for idx, tab_div in enumerate(tab_divs):
                # print(tab_div.tag_name)
                # tab_div.screenshot(f"tab_div_{idx}.png")
                tab_type_div = tab_div.find_element(
                    by="xpath",
                    value=f'.//div[@class="{div_classes.TAB_TYPE_CLASS}"]'
                )
                # print(tab_type_div.text)
                # tab_type_div.screenshot(f"tab_type_div_{idx}.png")
                if tab_type_div.text.lower().strip() == "guitar pro":
                    # count coloured stars
                    tab_rating = len(
                        tab_div.find_elements(
                            by='xpath',
                            value=f'.//span[@class="{div_classes.STAR_CLASS}"]'
                        )
                    )
                    # count half-coloured stars
                    tab_rating += len(
                        tab_div.find_elements(
                            by='xpath',
                            value=f'.//span[@class="{div_classes.HALF_STAR_CLASS}"]'
                        )
                    )

                    try:
                        tab_votes = int(
                            tab_div.find_element(
                                by='xpath',
                                value=f'.//div[@class="{div_classes.TAB_VOTES_CLASS}"]'
                            ).text.replace(",", "")
                        )
                    except NoSuchElementException:
                        # if there are no votes on selected tab
                        tab_votes = 0

                    tab_link = tab_div.find_element(
                        by='xpath',
                        value=f'.//a[@class="{div_classes.TAB_LINK_CLASS}"]'
                    ).get_attribute("href")
                    # print(tab_link, tab_votes, tab_rating)

                    if (
                        self.order == "rating" and tab_rating > best_tab_link[1]
                    ) or (
                        self.order == "votes" and tab_votes > best_tab_link[2]
                    ):
                        best_tab_link = (tab_link, tab_rating, tab_votes)
                    else:
                        tab_links_to_weigh.append(
                            (tab_link, tab_rating, tab_votes)
                        )
            if self.order == "rank_sum":
                rating_sort = sorted(
                    [i for i in range(len(tab_links_to_weigh))],
                    key=lambda x: tab_links_to_weigh[x][2],
                    reverse=True
                )
                rating_ranks = [
                    rating_sort.index(i) for i in range(len(tab_links_to_weigh))
                ]

                votes_sort = sorted(
                    [i for i in range(len(tab_links_to_weigh))],
                    key=lambda x: tab_links_to_weigh[x][2],
                    reverse=True
                )
                votes_ranks = [
                    votes_sort.index(i) for i in range(len(tab_links_to_weigh))
                ]

                rank_sums = [a + b for a, b in zip(rating_ranks, votes_ranks)]
                best_link_id = min(
                    [i for i in range(len(rank_sums))],
                    key=rank_sums.__getitem__
                )
                best_tab_link = tab_links_to_weigh[best_link_id]
        else:
            raise NoTabsFoundException(
                f"No tabs were found for {artist} - {track}"
            )

        # print(best_tab_link)
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
        return tab_link, tab_rating, tab_votes
