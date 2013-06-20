import urllib

url = "34%7Chttp%3A%2F%2Fv15.lscache6.c.youtube.com%2Fvideoplayback%3Fip%3D0.0.0.0%26sparams%3Did%252Cexpire%252Cip%252Cipbits%252Citag%252Calgorithm%252Cburst%252Cfactor%252Coc%253AU0dWSFNTT19FSkNNNl9LTVND%26algorithm%3Dthrottle-factor%26itag%3D34%26ipbits%3D0%26burst%3D40%26sver%3D3%26expire%3D1273381200%26key%3Dyt1%26signature%3D6F3D339F62444FB41A34A9B54B21AD0B2787737F.9E9B0D27B621B24C538D71FB7FC4A35362E620C5%26factor%3D1.25%26id%3Dfce065812cfcb123%2C"

print urllib.unquote_plus(urllib.unquote_plus(url))
