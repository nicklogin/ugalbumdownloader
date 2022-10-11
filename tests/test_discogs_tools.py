import unittest

from ug_album_bot.discogs_tools import DiscogsTracklistExtractor
from tests.params import USER_TOKEN


class TestDiscogsTracklistExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.tracklist_extractor = DiscogsTracklistExtractor(USER_TOKEN)

    def test_playlsit_extraction(self) -> None:
        albums = [
            ('Linkin Park', 'Meteora'),
            ('Metallica', 'And Justice For All'),
            ('U2', 'The Joshua Tree')
        ]

        tracklists = [
            self.tracklist_extractor.get_album_tracklist(
                artist, album
            ) for artist, album in albums
        ]

        self.assertEqual(
            tracklists[0],
            [
                'Foreword',
                "Don't Stay",
                'Somewhere I Belong',
                'Lying From You',
                'Hit The Floor',
                'Easier To Run',
                'Faint',
                'Figure.09',
                'Breaking The Habit',
                'From The Inside',
                "Nobody's Listening",
                'Session',
                'Numb'
            ]
        )
        self.assertEqual(
            tracklists[1],
            [
                'Blackened',
                '...And Justice For All',
                'Eye Of The Beholder',
                'One',
                'The Shortest Straw',
                'Harvester Of Sorrow',
                'The Frayed Ends Of Sanity',
                'To Live Is To Die',
                'Dyers Eve'
            ]
        )
        self.assertEqual(
            tracklists[2],
            [
                'Where The Streets Have No Name',
                "I Still Haven't Found What I'm Looking For",
                'With Or Without You',
                'Bullet The Blue Sky',
                'Running To Stand Still',
                'Red Hill Mining Town',
                "In God's Country",
                'Trip Through Your Wires',
                'One Tree Hill',
                'Exit',
                'Mothers Of The Disappeared'
            ]
        )
