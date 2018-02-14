import sys
import math
import random
import copy
from collections import OrderedDict

HDEPTH = 3
DEPTH = 2
DBG = 1
# inp = open('50turns.in')
# inp.readline().strip() | input()


def error(msg, **kwargs):
    print(msg, kwargs, file=sys.stderr)


def debug(msg, **kwargs):
    if DBG:
        error(msg, **kwargs)


class Utils:
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def move(x, y):
        print("MOVE {x} {y}".format(x=x, y=y))

    @staticmethod
    def fire(x, y):
        print("FIRE {x} {y}".format(x=x, y=y))

    @staticmethod
    def distance(a, b):
        return (abs(a.x - b.x) + abs(a.y - b.y)) / 2

    @staticmethod
    def belongs_to(c, cmin, cmax):
        return cmin <= c <= cmax

    @staticmethod
    def same_position(a, b):
        return a.x == b.x and a.y == b.y

    @staticmethod
    def min(a, b):
        if a < b:
            return a
        else:
            return b


class Bateau(object):
    def __init__(self, id, x, y, orientation, vitesse, rhum, est_a_moi,
                 my_id, nbbateaux=None, history=None):
        self.x = x
        self.y = y
        self.id = id
        self.orientation = orientation
        self.vitesse = vitesse
        self.rhum = rhum
        self.est_a_moi = est_a_moi
        self.my_id = my_id

        if est_a_moi:
            self.ymin = int(21 / nbbateaux) * self.my_id
            self.ymax = int(21 / nbbateaux) * (self.my_id + 1) - 1
            self.history = history
            self.wx = self.wy = None
            self.override = 0
            self.shot = False

    @property
    def front_position(self):
        if self.y % 2:  # impair
            offsetx = [1, 1, 0, -1, 0, 1]
            offsety = [0, -1, -1, 0, 1, 1]
        else:
            offsetx = [1, 0, -1, -1, -1, 0]
            offsety = [0, -1, -1, 0, 1, 1]
        fx = self.x + offsetx[self.orientation]
        fy = self.y + offsety[self.orientation]
        return GenericClass(x=fx, y=fy)

    def play(self, barils, cballs, enemies):
        if self.override:
            self.override -= 1
            self._move(self.history[0].wx, self.history[0].wy)

        # check for blocked
        if self._blocked(depth=DEPTH):
            if not self._threatened(cballs) and self._shoot_closest(enemies):
                debug("{} shot".format(self.id))
                pass
            else:
                debug("{} cannot shoot".format(self.id))
                self._move_around()
            return

        my_barils = [b for b in barils if Utils.belongs_to(b.y, self.ymin, self.ymax)]
        p = [(b.x, b.y) for b in my_barils]
        debug(p)
        if my_barils:
            self._move_to_closest(my_barils)
        else:
            if not self._threatened(cballs) and self._shoot_closest(enemies):
                debug("{} shot".format(self.id))
                pass
            else:
                debug("{} cannot shoot".format(self.id))
                self._move_around()
            return

    def _move(self, x, y):
        self.wx = x
        self.wy = y
        maitreDuJeu.move(self.id, x, y)

    def _move_around(self):
        destinations = OrderedDict([
            ('11', GenericClass(x=1, y=1)),
            ('119', GenericClass(x=1, y=19)),
            ('2119', GenericClass(x=21, y=19)),
            ('211', GenericClass(x=21, y=1)),
        ])
        idxs = [k for k in destinations.keys()]
        dests = [d for k, d in destinations.items()]
        prev = self.history[0]
        prevk = '{}{}'.format(prev.wx, prev.wy)
        if prevk in destinations:  # already going around, check for destination reached
            debug("{} was going around toward {} {}".format(prev.id, prev.wx, prev.wy))
            if Utils.same_position(self, GenericClass(x=prev.wx, y=prev.wy)):
                debug("{} reached {} {}".format(prev.id, prev.wx, prev.wy))
                for i in range(len(destinations)):
                    if prevk == idxs[i]:
                        nextk = idxs[(i+1) % len(destinations)]
                        next = destinations[nextk]
                        debug("{} no more barils/blocked {}: {} {}".format(self.id, self.vitesse, next.x, next.y))
                        self._move(next.x, next.y)
                        return
            else:
                self._move(prev.wx, prev.wy)
        else:
            self._move_to_closest(dests)
            debug("no more barils/blocked {} {}: {} {}".format(self.id, self.vitesse, self.wx, self.wy))

    def _move_to_closest(self, items):
        items.sort(key=lambda x: Utils.distance(self, x))
        self.wanted = items[0]
        self._move(x=self.wanted.x, y=self.wanted.y)

    def _shoot_closest(self, enemies):
        enemies.sort(key=lambda x: Utils.distance(self, x))
        closest_e = enemies[0]
        if not self.history[0].shot and Utils.distance(self.front_position, closest_e) <= 10:
            maitreDuJeu.fire(self.id, closest_e.x, closest_e.y)
            self.wx = self.history[0].wx
            self.wy = self.history[0].wy
            self.shot = True
            debug("shot {} {}".format(closest_e.x, closest_e.y))
            return True
        else:
            return False

    def _blocked(self, depth=1):
        lres = [
            self.x == h.x and self.y == h.y
            and self.orientation == h.orientation
            for h in self.history
        ]
        for r in lres:
            if not r:
                return False
        res = len(lres) >= depth
        if res:
            debug("! {} blocked !".format(self.id))
        return True if len(lres) >= depth and self.vitesse == 0 else False

    def _threatened(self, cballs):
        threats = [b for b in cballs if Utils.distance(self, b) <= 1]
        res = len(threats) != 0
        if res:
            debug("! {} threatened !".format(self.id))
        return res


class Baril(object):
    def __init__(self, id, x, y, rhum):
        self.x = x
        self.y = y
        self.id = id
        self.rhum = rhum


class MineManager(object):
    def __init__(self):
        self.count = self.prev_count = 0

    def start_tour(self):
        self.prev_count = self.count
        self.count = 0

    def one_detected(self):
        self.count += 1

    def take_a_detour(self):
        raise NotImplementedError


class CannonBall(object):
    def __init__(self, x, y, sender_id, nb_turns):
        self.x = x
        self.y = y
        self.sender_id = sender_id
        self.nb_turns = nb_turns


class GenericClass(object):
    def __init__(self, **kwargs):
        for k, arg in kwargs.items():
            setattr(self, k, arg)


class MaitreDuJeu:
    def __init__(self):
        # tableau contenant toutes les infos connues a propos des entites du jeu
        self.my_boats = None
        self.enemy_boats = None
        self.barrels = None
        self.cballs = None
        self.mine_manager = MineManager()
        # the number of remaining ships
        self.nb_bateaux = None
        # the number of entities (e.g. ships, mines or cannonballs)
        self.nb_entites = None
        self.has_played = None

        self.history = []

    def debuter_tour(self):
        self.my_boats = []
        self.enemy_boats = []
        self.barrels = []
        self.cballs = []
        self.has_played = []
        # self.mine_manager.start_tour()
        self.nb_bateaux = int(input())
        self.nb_entites = int(input())

    def analyser_plateau(self):
        debug('- analyse')
        for i in range(self.nb_entites):
            self._analyser_entite()
        self.my_boats.sort(key=lambda x: x.id)
        # self.barrels.sort(key=lambda x: distance(self.bateaux[0], x))

    def jouer_tous_bateaux(self):
        debug('- jeu')
        # if self.mine_manager.count:
        #     already FIRED
        # return

        for b in self.my_boats:
            b.play(self.barrels, self.cballs, self.enemy_boats)
            debug("{} is playing {} {}".format(b.id, b.wx, b.wy))
        # for i in range(self.nb_bateaux):
        #     self._jouer_un_bateau(i)
        # self.moi = self.bateaux[0]

    def finir_tour(self):
        debug('- fin')
        if len(self.history) == HDEPTH:
            self.history.pop()
        self.history.insert(0, GenericClass(my_boats=self.my_boats))

    def fire(self, id, x, y):
        if id in self.has_played:
            error("ERR {} wanted to fire at{} {} but has played already".format(id, x, y))
            raise Exception
        else:
            self.has_played.append(id)
            Utils.fire(x, y)

    def move(self, id, x, y):
        if id in self.has_played:
            error("ERR {} wanted to go to {} {} but has played already".format(id, x, y))
            raise Exception
        else:
            self.has_played.append(id)
            Utils.move(x, y)

    def _analyser_entite(self):
        id, type, x, y, arg_1, arg_2, arg_3, arg_4 = input().split()
        # debug(type)
        id = int(id)
        x = int(x)
        y = int(y)
        arg_1 = int(arg_1)
        arg_2 = int(arg_2)
        arg_3 = int(arg_3)
        arg_4 = int(arg_4)

        if type == 'SHIP':
            if arg_4:
                hist = [
                    [b for b in self.history[i].my_boats if b.id == id][0]
                    for i in range(Utils.min(DEPTH, len(self.history)))
                ]
                self.my_boats.append(Bateau(id, x, y, arg_1, arg_2, arg_3, arg_4,
                                            len(self.my_boats), self.nb_bateaux, hist))
            else:
                self.enemy_boats.append(Bateau(id, x, y, arg_1, arg_2, arg_3, arg_4,
                                               6660 + len(self.enemy_boats)))
        elif type == 'BARREL':
            self.barrels.append(Baril(id, x, y, arg_1))
        # elif type == 'MINE':
        #     self.mine_manager.one_detected()
        elif type == 'CANNONBALL':
            self.cballs.append(CannonBall(x, y, sender_id=arg_1, nb_turns=arg_2))
        else:
            return
            # TODO raise Exception('Type de protagoniste inconnu: ' + type)


# ---------- VARIABLE VIVANT TOUT AU LONG DU JEU ------------

maitreDuJeu = MaitreDuJeu()

# ---------- GAME LOOP ------------

while True:
    maitreDuJeu.debuter_tour()

    maitreDuJeu.analyser_plateau()

    maitreDuJeu.jouer_tous_bateaux()

    maitreDuJeu.finir_tour()
