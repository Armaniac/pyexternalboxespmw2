from Keys import keys
import thread
import urllib

_URL = "http://www.pyexternalboxespmw2.chickenkiller.com/web_stats"
_USER_AGENT = "pyexternalboxespmw2-5.1"

def fire_url(url, params):
    try:
        urllib.urlcleanup()
        real_url = url+"?"+urllib.urlencode(params)
        #print "Firing url="+real_url
        file = urllib.urlopen(real_url)
    except:
        pass


class MyURLopener(urllib.URLopener):
    version = _USER_AGENT

urllib._urlopener = MyURLopener()
    

class WebStats(object):
    
    def __init__(self, env):
        self.env = env
        self._prev_is_in_game = False
        self.params = {}
    
    def render(self):
        read_game = self.env.read_game
        if read_game.is_in_game:
            self.params["map"] = read_game.map_name
            self.params["score"] = "%i-%i" % (read_game.kills, read_game.deaths)
            self.params["gm"] = read_game.game_mode
            self.params["ch"] = keys["KEY_CROSSHAIR"] and 1 or 0
            self.params["esp"] = keys["KEY_BOXESP"] and 1 or 0
            self.params["sl"] = keys["KEY_BOX_SNAPLINE"] and 1 or 0
            self.params["rd"] = keys["KEY_RADAR"] and 1 or 0
            self.params["bot"] = keys["KEY_AIMBOT_ACTIVE"] and 1 or 0
            self.params["kn"] = keys["KEY_KNIFEBOT_ACTIVE"] and 1 or 0
            self.params["as"] = keys["KEY_AUTOSTAB"] and 1 or 0
            self.params["tg"] = keys["KEY_TRIGGERBOT"] and 1 or 0
            self.params["brd"] = keys["KEY_BIG_RADAR"] and 1 or 0
            if not self._prev_is_in_game:
                print "Starting match mode '%s' for map '%s'" % (self.params["gm"], self.params["map"])
                print "Sensitivity = %.1f" % (read_game.sensitivity, )
        else:
            if self._prev_is_in_game:
                print "Ending match score = %s" % (self.params["score"], )
                thread.start_new_thread(fire_url, (_URL, self.params))
        
        self._prev_is_in_game = read_game.is_in_game
            