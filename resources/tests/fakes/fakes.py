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

PROGRAM_URL = '&captions=True&desc=JB+Hi-Fi+turns+up+the+volume...&duration=902&episode_title=Monday+12%2F8%2F2019&rating=PG&series=The+Business&thumb=https%3A%2F%2Ffoo.com%2Fbar.jpg&time=2019-08-12+22%3A15%3A00&title=The+Business&type=Program&video_url=%2Fvideo%2FNC1906H140S00&addon_version=1.0.0'  # noqa: E501

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

EXPECTED_MULTISERIES_TITLES = [
    'Gardening Australia (S31E04): Series 31 Episode 4',
    'Gardening Australia (S31E03): Series 31 Episode 3',
    'Gardening Australia (S31E02): Series 31 Episode 2',
    'Gardening Australia (S31E01): Series 31 Episode 1',
    'Series 28',
    'Series 29',
    'Series 30'
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
    'Aliens Love Underpants And... (12)',
    "Andy's Prehistoric Adventures (14)",
    "Andy's Safari Adventures (15)", "Andy's Secret Hideout (10)",
    'Arthur (10)', 'Arthur (Mandarin) (10)', 'Baby Jake (14)',
    'Bananas In Pyjamas (60)', "Becca's Bunch (30)",
    "Ben And Holly's Little Kingdom (30)",
    'Big Block SingSong (20)', "Big Ted's Big Adventure (20)",
    'Bing (15)', 'Bluey (21)', 'Bob The Builder (29)',
    'Brewster The Rooster (26)', 'Charlie And Lola (14)',
    'Clangers (20)', 'Curious George (10)',
    'Dan Sultan: Nali and Friends (10)',
    "Daniel Tiger's Neighbourhood (14)", 'The Day Henry Met (25)',
    'Dinosaur Train (30)', 'dirtgirlworld (9)', 'Dot. (29)', 'Emma! (26)',
    'Fireman Sam (30)', 'Floogals (30)', 'The Furchester Hotel (20)',
    'Get Grubby TV (19)', 'Get Grubby TV: Shorts (37)',
    'Giggle And Hoot (40)', 'Go Jetters (15)',
    'Grandpa Honeyant Storytime (24)',
    'Guess How Much I Love You (23)', 'Hey Duggee (29)',
    'hoopla doopla! (20)', 'hoopla doopla! (Mandarin) (21)',
    "Humpty's Big Adventure (16)", "I'm A Creepy Crawly (52)",
    'Imagine This (6)', 'In The Night Garden (10)',
    'Jamillah and Aladdin (20)', "Jemima's Big Adventure (10)",
    "Joey's Big Adventure (13)",
    'Justine Clarke: Great Big World (15)',
    'Justine Clarke: I Like To Sing! (13)',
    'Justine Clarke: Pyjama Jam (4)',
    'The Justine Clarke Show! (11)',
    'Justine Clarke: Songs To Make You Smile (14)',
    'Kazoops! (36)', 'Kiddets (50)', 'Kiddets (Mandarin) (51)',
    'Kiri and Lou (20)', 'Lachy! (26)',
    "Lah-Lah's Adventures: Songs (27)",
    'Learning Time With Timmy (26)', "Lily's Driftwood Bay (30)",
    'Little Roy (10)', "Little Ted's Big Adventure (20)",
    'Luo Bao Bei (12)', 'Luo Bao Bei (Mandarin) (44)',
    "Maurice's Big Adventure (12)",
    "Miffy's Adventures Big and Small (30)", 'Mister Maker (5)',
    'Mister Maker Around The World (15)', 'Molly And Mack (20)',
    'Moon and Me (19)', 'Mouk (10)', 'Nella the Princess Knight (11)',
    'Noddy Toyland Detective (19)', 'Numberblocks (10)',
    'Octonauts (25)',
    'Octonauts And Operation Deep Freeze',
    'Octonauts (Mandarin) (30)',
    'Octonauts Special: The Over Under Adventure',
    'Olobob Top (1)', 'Our Acknowledgement of Country',
    'Pablo (14)', 'The Pajanimals (4)', 'Peg + Cat (30)', 'Peppa Pig (30)',
    'Peppa Pig (Mandarin) (27)', 'Pingu In The City (30)',
    'PJ Masks (12)', 'PJ Masks: Songs (9)', 'Play School (21)',
    'Play School: Acknowledgement of Country',
    'Play School Art Time (20)',
    'Play School Celebrity Covers (31)',
    'Play School: Stop, Look, Listen (20)',
    'Play School Story Time (24)',
    'Play School Story Time: Languages (5)',
    'Play School: Through The Windows (31)', 'Playdate (23)',
    'Pocoyo (30)', 'Pocoyo (Mandarin) (30)', 'Rainbow Chicks (39)',
    'Rainbow Chicks (Mandarin) (39)', 'Ready, Jet, Go! (29)',
    'Ready, Jet, Go!: Back To Bortron 7',
    'Ready, Steady, Wiggle! (30)', 'Rita and Crocodile (10)',
    'Rusty Rivets (14)', 'Sally & Possum (60)', 'Sarah And Duck (15)',
    'School Of Roars (29)', 'Scout And The Gumboot Kids (28)',
    'Sesame Street (30)', 'Shaun The Sheep (12)',
    'Sydney Sailboat (52)', 'Teacup Travels (10)', 'Team Rescue (22)',
    'Teeny Tiny Stevies (9)', 'Teletubbies (30)',
    'This Is Scarlett And Isaiah (51)', 'Thomas And Friends (30)',
    'Timmy Time (14)', 'Twirlywoos (30)', 'Waffle The Wonder Dog (30)',
    'Wallykazam! (10)', "We're Going On A Bear Hunt",
    'WildWoods (12)', 'The WotWots'
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
    'Sesame Street: Welcome to Sesame Hospital',
    'Sesame Street: The Furry Four',
    'Sesame Street: Earth Day',
    'Sesame Street: Honk if You Love Libraries',
    "Sesame Street: Julia's Haircut",
    'Sesame Street: Elmo the Engineer',
    'Sesame Street: Walking the Dog',
    'Sesame Street: Elmo Goes to Chicken School',
    'Sesame Street: Fishing X',
    'Sesame Street: Mechanics in Space',
    'Sesame Street: Rudy Rides the Bus',
    'Sesame Street: Sesame Friendship',
    'Sesame Street: The Big Pretend Band',
    "Sesame Street: Elmo's Happy Little Train",
    'Sesame Street: Dinosaur in the Laundromat',
    'Sesame Street: Astronaut Elmo',
    'Sesame Street: Bath Time For Blanky',
    'Sesame Street: Play Time',
    "Sesame Street: New Year's Eve Show",
    'Sesame Street: Math Magic',
    "Sesame Street: Elmo's Factory",
    'Sesame Street: So You Think Choreograph',
    'Sesame Street: Hey! Sesame Street News',
    'Sesame Street: Picture This',
    "Sesame Street: When You're a Vet",
    'Sesame Street (E09): Episode 9',
    'Sesame Street (E08): Episode 8',
    'Sesame Street (E07): Episode 7',
    'Sesame Street (E06): Episode 6',
    'Sesame Street (E05): Episode 5',
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
