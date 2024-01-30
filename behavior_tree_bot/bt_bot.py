#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')
    '''
    offensive_plan = Sequence(name='Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    attack = Action(attack_weakest_enemy_planet)
    offensive_plan.child_nodes = [largest_fleet_check, attack]

    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(most_profitable)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]
    '''

    defensive_strat = Sequence(name='Defensive Strategy')
    my_planet = Check(if_my_planet_available)
    threat_available = Check(threats)
    defense_against_threat = Action(defending)
    defensive_strat.child_nodes = [my_planet, threat_available, defense_against_threat]

    early_game = Sequence(name='Early Game Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    most_profitable_planet = Action(most_profitable)
    early_game.child_nodes =  [neutral_planet_check, most_profitable_planet]

    attack_spreader = Sequence(name='Spread Offensive Strategy')
    spread_identifier = Check(spread_attack)
    attack_attacker = Action(attack_multiple)
    attack_spreader.child_nodes = [spread_identifier, attack_attacker]

    attack = Sequence(name='Offensive Strategy')
    enemy_planet_check = Check(if_enemy_planet_available)
    attack_profitable_planet = Action(attack_profitable)
    attack.child_nodes = [enemy_planet_check, attack_profitable_planet]

    #needed a defensive strategy, and offensive strategy
    root.child_nodes = [defensive_strat, attack_spreader, early_game, attack]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
