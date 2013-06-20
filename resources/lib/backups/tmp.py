import urllib
BASE_LOGIN_URL = "https://www.google.com/accounts/ServiceLogin?service=youtube&hl=en_US&passive=true&ltmpl=sso&uilel=3&continue=http%3A//www.youtube.com/signup%3Fhl%3Den_US%26warned%3D%26nomobiletemp%3D1%26next%3D/"

print urllib.unquote_plus(BASE_LOGIN_URL)

if __name__ == "__main__":
    url = "http://www.youtube.com/watch?v=WIussgh00j8"
    url="http://www.youtube.com/watch?v=SMwh6zK1-QU"
    url ="http://www.youtube.com/watch?v=xXHy62bxoq8"
    #url = "http://www.youtube.com/watch?v=-xEzGIuY7kw"
    url = "http://www.youtube.com/watch?v=ao1JxzvoebI"
    client = YoutubeClient()
    # make the authentication call
    ##authkey, userid = client.authenticate( "nuka1195", "lslsj$$6545" )
    authkey = "Qyxfo8mDCvwb2XKBu6QRhxaPZx7I9zwGQPqXy-gUsggUK_ibcCFcp-ywLT3oCsEZQ1VWL0iZMQQ"
    # Youtube client
    client = YoutubeClient( client.BASE_USERS_URL, authkey )
    # fetch the videos
    # TODO: format=5, <- put this back if videos fail
    category="my_subscriptions"
    feeds = client.my_subscriptions( start__index=1, max__results=10)
    print feeds
    print feeds.keys()#['category', 'updated', 'title', 'author', 'yt$username', 'link', 'published', 'gd$feedLink', 'media$thumbnail', 'id']
    for feed in feeds[ "feed" ].get( "entry", [] ):
        print feed["author"]
        print feed["link"]
        print feed["media$thumbnail"]
        print feed["updated"]
        print feed["yt$username"]
        print feed["published"]
        print feed["gd$feedLink"]
        print feed["id"]

    # construct the video url with session id and get video details
    #url, title, director, genre, rating, runtime, count, date, thumbnail, plotoutline, video_id = client.construct_video_url( url, 18 )
    #print title
    #print url