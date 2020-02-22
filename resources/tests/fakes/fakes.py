# coding=utf-8
from future.moves.urllib.parse import quote_plus

from past.builtins import basestring

import requests

import xbmcgui


class FakeListItem(xbmcgui.ListItem):
    def __init__(self, label="", label2="", iconImage="", thumbnailImage="",
                 path="", offscreen=False):
        super(FakeListItem, self).__init__()
        self.setLabel(label)
        self.setLabel2(label2)
        self.setIconImage(iconImage)
        self.setThumbnailImage(thumbnailImage)
        self.setPath(path)
        self.offscreen = offscreen
        self.art = {}
        self.defaultRating = ''
        self.info = {}
        self.rating = {}
        self.streamInfo = {}
        self.property = {}
        self.subtitles = None
        self.uniqueid = {}

    def setLabel(self, label):
        assert isinstance(label, basestring)
        self.label = label

    def setLabel2(self, label):
        self.label2 = label

    def setIconImage(self, iconImage):
        self.iconImage = iconImage

    def setThumbnailImage(self, thumbFilename):
        self.thumbFilename = thumbFilename

    def setArt(self, dictionary):
        allowed_keys = [
            'thumb',
            'poster',
            'banner',
            'fanart',
            'clearart',
            'clearlogo',
            'landscape',
            'icon'
        ]
        for k, v in dictionary.items():
            if k not in allowed_keys:
                raise Exception('Unallowed key for setArt')
            self.art.update({k: v})

    def setIsFolder(self, isFolder):
        assert type(isFolder) == bool
        self.is_folder = isFolder

    def setUniqueIDs(self, values, defaultrating=''):
        allowed_keys = [
            'imdb',
            'tvdb',
            'tmdb',
            'anidb'
        ]
        if defaultrating:
            assert defaultrating in allowed_keys
            self.defaultRating = defaultrating
        for k, v in values.items():
            assert k in allowed_keys
            self.uniqueid.update({k: v})

    def setRating(self, type, rating, votes=0, default=False):
        assert isinstance(type, basestring)
        assert isinstance(rating, (int, float))
        assert isinstance(votes, int)
        assert isinstance(default, bool)
        self.rating.update({'type': type, 'rating': rating, 'votes': votes,
                            'default': default})

    def addSeason(self, number, name=''):
        assert isinstance(number, int)
        assert isinstance(name, basestring)

    def setInfo(self, type, infoLabels):
        self.info.update(infoLabels)

    def addStreamInfo(self, cType, dictionary):
        self.streamInfo.update({cType: dictionary})

    def setProperty(self, key, value):
        self.property.update({key: value})

    def setProperties(self, dictionary):
        self.property.update(dictionary)

    def setPath(self, path):
        assert isinstance(path, (str, bytes))
        self.path = path

    def setSubtitles(self, subtitleFiles):
        assert isinstance(subtitleFiles, list)
        self.subtitles = subtitleFiles

    def getLabel(self):
        return self.label

    def getPath(self):
        return self.path


class FakePlugin(object):
    def __init__(self):
        self.SORT_METHOD_LABEL = 1
        self.SORT_METHOD_LABEL_IGNORE_THE = 2
        self.SORT_METHOD_NONE = 0
        self.SORT_METHOD_TITLE = 9
        self.SORT_METHOD_TITLE_IGNORE_THE = 10
        self.SORT_METHOD_UNSORTED = 40
        self.SORT_METHOD_VIDEO_SORT_TITLE = 26
        self.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE = 27
        self.SORT_METHOD_VIDEO_TITLE = 25
        self.directory = []
        self.resolved = None

    def addDirectoryItem(self, handle, url, listitem, isFolder=False,
                         totalItems=0):
        assert isinstance(url, (str, bytes))
        self.directory.append(
            {'handle': handle, 'url': url, 'listitem': listitem,
             'isFolder': isFolder})

    def addDirectoryItems(self, handle, items, totalItems=0):
        for item in items:
            self.addDirectoryItem(handle, item[0], item[1],
                                  item[2] if len(item) == 3 else False,
                                  totalItems)

    def endOfDirectory(self, handle, succeeded=True, updateListing=False,
                       cacheToDisc=True):
        self.end = True

    def setResolvedUrl(self, handle, succeeded, listitem):
        self.resolved = (handle, succeeded, listitem)

    def addSortMethod(self, handle, sortMethod, label2Mask=''):
        pass

    def setContent(self, handle, content):
        self.content = content


PROGRAM_ATTRS = {
    'captions': True,
    'desc': 'JB Hi-Fi turns up the volume...',
    'duration': 902,
    'episode_title': 'Monday 12/8/2019',
    'rating': 'PG',
    'series': 'The Business',
    'thumb': 'https://foo.com/bar.jpg',
    'time': '2019-08-12 22:15:00',
    'title': 'The Business',
    'video_url': '/video/NC1906H140S00'
}

PROGRAM_URL = '&captions=True&desc=JB+Hi-Fi+turns+up+the+volume...&duration=902&episode_title=Monday+12%2F8%2F2019&rating=PG&series=The+Business&thumb=https%3A%2F%2Ffoo.com%2Fbar.jpg&time=2019-08-12+22%3A15%3A00&title=The+Business&type=Program&video_url=%2Fvideo%2FNC1906H140S00'  # noqa: E501

INFO_DICT = {
    'tvshowtitle': 'Foo',
    'title': 'Return of Foo',
    'duration': 100,
    'year': 2019,
    'aired': '2019-08-13',
    'season': 2,
    'mpaa': 'PG'
}

HN = 'NC1906H140S00'

EXPECTED_AUTH_URL = 'https://api.iview.abc.net.au/auth/hls/sign?ts=1565669764&hn=ZW1939A016S00&d=android-mobile&sig=45eb772f935e4cc35b7799ad99a9fc226aa3fe01bb440dea00388a38e8d13908'  # noqa: E501

EXPECTED_HLS_URL = 'https://iviewhlsvod-vh.akamaihd.net/i/playback/_definst_/_video/zw1/ZW1939A016S00MA1D1_20190731135521_,1500000,1000000,650000,500000,220000,.mp4.csmil/master.m3u8?subtitle_file_pattern=identifier_langcode&subtitle_identifier=ZW1939A016S00MA1D1_5d4e903d4a700&subtitle_location=%2Fplayback%2Fcaptions%2Fprod%2Fzw'  # noqa: E501

EXPECTED_LIVE_HLS_URL = 'https://abc-iview-mediapackagestreams-1.akamaized.net/out/v1/6ee5066dcc704c47a663eaf854562e8e/index.m3u8'  # noqa: E501

EXPECTED_SUB_URL = 'https://iview.abc.net.au/cc/zw/ZW1939A016S00MA1D1_5d4e903d4a700.vtt'  # noqa: E501

AUTH_URL_DEFAULT_TEST = 'https://api.iview.abc.net.au/auth/hls/sign?ts=1565672000&hn=ZW1939A025S00&d=android-mobile&sig=18ddf0fcb0f18572fa00667691d5b2889a6450520e7579f5d5126dad73c53ff5'  # noqa: E501

AUTH_URL_DEFAULT_FEATURE_TEST = 'https://api.iview.abc.net.au/auth/hls/sign?ts=1565672000&hn=ZW0659A001S00&d=android-mobile&sig=210e25f82da7bfd5afac8cf9bed7be80152c573bee6c2f82020b870de9f8569a'  # noqa: E501

AUTH_URL_DEFAULT_LIVE_TEST = 'https://api.iview.abc.net.au/auth/hls/sign?ts=1565672000&hn=NS1413V001S00&d=android-mobile&sig=eca18ee0e559a33dab913c42b9469b41c06a0ef0c8f9a28a77f9e4878b7b41e3'  # noqa: E501

AUTH_COOKIE = 'hdntl=exp=1565676000~acl=%2f*~data=hdntl~hmac=3e3986e98dc74d8d105ca94a1a575bcaf21eaa57b427297a35da94f2bbca3bbf; path=/; domain=;'  # noqa: E501

RESOLVED_URL = '{0}&hdnea={1}|User-Agent={2}&Cookie={3}'.format(EXPECTED_HLS_URL, '{0}', '{1}', quote_plus(AUTH_COOKIE))  # noqa: E501

RESOLVED_LIVE_URL = '{0}?hdnea={1}|User-Agent={2}&Cookie={3}'.format(EXPECTED_LIVE_HLS_URL, '{0}', '{1}', quote_plus(AUTH_COOKIE))  # noqa: E501

EXPECTED_CAPTIONS_URL = 'https://iview.abc.net.au/cc/zw/ZW1939A016S00MA1D1_5d4e903d4a700.vtt'  # noqa: E501

COOKIEJAR = requests.cookies.RequestsCookieJar()
COOKIEJAR.set('Foo', 'Bar', path='Somewhere', domain='foo.org', )

EXPECTED_CATEGORY_TITLES = [
    'ABC',
    'ABC COMEDY',
    'ABC ME',
    'ABC KIDS',
    'ABC NEWS',
    'ABC ARTS',
    'IVIEW PRESENTS',
    'Arts & Culture',
    'Comedy',
    'Documentary',
    'Drama',
    'Education',
    'Lifestyle',
    'News & Current Affairs',
    'Panel & Discussion',
    'Regional Australia',
    'Sport',
    'Live Streams',
    'Search',
    'Settings'
]

EXPECTED_COLLECTION_TITLES = [
    'ABC KIDS: A-Z',
    'ABC KIDS Favourites',
    'ABC KIDS Latest Episodes',
    'ABC KIDS Shows Expiring Soon',
    "Andy's Adventures",
    'Arts and Crafts Time',
    'Fun and Games',
    'Giggle and Hoot: Giggle Party Time!',
    'Giggle and Hoot: Owl Pals',
    'Kiddets: New Episodes',
    'Mandarin Favourites',
    'Peppa Pig: New Episodes',
    'Puggles',
    'Rusty Rivets: New Episodes',
    'Science Week on ABC KIDS',
    'Teach Me How',
    'Winter Wonders'
]

EXPECTED_CATEGORY_PATHS = [
    '/channel/abc1',
    '/channel/abc2',
    '/channel/abc3',
    '/channel/abc4kids',
    '/channel/news',
    '/channel/abcarts',
    '/channel/iview',
    '/category/arts',
    '/category/comedy',
    '/category/docs',
    '/category/drama',
    '/category/education',
    '/category/lifestyle',
    '/category/news',
    '/category/panel',
    '/category/regional',
    '/category/sport',
    'livestreams',
    'search',
    'settings'
]

EXPECTED_SERIES_TITLES = [
    'Aliens Love Underpants And...',
    "Andy's Prehistoric Adventures",
    "Andy's Safari Adventures", "Andy's Secret Hideout",
    'Arthur', 'Arthur (Mandarin)', 'Baby Jake',
    'Bananas In Pyjamas', "Becca's Bunch",
    "Ben And Holly's Little Kingdom",
    'Big Block SingSong', "Big Ted's Big Adventure",
    'Bing', 'Bluey', 'Bob The Builder',
    'Brewster The Rooster', 'Charlie And Lola',
    'Clangers', 'Curious George',
    'Dan Sultan: Nali and Friends',
    "Daniel Tiger's Neighbourhood", 'The Day Henry Met',
    'Dinosaur Train', 'dirtgirlworld', 'Dot.', 'Emma!',
    'Fireman Sam', 'Floogals', 'The Furchester Hotel',
    'Get Grubby TV', 'Get Grubby TV: Shorts',
    'Giggle And Hoot', 'Go Jetters',
    'Grandpa Honeyant Storytime',
    'Guess How Much I Love You', 'Hey Duggee',
    'hoopla doopla!', 'hoopla doopla! (Mandarin)',
    "Humpty's Big Adventure", "I'm A Creepy Crawly",
    'Imagine This', 'In The Night Garden',
    'Jamillah and Aladdin', "Jemima's Big Adventure",
    "Joey's Big Adventure",
    'Justine Clarke: Great Big World',
    'Justine Clarke: I Like To Sing!',
    'Justine Clarke: Pyjama Jam',
    'The Justine Clarke Show!',
    'Justine Clarke: Songs To Make You Smile',
    'Kazoops!', 'Kiddets', 'Kiddets (Mandarin)',
    'Kiri and Lou', 'Lachy!',
    "Lah-Lah's Adventures: Songs",
    'Learning Time With Timmy', "Lily's Driftwood Bay",
    'Little Roy', "Little Ted's Big Adventure",
    'Luo Bao Bei', 'Luo Bao Bei (Mandarin)',
    "Maurice's Big Adventure",
    "Miffy's Adventures Big and Small", 'Mister Maker',
    'Mister Maker Around The World', 'Molly And Mack',
    'Moon and Me', 'Mouk', 'Nella the Princess Knight',
    'Noddy Toyland Detective', 'Numberblocks',
    'Octonauts',
    'Octonauts And Operation Deep Freeze',
    'Octonauts (Mandarin)',
    'Octonauts Special: The Over Under Adventure',
    'Olobob Top', 'Our Acknowledgement of Country',
    'Pablo', 'The Pajanimals', 'Peg + Cat', 'Peppa Pig',
    'Peppa Pig (Mandarin)', 'Pingu In The City',
    'PJ Masks', 'PJ Masks: Songs', 'Play School',
    'Play School: Acknowledgement of Country',
    'Play School Art Time',
    'Play School Celebrity Covers',
    'Play School: Stop, Look, Listen',
    'Play School Story Time',
    'Play School Story Time: Languages',
    'Play School: Through The Windows', 'Playdate',
    'Pocoyo', 'Pocoyo (Mandarin)', 'Rainbow Chicks',
    'Rainbow Chicks (Mandarin)', 'Ready, Jet, Go!',
    'Ready, Jet, Go!: Back To Bortron 7',
    'Ready, Steady, Wiggle!', 'Rita and Crocodile',
    'Rusty Rivets', 'Sally & Possum', 'Sarah And Duck',
    'School Of Roars', 'Scout And The Gumboot Kids',
    'Sesame Street', 'Shaun The Sheep',
    'Sydney Sailboat', 'Teacup Travels', 'Team Rescue',
    'Teeny Tiny Stevies', 'Teletubbies',
    'This Is Scarlett And Isaiah', 'Thomas And Friends',
    'Timmy Time', 'Twirlywoos', 'Waffle The Wonder Dog',
    'Wallykazam!', "We're Going On A Bear Hunt",
    'WildWoods', 'The WotWots'
]

EXPECTED_EPISODE_COUNTS = [
    12, 14, 15, 10, 10, 10, 14, 60, 30, 30, 20, 20, 15, 21, 29, 26, 14, 20, 10,
    10, 14, 25, 30, 9, 29, 26, 30, 30, 20, 19, 37, 40, 15, 24, 23, 29, 20, 21,
    16, 52, 6, 10, 20, 10, 13, 15, 13, 4, 11, 14, 36, 50, 51, 20, 26, 27, 26,
    30, 10, 20, 12, 44, 12, 30, 5, 15, 20, 19, 10, 11, 19, 10, 25, None, 30,
    None, 1, None, 14, 4, 30, 30, 27, 30, 12, 9, 21, None, 20, 31, 20, 24, 5,
    31, 23, 30, 30, 39, 39, 29, None, 30, 10, 14, 60, 15, 29, 28, 30, 12, 52,
    10, 22, 9, 30, 51, 30, 14, 30, 30, 10, None, 12, None
]

EXPECTED_SHOW_TITLES = [
    'Welcome to Sesame Hospital',
    'The Furry Four',
    'Earth Day',
    'Honk if You Love Libraries',
    "Julia's Haircut",
    'Elmo the Engineer',
    'Walking the Dog',
    'Elmo Goes to Chicken School',
    'Fishing X',
    'Mechanics in Space',
    'Rudy Rides the Bus',
    'Sesame Friendship',
    'The Big Pretend Band',
    "Elmo's Happy Little Train",
    'Dinosaur in the Laundromat',
    'Astronaut Elmo',
    'Bath Time For Blanky',
    'Play Time',
    "New Year's Eve Show",
    'Math Magic',
    "Elmo's Factory",
    'So You Think Choreograph',
    'Hey! Sesame Street News',
    'Picture This',
    "When You're a Vet",
    'Episode 9',
    'Episode 8',
    'Episode 7',
    'Episode 6',
    'Episode 5',
]

EXPECTED_SRT_TEXT = (
b"""1
00:00:00,500 --> 00:00:02,000
The Web is always changing

2
00:00:02,500 --> 00:00:04,300
and the way we access it is changing
"""  # noqa: E122
)

EXPECTED_SEARCH_TITLES = [
    'ABC NEWS Live Stream',
    'News Breakfast: Short Cuts',
    'ABC Late News',
    'ABC News Stories',
    'ABC News At Noon',
    'ABC News Mornings',
    'Navigating The News',
    'ABC Late News Weekend',
    'ABC News At Noon Weekend',
    'Pell Appeal - ABC News Special Coverage',
    'Coastal Erosion: An ABC News WA Special',
    'BTN',
    'ABC News WA',
    'ABC News SA',
    'ABC News NT',
    'ABC News VIC',
    'ABC News ACT',
    'ABC News QLD',
    'ABC News NSW',
    'ABC News TAS',
    'BTN Newsbreak'
]

SEARCH_HISTORY_SERIALIZED = '["foo", "bar", "foo bar"]'

EXPECTED_SEARCH_HISTORY = [
    'foo',
    'bar',
    'foo bar'
]
