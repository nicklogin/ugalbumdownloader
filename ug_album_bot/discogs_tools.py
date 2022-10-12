from discogs_client import Client

from typing import List


class DiscogsTracklistExtractor:
    def __init__(self,  user_token: str):
        self.token = user_token

    def get_album_tracklist(self, artist: str, album: str) -> List[str]:
        d = Client('ExampleApplication/0.1', user_token=self.token)
        results = d.search(album, artist=artist, type="release")
        if results:
            release = results[0]
            output = [track.title for track in release.tracklist]
        else:
            output = []
        del d
        return output
