import sys
import math
import pandas as pd


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


def mafcbateau(x, y, aller_droite):
    def avancer_x(x, aller_droite):
        if aller_droite:
            x += 1
        else:
            x -= 1
        return x

    x = avancer_x(x, aller_droite)

    if x == 23 or x == -1:
        y += 1
        aller_droite = not aller_droite
        x = avancer_x(x, aller_droite)

    return {
        'x': x,
        'y': y,
        'aller_droite': aller_droite
    }


curr_pos = {
    'x': 0,
    'y': 0,
    'aller_droite': True
}
protagonistes = pd.DataFrame(columns=[
    'type',
    'x', 'y',
    'orientation',
    'vitesse',
    'rhum',
    'est_a_moi'
])
barrels = []


def obtenir_infos_protagoniste(input, protagonistes):
    id, type, x, y, arg_1, arg_2, arg_3, arg_4 = input.split()
    id = int(id)
    x = int(x)
    y = int(y)
    arg_1 = int(arg_1)
    arg_2 = int(arg_2)
    arg_3 = int(arg_3)
    arg_4 = int(arg_4)

    if type == 'SHIP':
        infos = pd.Series({
            'type': type,
            'x': x, 'y': y,
            'orientation': arg_1,
            'vitesse': arg_2,
            'rhum': arg_3,
            'est_a_moi': arg_4
        })
    elif type == 'BARREL':
        infos = pd.Series({
            'type': type,
            'x': x, 'y': y,
            'rhum': arg_1
        })
    else:
        raise Exception('Type de protagoniste inconnu: ' + type)

    protagonistes.loc[id] = infos
    # print("protagonistes: \n{}".format(infos), file=sys.stderr)
    return id


# game loop
while True:
    my_ship_count = int(input())  # the number of remaining ships
    entity_count = int(input())  # the number of entities (e.g. ships, mines or cannonballs)

    # recuperation des infos sur les protagonistes
    for i in range(entity_count):
        mon_id = obtenir_infos_protagoniste(input(), protagonistes)

    # chacun de nos bateaux joue
    for i in range(my_ship_count):
        # init to start
        # if not curr_pos['x'] and not curr_pos['y']:
        if not curr_pos['x'] and not curr_pos['y']:
            curr_pos['x'] = protagonistes.loc[mon_id, 'x']
            curr_pos['y'] = protagonistes.loc[mon_id, 'y']

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        # print("before...{}".format(curr_pos), file=sys.stderr)
        # decide where to go
        # curr_pos = mafcbateau(**curr_pos)
        # print("after...{}".format(curr_pos), file=sys.stderr)

        # Any valid action, such as "WAIT" or "MOVE x y"
        # print('MOVE {x} {y}'.format(x=curr_pos['x'], y=curr_pos['y']))

        # find a barrel
        if len(barrels) == 0:
            barrels = protagonistes.loc[protagonistes.type == 'BARREL']

        moi = protagonistes.loc[protagonistes.est_a_moi == 1]

        reached_barrel = barrels.loc[barrels.x == moi.iloc[0].x].loc[barrels.y == moi.iloc[0].y].index
        if len(reached_barrel):
            print("dbg: \n{}".format(barrels.loc[reached_barrel]), file=sys.stderr)
            barrels.drop(reached_barrel, inplace=True)

        barrel = barrels.iloc[0]

        print("barrel: \n{}".format(barrel), file=sys.stderr)
        print('MOVE {x} {y}'.format(x=barrel.x, y=barrel.y))
