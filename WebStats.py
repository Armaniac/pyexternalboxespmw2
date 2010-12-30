import thread
import urllib

_URL = "http://www.pyexternalboxespmw2.chickenkiller.com/web_stats"
_USER_AGENT = "pyexternalhack-1.5"

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
            if not self._prev_is_in_game:
                print "Starting match mode '%s' for map '%s'" % (self.params["gm"], self.params["map"])
                if read_game.sensitivity_raw > 0:
                    print "Sensitivity = %.1f" % (read_game.sensitivity, )
                else:
                    print "Unable to get in-game sensitivity"
        else:
            if self._prev_is_in_game:
                print "Ending match score = %s" % (self.params["score"], )
                thread.start_new_thread(fire_url, (_URL, self.params))
        
        self._prev_is_in_game = read_game.is_in_game
            