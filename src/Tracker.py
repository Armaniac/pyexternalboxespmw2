from structs import EntityTracker, ET_PLAYER, PLAYERMAX

class Tracker(object):
    _next_zombie = -1                               # decrementing number for the next zombie index to use
    
    def __init__(self, env):
        self.env = env
        self._tracked_ent = {}
        
    def render(self):
        read_game = self.env.read_game
        
        if not read_game.is_in_game:
            self._tracked_ent.clear()                # clear all tracked entities
            return
    
        te_keys = self._tracked_ent.keys()           # get a copy so when we change the map it doesn't interfere with loop
        for idx in te_keys:
            te = self._tracked_ent[idx]
            if idx >= 0:                     # do not update if zombie object
                te.set_values(read_game.mw2_entity.arr[te.idx])
                if not(te.alive & 0x01):                # do not update if zombie object                  # go to zombie mode
                    del self._tracked_ent[idx]           # remove from regular list
                    if te.endoflife > 0 and te.endoflife > read_game.game_time:
                        te.idx = self.get_next_zombie_idx()   
                        self._tracked_ent[te.idx] = te   # re-register entity as a zombie
            elif te.endoflife <= read_game.game_time:
                del self._tracked_ent[idx]
    
    def track_entity(self, idx, owner=-1):
        read_game = self.env.read_game
        if not idx in self._tracked_ent:
            e = read_game.mw2_entity.arr[idx]
            te = EntityTracker(idx)
            te.startoflife = read_game.game_time
            te.set_values(e)
            te.weapon_num = e.WeaponNum
            te.model_name = self.env.weapon_names.get_weapon_model(e.WeaponNum)
            if owner >= 0 and owner < PLAYERMAX:
                te.planter = read_game.player[owner]
            else:
                te.planter = self.find_nearest_player(te.pos)
            # if airdrop
            self._tracked_ent[idx] = te
            return te
        else:
            return None                             # no new object created

    def find_nearest_player(self, pos):
        read_game = self.env.read_game
        dist = -1
        cur_p = read_game.my_player
        for p in read_game.player:
            if (p.type == ET_PLAYER) and p.valid and p.alive & 0x01: 
                len = (pos-p.pos).length()
                if dist < 0:
                    dist = len
                    cur_p = p
                elif len < dist:
                    dist = len
                    cur_p = p
        return cur_p

    def get_tracked_entity_list(self):
        return self._tracked_ent.values()

    def get_next_zombie_idx(self):
        Tracker._next_zombie -= 1
        return Tracker._next_zombie
    