import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
    
def custom_sort(item):
    return (-item[0], item[1], item[2], item[3], item[4])

def most_profitable(state):
    # planets you can win
    statistics = []
    fleet_in_flight = [(fleet.source_planet, fleet.destination_planet) for fleet in state.my_fleets()]
    neutral_planets = state.neutral_planets()
    
    our_planets = state.my_planets()
    enemy_moves = state.enemy_fleets()
    enemy_planets = [planets.destination_planet for planets in enemy_moves]

    for planets in our_planets:
        for unclaimed in neutral_planets:
            if unclaimed.ID in enemy_planets:
                #assume that there's only 1 enemy fleet going to the planet
                enemy = None
                for instances in enemy_moves:
                    if instances.destination_planet == unclaimed.ID:
                        enemy = instances
                if enemy.turns_remaining < state.distance(planets.ID, unclaimed.ID):
                    #if the enemy ship arrives first
                    ships_needed = abs(unclaimed.num_ships - enemy.num_ships) + unclaimed.growth_rate * abs((state.distance(planets.ID, unclaimed.ID) - enemy.turns_remaining))
                    ships_left = planets.num_ships
                    statistics.append((unclaimed.growth_rate, ships_needed + 1, planets, ships_left, unclaimed))
                else:
                    #if the enemy ship arrives second
                    ships_needed = (unclaimed.num_ships + 1) + max((enemy.num_ships - (unclaimed.growth_rate * (enemy.turns_remaining - state.distance(planets.ID, unclaimed.ID)))), 0)
                    ships_left = planets.num_ships
                    statistics.append((unclaimed.growth_rate, ships_needed, planets, ships_left, unclaimed))
            else:
                #if there's no enemy ship approaching
                ships_left = planets.num_ships
                statistics.append((unclaimed.growth_rate, unclaimed.num_ships + 1, planets, ships_left, unclaimed))

    statistics = sorted(statistics, key=custom_sort)
    for instances in statistics:
        if instances[1] <= instances[3] and (instances[2].ID, instances[4].ID) not in fleet_in_flight:
            return issue_order(state, instances[2].ID, instances[4].ID, instances[1])
    return False
    
    '''
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
    '''