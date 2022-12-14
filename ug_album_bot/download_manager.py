import os
import json
import zipfile

from typing import List, Literal

from ug_album_bot.discogs_tools import DiscogsTracklistExtractor
from ug_album_bot.ug_tools import UGDownloader
from ug_album_bot.exceptions import NoTabsFoundException


class AlbumDownloadManager:
    def __init__(
        self,
        dg_user_token: str,
        ug_username: str,
        ug_password: str,
        download_dir: str,
        timeout: float,
        geckopath: str = "geckodriver.exe",
        order: Literal["rating", "votes", "rank_sum"] = "rating"
    ):
        self.dg_user_token = dg_user_token
        self.ug_username = ug_username
        self.ug_password = ug_password
        self.download_dir = download_dir
        self.timeout = timeout
        self.geckopath = geckopath
        self.order = order

    def download_tracklist_tabs(
        self,
        artist: str,
        tracklist: List[str]
    ) -> None:
        # TODO: optimize with multiprocessing
        downloader = UGDownloader(
            username=self.ug_username,
            password=self.ug_password,
            directory=self.album_download_dir,
            geckopath=self.geckopath,
            timeout=self.timeout,
            order=self.order
        )
        downloader.login()
        for track_id, track in enumerate(tracklist):
            print(track)
            try:
                tab_link,\
                    tab_rating,\
                    tab_votes = downloader.download_tab_by_name(
                        artist, track
                    )
                self.album_info.append(
                    {
                        "track_number": track_id,
                        "track": track,
                        "album": self.album,
                        "artist": artist,
                        "link": tab_link,
                        "rating": tab_rating,
                        "votes": tab_votes
                    }
                )
            except NoTabsFoundException:
                pass

            # find track in folder and rename it to include ID
            pass

        downloader.close_driver()
        del downloader

    def save_album_info(self) -> None:
        with open(os.path.join(
            self.album_download_dir,
            "info.json"
        ), "w", encoding="utf-8") as inp:
            json.dump(
                self.album_info,
                inp,
                ensure_ascii=False,
                indent=4
            )

    def zip_all(self) -> None:
        fulldname = self.album_download_dir
        fullzipfname = f"{self.artist} - {self.album}.zip"

        # Taken from https://stackoverflow.com/a/65990560
        with zipfile.ZipFile(fullzipfname, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(fulldname):
                for _dir in dirs:
                    zipf.write(
                        os.path.join(root, _dir),
                        os.path.relpath(
                            os.path.join(root, _dir),
                            os.path.join(fulldname)
                        )
                    )
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        os.path.relpath(
                            os.path.join(root, file),
                            os.path.join(fulldname)
                        )
                    )
        for root, dirs, files in os.walk(fulldname, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for _dir in dirs:
                os.rmdir(os.path.join(root, _dir))
        os.rmdir(fulldname)

    def download_album_tabs(
        self,
        artist: str,
        album: str,
        zip_folder: bool = False
    ) -> None:
        self.album_download_dir = os.path.join(
            self.download_dir,
            f"{artist} - {album}"
        )
        self.album_info = []
        self.album = album
        self.artist = artist
        os.mkdir(self.album_download_dir)

        tracklist = DiscogsTracklistExtractor(
            self.dg_user_token
        ).get_album_tracklist(artist, album)
        self.download_tracklist_tabs(artist, tracklist)
        self.save_album_info()
        if zip_folder:
            self.zip_all()


if __name__ == '__main__':
    import tests.params as params
    import typer
    m = AlbumDownloadManager(
        dg_user_token=params.USER_TOKEN,
        ug_username=params.USERNAME,
        ug_password=params.PASSWORD,
        download_dir=params.DOWNLOAD_DIR,
        timeout=params.TIMEOUT,
        order=params.ORDER
    )
    typer.run(m.download_album_tabs)
