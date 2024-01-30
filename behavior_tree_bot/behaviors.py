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
        if instances[1] < instances[3] and (instances[2].ID, instances[4].ID) not in fleet_in_flight:
            return issue_order(state, instances[2].ID, instances[4].ID, instances[1])
    return False

def defending(state):
    fleet_in_flight = [fleet.destination_planet for fleet in state.my_fleets()]
    enemy_moves = state.enemy_fleets()
    allied_planets = state.my_planets()

    biggest_threat = []
    strongest_growth = max(state.my_planets(), key=lambda t: t.growth_rate, default=None).growth_rate
    for instances in enemy_moves:
      target_planet = None
      for planets in allied_planets:
          if planets.ID == instances.destination_planet:
              target_planet = planets
              break
      if target_planet != None and target_planet.growth_rate == strongest_growth:
          biggest_threat.append(instances)

    
    moves = []

    for enemy in biggest_threat:
        #calculate the number of ships needed to fend off a fleet assault
        destination = None
        for planets in allied_planets:
            if planets.ID == instances.destination_planet:
                destination = planets
                break
        if destination == None: 
            # should never happen but there for safety
            continue
        for planets in state.my_planets():
            if enemy.turns_remaining < state.distance(planets.ID, enemy.destination_planet):
                #if the enemy ship arrives first
                ships_needed = 1 + destination.growth_rate * abs((state.distance(planets.ID, destination.ID) - enemy.turns_remaining))
                ships_left = planets.num_ships
                moves.append((ships_needed, planets, ships_left, destination))
            else:
                #if the enemy ship arrives second
                ships_needed = (destination.num_ships + 1) + max((enemy.num_ships - (destination.growth_rate * (enemy.turns_remaining - state.distance(planets.ID, destination.ID)))), 0)
                ships_left = planets.num_ships
                moves.append((ships_needed, planets, ships_left, destination))

    moves = sorted(moves, reverse=True)
    
    for instances in moves:
        if instances[0] < instances[2] and instances[3].ID not in fleet_in_flight:
            return issue_order(state, instances[1].ID, instances[3].ID, instances[0])
    return False


def attack_profitable(state):
    fleet_in_flight = [fleet.destination_planet for fleet in state.my_fleets()]
    enemy_planets = state.enemy_planets()

    our_planets = state.my_planets()

    statistics = []
    for planets in our_planets:
        for enemy in enemy_planets:
            #calculate the number of ships needed to reclaim a captured planet
            ships_needed = 1 + enemy.num_ships + (enemy.growth_rate * state.distance(planets.ID, enemy.ID))
            ships_left = planets.num_ships
            if ships_needed < ships_left: 
                statistics.append((enemy.growth_rate, ships_needed, planets, ships_left, enemy))

    statistics = sorted(statistics, key=custom_sort)
    
    for instances in statistics:
        if instances[4].ID not in fleet_in_flight:
            return issue_order(state, instances[2].ID, instances[4].ID, instances[1])
    return False

def attack_multiple(state):
    fleet_in_flight = [fleet.destination_planet for fleet in state.my_fleets()]
    enemy_planets = state.enemy_planets()
    enemy_moves = state.enemy_fleets()

    our_planets = state.my_planets()
    attack_targets = []
    for instances in enemy_moves:
        target_planet = None
        for planets in enemy_planets:
            if planets.ID == instances.source_planet:
                target_planet = planets
                break
        if target_planet != None:
            attack_targets.append(target_planet)

    logging.info(attack_targets)
    statistics = []
    for planets in our_planets:
        for enemy in attack_targets:
            #calculate the number of ships needed to intercept
            logging.info(enemy)
            ships_needed = 1 + enemy.num_ships + (enemy.growth_rate * state.distance(planets.ID, enemy.ID))
            ships_left = planets.num_ships
            if ships_needed < ships_left: 
                statistics.append((enemy.growth_rate, ships_needed, planets, ships_left, enemy))

    statistics = sorted(statistics, key=custom_sort)
    for instances in statistics:
        if instances[4].ID not in fleet_in_flight:
            return issue_order(state, instances[2].ID, instances[4].ID, instances[1])
    return False