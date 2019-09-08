# flake8: noqa
NAME = 'ABC iView'
ADDON_ID = 'plugin.video.abc_iview'

USER_AGENT = 'Mozilla/5.0 (PlayStation 4) AppleWebKit/531.3 (KHTML, like Gecko) SCEE/1.0 Nuanti/2.0'
HEADERS = {'User-Agent': USER_AGENT,
           'Origin': 'http://tv.iview.abc.net.au',
           'Referer': 'http://tv.iview.abc.net.au/playstation.php'}
SECRET = 'android.content.res.Resources'

API_BASE_URL = 'https://api.iview.abc.net.au{path}'
CONFIG_URL = 'https://api.iview.abc.net.au/v2/navigation/mobile'
AUTH_PATH = '/auth/hls/sign?{params}'
AUTH_PARAMS = 'ts={ts}&hn={hn}&d=android-mobile'

#  Dictionary for converting LG iview API categories to mobile API categories
#  Many users have saved 'favourites' in Kodi, this will mitigate a lot of
#  potential errors
OLD_CATEGORIES = {
    'arts': 'channel/abcarts',
    'docs': 'category/docs',
    'comedy': 'category/comedy',
    'drama': 'category/drama',
    'education': 'category/education',
    'abc4kids': 'channel/abc4kids',
    'indigenous': 'category/arts',
    'lifestyle': 'category/lifestyle',
    'news': 'category/news',
    'panel': 'category/panel',
    'sport': 'category/sport',
    'abc1': 'channel/abc1',
    'abc2': 'channel/abc2',
    'abc3': 'channel/abc3',
    'news24': 'channel/news24',
    'iview': 'channel/iview'
}
