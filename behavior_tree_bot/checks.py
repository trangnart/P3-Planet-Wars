import logging

def if_neutral_planet_available(state):
    return any(state.neutral_planets())

def if_my_planet_available(state):
    return any(state.my_planets())

def if_enemy_planet_available(state):
    return any(state.enemy_planets())

def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())    

def threats(state):
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
    logging.info(biggest_threat)
    return biggest_threat != []

def spread_attack(state):
    return len(state.enemy_fleets()) >= 5