import Scheduler
import time
import ReadGame, Frame, Radar2, Status, Keys, Inspector, Tracker, Crosshair, Esp, Bot, Rage, Killstreak, WeaponNames, Autostab, WebStats
import Sprites, Textures, BigRadar
#import Textures, Radar2, BigRadar, PatternFinder
#import cProfile
from Config import PROFILING, MAIN_MAX_FPS
import traceback
from utils import ExitingException
import threading
from time import sleep

WM_QUIT = 0x0012


class Main(object):
    
    def __init__(self):
        self.global_plugins = []
        self.game_plugins = []
        
        self.ticks = 0
        self.time = time.clock()
        self.quit = False
        self.wnd_thread = None
        
        self.lock = threading.Lock()
        self.sleep_interval = 1.0 / MAIN_MAX_FPS
        
        self.sched = Scheduler.Scheduler()
                
        # read_game and frame are 2 special modules
        self.read_game = ReadGame.ReadGame(self)
        #self.pattern_finder = PatternFinder.PatternFinder(self)
#        self.pattern_finder = PatternFinder.PatternFinder(self)
        self.frame = Frame.Frame(self)
        self.textures = Textures.Textures(self)
        self.tracker = Tracker.Tracker(self)
        # other are simple modules
        self.rage = Rage.Rage(self)
        self.status = Status.Status(self)
        self.esp = Esp.Esp(self)
        self.radar = Radar2.Radar(self)
        self.bigradar = BigRadar.BigRadar(self)
        self.sprites = Sprites.Sprites(self)
        self.crosshair = Crosshair.Crosshair(self)
        self.bot = Bot.Bot(self)
        self.autostab = Autostab.Autostab(self)
        self.killstreak = Killstreak.Killstreak(self)
        self.weapon_names = WeaponNames.WeaponNames(self)
        self.webstats = WebStats.WebStats(self)
        # inspector debug class
        self.inspector = Inspector.Inspector(self)
    
    def init(self):
        # first wait for game
        self.read_game.init()
        #self.pattern_finder.find_patterns(self.read_game.mw2_process.handle)
        self.wnd_thread = threading.Thread(target=self.thread_window)
        self.wnd_thread.daemon = True
        self.wnd_thread.start()
        # then prepare frame environment
        window_ready = False
        while not window_ready:
            #with self.lock:
            try:
                self.lock.acquire()
                if self.frame.hwnd is not None:
                    window_ready = True
            finally:
                self.lock.release()
            sleep(0.050)
        self.frame.init_d3d()
        self.textures.init()
        self.sprites.init()
        
    def run(self):
        if PROFILING:
            iter = 0
        while not self.quit:
            self.ticks += 1
            self.time = time.clock()
            
            self.read_game.render()
            self.frame.BeginPaint()
            Keys.render()
            self.tracker.render()
            
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
            self.webstats.render()
            self.inspector.render()
            # now run scheduled coroutines
            self.sched.mainloop_1()
            #
            self.frame.EndPaint()

            time.sleep(self.sleep_interval)                                   # avoid eating up all CPU
            if PROFILING:
                iter += 1
                if iter > 5000 :return      # 1 iteration only

    def release(self):
        if self.frame:
            print "Application ending, cleaning up D3D"
            try:
                self.frame.release_d3d()
            except Exception:
                pass
        self.frame = None
        
    def thread_window(self):
        #with self.lock:
        try:
            self.lock.acquire()
            self.frame.init_create_window()
        finally:
            self.lock.release()
        self.frame.pump_messages()

def launch():
    #import psyco
    #psyco.profile()
    m = Main()
    try:
        m.init()
        m.run()
#        if PROFILING:
#            cProfile.runctx('m.run()', globals(), locals())
#        else:
#            m.run()
    except ExitingException, e:
        print "Exiting: %s" % e
    except Exception:
        m.release()
        traceback.print_exc()
        raw_input("Press [ENTER] to exit application")

    finally:
        m.release()
