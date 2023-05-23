import threading
import socket

from xbmc import Monitor
import xbmcaddon

from aussieaddonscommon import utils
if utils.get_kodi_major_version() >= 19:
    from socketserver import TCPServer
else:
    from SocketServer import TCPServer

from resources.lib.PlaylistRequestHandler import PlaylistRequestHandler

ADDON = xbmcaddon.Addon()

# server defaults
TCPServer.allow_reuse_address = True


def select_unused_port():
    """
    Helper function to select an unused port on the host machine
    :return: int - Free port
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    _, port = sock.getsockname()
    sock.close()
    return port


playlist_req_port = select_unused_port()
ADDON.setSetting('playlist_port', str(playlist_req_port))

playlist_req_server = TCPServer(('127.0.0.1', playlist_req_port),
                             PlaylistRequestHandler)
playlist_req_server.server_activate()
playlist_req_server.timeout = 1
utils.log('Started iplay playlist HTTP server on port {0}'
          .format(playlist_req_port))

if __name__ == '__main__':
    mon = Monitor()

    # start thread for playlist HTTP service
    playlist_proxy_thread = threading.Thread(target=playlist_req_server.serve_forever)
    playlist_proxy_thread.daemon = True
    playlist_proxy_thread.start()

    # kill the services if kodi monitor tells us to
    while not mon.abortRequested():
        if mon.waitForAbort(5):
            playlist_req_server.shutdown()
            break

    # Netflix service shutdown sequence
    playlist_req_server.server_close()
    playlist_req_server.socket.close()
    playlist_req_server.shutdown()
    utils.log('Stopped iplay playlist HTTP server')
