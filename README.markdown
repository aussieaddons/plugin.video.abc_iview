ABC iView addon for XBMC
================================

This addon provides a simple list of available programs from the ABC iView
web site, and allows you to stream them with.

The content is only available with Australia, or you can apparently use sites
like Unblock-US, UnoTelly or Tunlr.net (free). or your own VPN solution which
terminates in with an AU IP address.

We now support streaming using both RTMP (old) and HTTP (new). In some cases
the RTMP stream can crash XBMC, especially for older versions of XBMC.
HTTPS streaming support is still new, but is probably more reliable and
recommended. You can switch your streaming method from the addon settings.

This addon wouldn't be possible without the great work on python-iview from
Jeremy Visser.
https://jeremy.visser.name/2009/08/python-iview/

Thanks also for contributions from:
  * sdt (Stephen Thirlwall)
  * Adam M-W

Installation
------------
The latest stable release of this add-on is available as part of the
[XBMC CatchUp TV AU repository] [repository].

If you prefer, you can grab the stable release ZIP file by itself from the
[Github project site download] [download].

For the latest development version, you can grab the [GitHub generated ZIP file] [githubzip].

Simply download the ZIP file to your XBMC device and install through the menu via
System -> Settings -> Add-ons -> Install from zip file, but ensure you've
uninstalled any previous version first.

Issues
------
In some cases the RTMP stream can crash XBMC, especially for older versions.
It is recommended that you use XBMC v13 (Gotham) or later and switch to HTTP
streaming via the addon settings.

For any other issues or bug reports, please file them on the [issues page] [issues].

Please include log output if possible, using Github Gist or Pastebin.com.

The location of your XBMC log file will depend on your platform.

For Windows:
```
%APPDATA%\XBMC\temp\xbmc.log
```

For Linux:
```
~/.xbmc/temp/xbmc.log
```

For Mac OS X:
```
~/Library/Application Support/XBMC/temp/xbmc.log
```

For AppleTV:
```
/Users/frontrow/Library/Application Support/XBMC/temp/xbmc.log
```

Contact Me
----------
For anything else, you can contact me by email at andy#andybotting.com

[repository]: https://github.com/xbmc-catchuptv-au/repo
[download]: https://github.com/xbmc-catchuptv-au/repo/tree/master/plugin.video.abc_iview
[githubzip]: https://github.com/andybotting/xbmc-addon-abc-iview/archive/master.zip
[issues]: https://github.com/andybotting/xbmc-addon-abc-iview/issues
