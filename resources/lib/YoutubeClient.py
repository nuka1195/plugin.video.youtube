"""
    Youtube api client module
"""

# main imports
import sys
import os
from urllib import urlencode, unquote_plus, quote_plus
import urllib2
import cookielib
import re

try:
    import xbmc
    try:
        import xbmcaddon
    except:
        # get xbox compatibility module
        from xbox import *
        xbmcaddon = XBMCADDON()
    DEBUG = False
except:
    DEBUG = True


class YoutubeClient:
    # Addon module
    Addon = xbmcaddon.Addon(id=os.path.basename(os.getcwd()))
    # base urls
    BASE_STANDARD_URL = "http://gdata.youtube.com/feeds/api/standardfeeds/%s?%s"
    BASE_SEARCH_URL = "http://gdata.youtube.com/feeds/api/%s?%s"
    BASE_USERS_URL = "http://gdata.youtube.com/feeds/api/%s?%s"
    BASE_VIDEO_URL = "http://www.youtube.com/get_video.php?video_id=%s&t=%s&fmt=35"
    BASE_VIDEO_TOKEN_URL = "http://www.youtube.com/get_video_info.php?video_id=%s"
    BASE_ID_URL = "http://www.youtube.com/watch?v=%s"
    BASE_MIDDIO_RANDOM_URL = "http://middio.com/random"
    BASE_VIDEO_COMMENTS_FEED = "http://gdata.youtube.com/feeds/api/videos/%s/comments?%s"
    BASE_VIDEO_DETAILS_URL = "http://gdata.youtube.com/feeds/api/videos/%s?%s"
    BASE_RELATED_URL = "http://gdata.youtube.com/feeds/api/videos/%s/related?%s"
    BASE_AUTHENTICATE_URI = "https://www.google.com/youtube/accounts/ClientLogin"
    BASE_LOGIN_URL = "http://www.youtube.com/signup?hl=en_US&warned=&nomobiletemp=1&next=/&action_login"

    # developer key and client id
    YOUTUBE_DEVELOPER_KEY = u"%s" % (str([ chr(c) for c in (65, 73, 51, 57, 115, 105, 53, 84, 113, 48, 66, 49, 102, 87, 87, 72, 49, 74, 72, 75, 88, 86, 66, 69, 106, 48, 77, 86, 99, 117, 108, 78, 71, 87, 97, 48, 50, 73, 116, 100, 70, 105, 100, 74, 54, 103, 116, 122, 106, 116, 101, 89, 68, 54, 97, 77, 52, 45, 87, 68, 99, 101, 99, 49, 111, 102, 84, 104, 99, 86, 110, 74, 103, 114, 110, 83, 83, 111, 79, 88, 76, 45, 98, 65, 107, 100, 109, 82, 112, 122, 108, 48, 45, 88, 48, 89, 80, 81,) ]).replace("'", "").replace(", ", "")[ 1 :-1 ],)
    YOUTUBE_CLIENT_ID = u"%s" % (str([ chr(c) for c in (121, 116, 97, 112, 105, 45, 78, 117, 107, 97, 45, 88, 66, 77, 67, 89, 111, 117, 116, 117, 98, 101, 45, 97, 51, 105, 99, 52, 104, 103, 108, 45, 48,) ]).replace("'", "").replace(", ", "")[ 1 :-1 ],)

    # base path
    if (DEBUG):
        BASE_COOKIE_PATH = os.path.join(os.getcwd(), "cookie.txt")
    else:
        BASE_COOKIE_PATH = os.path.join(xbmc.translatePath(self.Addon.getAddonInfo("Profile")), "cookie.txt")

    def __init__(self, base_url=None, authkey=None, email=None):
        # install our opener for cookie handling
        self._install_opener()
        self.base_url = base_url
        self.authkey = authkey
        self.email = email

    def _install_opener(self):
        # set cookie jar
        self.cookie_jar = cookielib.LWPCookieJar()
        # load cookie if it exists
        if (os.path.isfile(self.BASE_COOKIE_PATH)):
            self.cookie_jar.load(self.BASE_COOKIE_PATH)
        # create the opener object
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        # install opener
        urllib2.install_opener(opener)

    def __getattr__(self, feeds):
        def feeds(_feeds=feeds, **params):
            try:
                # json uses null instead of None, true instead of True and false instead of False (should be faster than replace()
                true = True
                false = False
                null = None
                # if this is a users favorites or uploads
                if (_feeds.startswith("my_") or _feeds.startswith("add_")):
                    _feeds = "users/default/%s" % (_feeds.split("_")[ 1 ],)
                # if this is a user search, add username and eliminate author
                #if ( _feeds == "users" ):
                #    _feeds = "users__uploads"
                # convert double underscore to format specifier for feed
                _feeds = _feeds.replace("__", "/%s/")
                # if this is a users feed, add username and eliminate author
                if (_feeds.startswith("users/%s/")):
                    _feeds = _feeds % (params[ "author" ],)
                    del params[ "author" ]
                if (_feeds.startswith("related")):
                    _feeds = params[ "related" ]
                    del params[ "related" ]
                # convert double underscore to hyphen for parameter name and remove parameters with no value
                fparams = {}
                for key, value in params.items():
                    if (value):
                        # if a region id was passed, use it
                        if (key == "region_id"):
                            _feeds = "%s/%s" % (value, _feeds,)
                        else:
                            fparams[ key.replace("__", "-") ] = value
                # add alt parameter with a value of json, as it basically returns a python dictionary
                fparams[ "alt" ] = "json"
                # add client id and developer key
                fparams[ "client" ] = self.YOUTUBE_CLIENT_ID
                fparams[ "key" ] = self.YOUTUBE_DEVELOPER_KEY
                if (self.email is not None):
                    fparams[ "Email" ] = self.email
                # we need to request the url to be redirected to the swf player url to grab the session id
                request = urllib2.Request(self.base_url % (_feeds, urlencode(fparams),))
                # add authentication header
                if (self.authkey is not None and self.authkey != ""):
                    request.add_header("Authorization", "GoogleLogin auth=%s" % self.authkey)
                # read source
                jsonSource = urllib2.urlopen(request).read()
                # eval jsonSource to a native python dictionary (startswith is a safety check)
                if (jsonSource.startswith("{")):
                    return eval(jsonSource.replace("\\/", "/"))
                return {}
            except:
                # oops return an empty dictionary
                print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
                return {}
        return feeds

    def add_favorites(self, video_id):
        try:
            # create the xml data string
            add_request = '<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom"><id>%s</id></entry>' % (video_id,)
            # we need to request the url to post our data
            request = urllib2.Request(self.base_url % ("users/default/favorites/", "",), add_request)
            # add authentication header
            if (self.authkey is not None and self.authkey != ""):
                request.add_header("Authorization", "GoogleLogin auth=%s" % self.authkey)
            # add the rest of the headers
            request.add_header("X-GData-Client", self.YOUTUBE_CLIENT_ID)
            request.add_header("X-GData-Key", "key=%s" % self.YOUTUBE_DEVELOPER_KEY)
            request.add_header("Content-Type", "application/atom+xml")
            request.add_header("Content-Length", str(len(add_request)))
            # open url
            usock = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            # if successful return True
            if (str(e) == "HTTP Error 201: Created"):
                return True
        # we failed
        return False

    def delete_favorites(self, delete_url):
        try:
            # authentication is required
            if (self.authkey is None or self.authkey == ""):
                return False
            # add our headers
            headers = {}
            headers[ "Authorization" ] = "GoogleLogin auth=%s" % (self.authkey,)
            headers[ "X-GData-Client" ] = self.YOUTUBE_CLIENT_ID
            headers[ "X-GData-Key" ] = "key=%s" % self.YOUTUBE_DEVELOPER_KEY
            headers[ "Content-Type" ] = "application/atom+xml"
            headers[ "Host" ] = "gdata.youtube.com"
            headers[ "GData-Version" ] = "1"
            # we use httplib for a DELETE request
            import httplib
            # connect
            conn = httplib.HTTPConnection("gdata.youtube.com")
            # get our request object
            conn.request("DELETE", delete_url, headers=headers)
            # get the response
            response = conn.getresponse()
            # 200 means successful
            if (response.status == 200):
                return True
        except:
            # oops return an empty list
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
        # we failed
        return False

    def get_comments(self, video_id, **params):
        try:
            # TODO: enable this
            # json uses null instead of None, true instead of True and false instead of False (should be faster than replace()
            true = True
            false = False
            null = None
            # set params
            fparams = {}
            for key, value in params.items():
                if (value): fparams[ key.replace("__", "-") ] = value
            # add alt parameter with a value of json, as it basically returns a python dictionary
            fparams[ "alt" ] = "json"
            # add client id and developer key
            fparams[ "client" ] = self.YOUTUBE_CLIENT_ID
            fparams[ "key" ] = self.YOUTUBE_DEVELOPER_KEY
            # we use a request object to add the auth headers
            request = urllib2.Request(self.BASE_VIDEO_DETAILS_URL % (video_id, urlencode(fparams),))
            # add a faked header, we use ie 8.0. it gives correct results for regex
            request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
            ##usock = urllib2.urlopen( self.BASE_VIDEO_COMMENTS_FEED % ( video_id, urlencode( fparams ), ) )
            # TODO: remove these if above works
            #request.add_header( "X-GData-Client", self.YOUTUBE_CLIENT_ID )
            #request.add_header( "X-GData-Key", "key=%s" % self.YOUTUBE_DEVELOPER_KEY )
            if (self.authkey is not None and self.authkey != ""):
                request.add_header("Authorization", "GoogleLogin auth=%s" % self.authkey)
            # read source
            jsonSource = urllib2.urlopen(request).read()
            # eval jsonSource to a native python dictionary (startswith is a safety check)
            if (jsonSource.startswith("{")):
                return eval(jsonSource.replace("\\/", "/"))["feed"]["entry"]
            return []
        except:
            # oops return an empty list
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
            return []

    def get_details(self, video_id, **params):
        try:
            # json uses null instead of None, true instead of True and false instead of False (should be faster than replace()
            true = True
            false = False
            null = None
            # set params
            fparams = {}
            for key, value in params.items():
                if (value): fparams[ key.replace("__", "-") ] = value
            # add alt parameter with a value of json, as it basically returns a python dictionary
            fparams[ "alt" ] = "json"
            # add client id and developer key
            fparams[ "client" ] = self.YOUTUBE_CLIENT_ID
            fparams[ "key" ] = self.YOUTUBE_DEVELOPER_KEY
            # we use a request object to add the auth headers
            request = urllib2.Request(self.BASE_VIDEO_DETAILS_URL % (video_id, urlencode(fparams),))
            # TODO: remove these if above works
            #request.add_header( "X-GData-Client", self.YOUTUBE_CLIENT_ID )
            #request.add_header( "X-GData-Key", "key=%s" % self.YOUTUBE_DEVELOPER_KEY )
            if (self.authkey is not None and self.authkey != ""):
                request.add_header("Authorization", "GoogleLogin auth=%s" % self.authkey)
            # read source
            jsonSource = urllib2.urlopen(request).read()
            # eval jsonSource to a native python dictionary (startswith is a safety check)
            details = {}
            if (jsonSource.startswith("{")):
                details = eval(jsonSource.replace("\\/", "/"))
            # set our values
            encoding = details[ "encoding" ]
            # title (exec is a hack for unescaping \u#### characters)
            exec 'title = u"%s"' % (unicode(details[ "entry" ][ "title" ][ "$t" ].replace('"', '\\"'), encoding, "replace"),)
            # author (exec is a hack for unescaping \u#### characters)
            exec 'author = u"%s"' % (unicode(details[ "entry" ][ "author" ][ 0 ][ "name" ][ "$t" ].replace('"', '\\"'), encoding, "replace"),)
            # genre
            genre = details[ "entry" ][ "media$group" ][ "media$category" ][ 0 ][ "$t" ]
            # viewer rating
            try:
                rating = float(details[ "entry" ][ "gd$rating" ][ "average" ])
            except:
                rating = 0.0
            # format runtime as 00:00
            runtime = int(details[ "entry"][ "media$group" ][ "yt$duration" ][ "seconds" ])
            # video runtime
            if (runtime):
                runtime = "%02d:%02d" % divmod(runtime, 60)
            else:
                runtime = ""
            # times viewed
            try:
                count = int(details[ "entry"][ "yt$statistics" ][ "viewCount" ])
            except:
                count = 0
            # updated date
            date = "%s-%s-%s" % (details[ "entry" ][ "updated" ][ "$t" ][ 8 : 10 ], details[ "entry" ][ "updated" ][ "$t" ][ 5 : 7 ], details[ "entry" ][ "updated" ][ "$t" ][ : 4 ],)
            # thumbnail url
            thumbnail_url = details[ "entry" ][ "media$group" ][ "media$thumbnail" ][ -1 ][ "url" ]
            # plot
            plot = ""
            if ("media$description" in details[ "entry" ][ "media$group" ]):
                # we need to replace \n and \r as it messes up our exec hack (exec is a hack for unescaping \u#### characters)
                exec 'plot = u"%s"' % (unicode(details[ "entry" ][ "media$group" ][ "media$description" ][ "$t" ].replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r"), encoding, "replace"),)
            # return our values
            return title, author, genre, rating, runtime, count, date, thumbnail_url, plot
        except:
            # oops return a list of empty strings
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
            return [ "" ] * 9

    def construct_video_url_keepvid(self, url, quality=18, encoding="UTF-8"):
        try:
            url = unquote_plus(url)
            video_id = url.split("v=")[ 1 ]
            # we need to unquote the play url
            url = "http://keepvid.com/?url=" + quote_plus(url)
            # spam url to log for checking
            if (not DEBUG):
                xbmc.log("[PLUGIN] '%s: version %s' - (quality=%d, video url=%s)" % (sys.modules[ "__main__" ].__plugin__, sys.modules[ "__main__" ].__version__, quality, url,), xbmc.LOGDEBUG)
            # we need to request the url to be redirected to the swf player url to grab the session id
            request = urllib2.Request(url)
            # add a faked header, we use ie 8.0. it gives correct results for regex
            request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
            # create an opener object to grab the info
            opener = urllib2.urlopen(request)
            # read source
            htmlSource = opener.read()
            # close opener
            opener.close()
            # get the video id and session id
            video_url = unquote_plus(re.findall("<a href=\"/save-video.mp4?(.+?)\"", htmlSource)[ 0 ])[ 1 : ]
            # get details for the video and return the details
            title, author, genre, rating, runtime, count, date, thumbnail_url, plot = self.get_details(video_id)
            # return our values
            return video_url, title, author, genre, rating, runtime, count, date, thumbnail_url, plot, video_id
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
            return [ "" ] * 11

    def construct_video_url(self, url, quality=18, encoding="UTF-8"):
        try:
            # we need to unquote the play url
            video_url = self.BASE_VIDEO_TOKEN_URL % (unquote_plus(url).split("v=")[ 1 ],)
            # spam url to log for checking
            if (not DEBUG):
                xbmc.log("[PLUGIN] '%s: version %s' - (quality=%d, video url=%s)" % (sys.modules[ "__main__" ].__plugin__, sys.modules[ "__main__" ].__version__, quality, url,), xbmc.LOGDEBUG)
            # we need to request the url to be redirected to the swf player url to grab the session id
            request = urllib2.Request(video_url)
            # add a faked header, we use ie 8.0. it gives correct results for regex
            request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
            # create an opener object to grab the info
            opener = urllib2.urlopen(request)
            # read source
            htmlSource = opener.read()
            # close opener
            opener.close()
            # reset video_url
            video_url = None
            # check if unsuccessful
            if (htmlSource.startswith("status=fail&errorcode=150")):
                # we need to request the url to be redirected to the swf player url to grab the session id
                request = urllib2.Request(url)
                # add a faked header, we use ie 8.0. it gives correct results for regex
                request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
                # create an opener object to grab the info
                opener = urllib2.urlopen(request)
                # read source
                htmlSource = opener.read()
                # close opener
                opener.close()
                # get the video id 'video_id': '-xEzGIuY7kw'
                video_id = re.findall("\"video_id\": \"([^\"]+)\"", htmlSource)[ 0 ]
                # get video urls
                try:
                    fmt_url_map = unquote_plus(re.findall("\"fmt_url_map\": \"([^\"]+)\"", htmlSource)[ 0 ]).split(",")
                except:
                    # none found, handle special TODO: figure out why 403 forbidden for (MacGyver)
                    # get session token
                    token = re.findall("\"t\": \"([^\"]+)\"", htmlSource)[ 0 ]
                    # create video url
                    video_url = self.BASE_VIDEO_URL % (video_id, token,)
            else:
                # get the video id
                video_id = re.findall("&video_id=([^&]+)", htmlSource)[ 0 ]
                # get video urls
                fmt_url_map = unquote_plus(re.findall("&fmt_url_map=([^&]+)", htmlSource)[ 0 ]).split(",")
            # only need to do this if getting video urls succeeded
            if (video_url is None):
                # enumerate thru and get proper video
                for url in fmt_url_map:
                    # if user preference is HD look for 22
                    if (quality == 22 and url.startswith("22|")):
                        video_url = url.split("|")[ 1 ]
                        break
                    elif (url.startswith("35|") or url.startswith("34|") or url.startswith("18|")):
                        video_url = url.split("|")[ 1 ]
                        break
            # get details for the video and return the details
            title, author, genre, rating, runtime, count, date, thumbnail_url, plot = self.get_details(video_id)
            # return our values
            return video_url, title, author, genre, rating, runtime, count, date, thumbnail_url, plot, video_id
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
            return [ "" ] * 11

    def get_random_middio_video(self, quality=0):
        try:
            # we need to request the url to be redirected to the swf player url to grab the session id
            request = urllib2.Request(self.BASE_MIDDIO_RANDOM_URL)
            # create an opener object to grab the info
            opener = urllib2.urlopen(request)
            # get htmlSource
            htmlSource = opener.read()
            # close opener
            opener.close()
            # we only need the video id. find the youtube url
            id_start = htmlSource.find("http://www.youtube.com/watch?v=")
            # find the ending quote
            id_end = htmlSource.find('"', id_start + 1)
            # the video url should be the only parameter after the equal sign
            video_id = htmlSource[ id_start + 1 : id_end ].split("=")[ 1 ]
            # we found a valid video id, construct the url and fetch the real video url
            url, title, author, genre, rating, runtime, count, date, thumbnail_url, plot, vidoe_id = self.construct_video_url(self.BASE_ID_URL % (video_id,), quality)
            # return our values
            return url, title, author, genre, rating, runtime, count, date, thumbnail_url, plot
        except:
            # oops return a list of empty strings
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
            return [ "" ] * 10

    def authenticate(self, user_id, user_password):
        try:
            # the needed parameters for authenticating
            auth_request = { "Email": user_id, "Passwd": user_password, "service": "youtube", "source": "XBMC Youtube" }#"accountType": "HOSTED_OR_GOOGLE", 
            # we post the needed authentication request to our uri
            request = urllib2.Request(self.BASE_AUTHENTICATE_URI, urlencode(auth_request))
            # add the required header
            request.add_header("Content-Type", "application/x-www-form-urlencoded")
            # create an opener object to grab the data
            opener = urllib2.urlopen(request)
            # read data
            data = opener.read()
            # close opener
            opener.close()
            # find the authentication key
            authkey = re.findall("Auth=(.+)", data)[ 0 ]
            userid = re.findall("YouTubeUser=(.+)", data)[ 0 ]
            # we must login for adult videos
            self._login(user_id, user_password)
            # return the authentication key
            return authkey, userid
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
            return "", ""

    def _login(self, user_id, user_password):
        try:
            # the needed parameters for logging in
            login_request = { "current_form": "loginForm", "username": user_id, "password": user_password, "action_login": "Log In" }
            # we post the needed authentication request to our url
            request = urllib2.Request(self.BASE_LOGIN_URL, urlencode(login_request))
            # add a faked header, we use ie 8.0. it gives correct results for regex
            request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
            # create an opener object to grab the data
            opener = urllib2.urlopen(request)
            # read data
            data = opener.read()
            # close opener
            opener.close()
            # save cookie
            self.cookie_jar.save(self.BASE_COOKIE_PATH)
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)

if __name__ == "__main__":
    url = "http://www.youtube.com/watch?v=WIussgh00j8"
    url = "http://www.youtube.com/watch?v=SMwh6zK1-QU"
    #url ="http://www.youtube.com/watch?v=xXHy62bxoq8"
    #url = "http://www.youtube.com/watch?v=-xEzGIuY7kw"
    client = YoutubeClient(YoutubeClient.BASE_SEARCH_URL)
    # make the authentication call
    authkey, userid = client.authenticate("nuka1195", "lslsj$$6545")
    print authkey
    client = YoutubeClient()
    # construct the video url with session id and get video details
    url, title, director, genre, rating, runtime, count, date, thumbnail, plotoutline, video_id = client.construct_video_url(url, 18)
    print title
    print url
