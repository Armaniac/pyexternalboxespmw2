import stealth      # scramble memory a little - anti-VAC feature
import time
import win32gui, win32con
import ReadGame, Frame, Textures, Radar, Esp, Status, Keys, Autostab, Inspector, Rage, Killstreak, BigRadar, WeaponNames
import Crosshair, Bot
import cProfile
from Config import MAIN_LOOP_SLEEP, PROFILING

WM_QUIT = 0x0012

class Main(object):
    
    def __init__(self):
        self.global_plugins = []
        self.game_plugins = []
        
        self.ticks = 0
        self.time = time.clock()
        self.quit = False
                
        # read_game and frame are 2 special modules
        self.read_game = ReadGame.ReadGame(self)
        self.frame = Frame.Frame(self)
        self.textures = Textures.Textures(self)
        # other are simple modules
        self.rage = Rage.Rage(self)
        self.status = Status.Status(self)
        self.esp = Esp.Esp(self)
        self.radar = Radar.Radar(self)
        self.bigradar = BigRadar.BigRadar(self)
        self.crosshair = Crosshair.Crosshair(self)
        self.bot = Bot.Bot(self)
        self.autostab = Autostab.Autostab(self)
        self.killstreak = Killstreak.Killstreak(self)
        self.weapon_names = WeaponNames.WeaponNames(self)
        # inspector debug class
        self.inspector = Inspector.Inspector(self)
    
    def init(self):
        # first wait for game
        self.read_game.init()
        # then prepare frame environment
        self.frame.init()
        self.frame.init_d3d()
        self.textures.init()
                
    def run(self):
        if PROFILING:
            iter = 0
        while not self.quit:            
            pending, msg = win32gui.PeekMessage(0, 0, 0, win32con.PM_REMOVE)
            #===================================================================
            # if (msg[2] & 0xFFFF) == WM_QUIT:
            #    break
            #===================================================================

            self.ticks += 1
            self.time = time.clock()
            win32gui.TranslateMessage(msg)

            self.read_game.render()
            self.frame.BeginPaint()
            Keys.render()
            
            self.weapon_names.render()
            self.rage.render()
            self.status.render()
            self.esp.render()
            self.radar.render()
            self.bigradar.render()
            self.crosshair.render()
            self.bot.render()
            self.autostab.render()
            self.killstreak.render()
            #
            self.inspector.render()
            #
            self.frame.EndPaint()

            win32gui.DispatchMessage(msg)
            time.sleep(MAIN_LOOP_SLEEP)                                   # avoid eating up all CPU
            if PROFILING:
                 iter += 1
                 if iter > 5000 :return      # 1 iteration only

    def release(self):
        self.frame.release_d3d()

def launch():
    import psyco
    psyco.profile()
    m = Main()
    try:
        m.init()
        if PROFILING:
            cProfile.runctx('m.run()', globals(), locals())
        else:
            m.run()
    finally:
        print "Application ending, cleaning up D3D"
        m.release()


if __name__ == '__main__':
    launch()