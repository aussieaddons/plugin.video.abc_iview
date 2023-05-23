import http.server

from aussieaddonscommon import utils

from future.moves.urllib.parse import unquote_plus, urljoin

import requests


class PlaylistRequestHandler(http.server.BaseHTTPRequestHandler):
    """ Workaround for malformed HLS playlists that reference 
        audio variants which don't exist (but audio is still bundled
        with the video .TS stream)
    """

    def FixMasterPlaylist(self, text, base_url):
        MEDIA = "#EXT-X-MEDIA:"
        STREAM_INF = "#EXT-X-STREAM-INF:"
        output = []
        found_stream_inf = False
        for line in text.splitlines():
            if line.startswith(MEDIA):
                uri_pos = line.find('URI="') + 5
                path = line[uri_pos:-1]
                if not path.startswith('http'):
                    line = line.replace(path, urljoin(base_url, path))
            elif line.startswith(STREAM_INF):
                found_stream_inf = True
                line = line.replace(',AUDIO="audio_aac"', '')
            elif found_stream_inf:
                found_stream_inf = False
                if not line.startswith('http'):
                    line = urljoin(base_url, line)
            output.append(line)
        return '\n'.join(output).encode('utf-8')
    
    def do_GET(self):#, body=True):
        utils.log('Proxying {0}'.format(self.path))
        """Intercept and alter response"""
        path = unquote_plus(self.path)[1:]
        path = path[:path.find('|')]
        base_url = urljoin(path, '.')
        headers = self.headers
        del headers['Host']
        res = requests.get(path, headers=headers).text
        res = self.FixMasterPlaylist(res, base_url)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(res)

    def do_HEAD(self):
        """Send a 200 on any HTTP HEAD request"""
        self.send_response(200)
        self.end_headers()
