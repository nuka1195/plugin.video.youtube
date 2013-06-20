"""
    Plugin for viewing content from Youtube.com
"""

# main imports
import sys

# plugin constants
__plugin__ = "YouTube"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-addons/"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/addons/plugin.video.youtube"


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        from resources.lib import categories as plugin
    elif ( "category='presets_videos'" in sys.argv[ 2 ] ):
        from resources.lib import categories as plugin
    elif ( "category='presets_users'" in sys.argv[ 2 ] ):
        from resources.lib import categories as plugin
    elif ( "category='presets_categories'" in sys.argv[ 2 ] ):
        from resources.lib import categories as plugin
    elif ( "category='my_subscriptions'" in sys.argv[ 2 ] ):
        from resources.lib import categories as plugin
    elif ( "category='delete_preset'" in sys.argv[ 2 ] ):
        from resources.lib import categories as plugin
    elif ( "category='play_video_by_id'" in sys.argv[ 2 ] ):
        from resources.lib import player_by_id as plugin
    elif ( "category='play_video'" in sys.argv[ 2 ] ):
        from resources.lib import player as plugin
    elif ( "category='download_video'" in sys.argv[ 2 ] ):
        from resources.lib import download as plugin
    else:
        from resources.lib import videos as plugin
    try:
        plugin.Main()
    except:
        pass
