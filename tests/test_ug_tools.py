import unittest
import os

from ug_album_bot.ug_tools import UGDownloader
from tests.params import USERNAME, PASSWORD, DOWNLOAD_DIR, TIMEOUT, ORDER


# class TestUGTracklistExtractor(unittest.TestCase):
#     def setUp(self) -> None:
#         self.tracklist_extractor = UGTrackListExtractor()

#     def test_get_tab_links(self):
#         artist = "Linkin Park"
#         tracklist = [
#             'Foreword',
#             "Don't Stay",
#             'Somewhere I Belong',
#             'Lying From You',
#             'Hit The Floor',
#             'Easier To Run',
#             'Faint',
#             'Figure.09',
#             'Breaking The Habit',
#             'From The Inside',
#             "Nobody's Listening",
#             'Session',
#             'Numb'
#         ]

#         tab_links = self.tracklist_extractor.get_tab_links(artist, tracklist)
#         for tab_link, rating, votes in tab_links:
#             self.assertIsNotNone(tab_link)
#             self.assertGreater(rating, 0)
#             self.assertGreater(votes, 0)


class TestUGDownloader(unittest.TestCase):
    def setUp(self) -> None:
        if not os.path.exists(DOWNLOAD_DIR):
            os.mkdir(DOWNLOAD_DIR)
        self.download_dir = os.path.abspath(DOWNLOAD_DIR)

        self.tab_downloader = UGDownloader(
            USERNAME,
            PASSWORD,
            self.download_dir,
            timeout=TIMEOUT,
            order=ORDER
        )

    def tearDown(self) -> None:
        self.tab_downloader.close_driver()

    def test_login(self) -> None:
        self.tab_downloader.login()
        self.assertNotIn(
            "Incorrect password",
            self.tab_downloader.driver.page_source
        )

    def test_download_tab_by_url(self) -> None:
        url = "https://tabs.ultimate-guitar.com/tab/linkin-park/faint-guitar-pro-224026"
        filename = "Linkin Park - Faint (ver 2).gp3"
        self.tab_downloader.login()
        self.tab_downloader.download_tab_by_url(url)
        filepath = os.path.join(
            self.download_dir,
            filename
        )
        self.assertTrue(
            os.path.exists(filepath)
        )
        os.remove(filepath)

    def test_get_best_tab_link(self) -> None:
        artist = "Linkin Park"
        track = "Faint"
        url = "https://tabs.ultimate-guitar.com/tab/linkin-park/faint-guitar-pro-224026"

        tab_link, tab_rating, tab_votes = self.tab_downloader.get_best_tab_link(
            artist, track
        )
        print(tab_link)

        self.assertTrue(tab_link == url)

