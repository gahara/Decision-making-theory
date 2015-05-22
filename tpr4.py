#!/usr/bin/env python3
import random

class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return repr(self.__dict__)

class Tank(object):
    spa = 0.1 #speed per acceleration
    sps = 1.0 #ster per speed
    max_h = 1.0 #max health
    min_h = 0.01 #min health
    max_ad = 3.0 #max attack distance
    ctrl = 10.0

    min_sl = 0.1 #min speed loss
    min_hl = 0.05 #min health loss

    sa_s_sl = 0.95 #successfull attack self speed loss
    sa_c_sl = 0.5 #successfull attack competitor speed loss
    sa_s_hl = 0.95 #successfull attack self speed loss
    sa_c_hl = 0.7 #successfull attack competitor speed loss

    fa_sl = 0.95 #failed attack self speed loss
    min_sa_p = 0.2 #minimal sucessfull atack probability

    behaviours = {
            'nearest': lambda _, competitors: sorted(competitors, key=lambda r: r.dist),
            'highest_max_speed': lambda _, competitors: sorted(competitors, key=lambda r: r.tank.max_speed, reverse=True),
            'highest_cur_speed': lambda _, competitors: sorted(competitors, key=lambda r: r.tank.cur_speed, reverse=True),
            'highest_acceleration': lambda _, competitors: sorted(competitors, key=lambda r: r.tank.acceleration, reverse=True),
    }

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.cur_speed = 0
        self.health = self.max_h

    def damage(self):
        return self.strength * self.cur_speed * self.health * self.control
    def endure(self):
        return self.durability * self.cur_speed * self.health * self.control
    def sa_prob(self, competitor):
        my_damage, competitior_endurance = self.damage(), competitor.tank.endure()
        return (1 - competitor.dist / self.max_ad) * ((my_damage - competitior_endurance) / (my_damage + competitior_endurance + 1e-5))
    def attack(self, competitor):
        sucess_probability = self.sa_prob(competitor)
        if sucess_probability <= self.min_sa_p:
            return True
        if random.random() < sucess_probability:
            self_speed_loss = min(self.cur_speed, max(self.cur_speed * (1 - self.sa_s_sl), self.min_sl))
            self.cur_speed -= self_speed_loss

            competitor_speed_loss = min(competitor.tank.cur_speed, max(competitor.tank.cur_speed * (1 - self.sa_c_sl), self.min_sl))
            competitor.tank.cur_speed -= competitor_speed_loss

            self_health_loss = min(self.health, max(self.health * (1 - self.sa_s_hl), self.min_hl))
            self.health -= self_health_loss

            competitor_health_loss = min(competitor.tank.health, max(competitor.tank.health * (1 - self.sa_c_hl), self.min_hl))
            competitor.tank.health -= competitor_health_loss

            print('  -- "{}" attacked "{}" (speed loss = {:.2f}, health loss={:.2f})'.format(
                  self.name, competitor.tank.name, competitor_speed_loss, competitor_health_loss))
            return True
        else:
            self_speed_loss = min(self.cur_speed, max(self.cur_speed * (1 - self.fa_sl), self.min_sl))
            self.cur_speed -= self_speed_loss
            #print('  --- "{}" failed to attack "{}" (speed loss={:.2f}, prob={:.2f})'.format(
            #      self.name, competitor.tank.name, self_speed_loss, sucess_probability))
            return False

    def is_alive(self):
        return self.health > self.min_h

    def make_move_step(self, is_turn):
        if not self.is_alive():
            return 0

        if is_turn:
            self.cur_speed *= self.control / self.ctrl
        elif self.cur_speed < self.max_speed:
            old_speed = self.cur_speed
            self.cur_speed = min(self.max_speed, self.cur_speed + self.acceleration * self.spa)
        return self.cur_speed * self.sps

    def make_attack_step(self, competitors):
        if not self.is_alive():
            return
        competitors_can_attack = [r for r in competitors if r.dist < self.max_ad]
        competitors_to_attack = self.behaviours[self.at_strategy](self, competitors_can_attack)
        for competitor in competitors_to_attack:
            if not self.attack(competitor):
                break

    def state_to_str(self):
        if not self.is_alive():
            return 'Blown up'
        return 'speed={:.2f}, health={:.2f}, damage={:.2f}, endurance={:.2f}'.format(
                self.cur_speed, self.health, self.damage(), self.endure())
    def __repr__(self):
        return 'Tank(name={}, cur_sp={:.2f}, h={:.2f})'.format(self.name, self.cur_speed, self.health)

class Battle(object):
    TURNS_DENSITY = 0.1

    def __init__(self, tanks, track_len):
        self._tanks = tanks
        random.shuffle(self._tanks)
        self._track_len = track_len
        self._tank_positions = [0 for _ in range(track_len)]
    def make_step(self):
        is_turn = random.random() < self.TURNS_DENSITY
        if is_turn:
            print('turn on the track!')

        for i, tank in enumerate(self._tanks):
            self._tank_positions[i] += tank.make_move_step(is_turn)

        for i, tank in enumerate(self._tanks):
            distances = map(lambda p: abs(self._tank_positions[i] - p), self._tank_positions)
            competitors = tuple(Bunch(tank=c, dist=d, pos=p) for c, d, p in zip(self._tanks, distances, self._tank_positions) if c != tank)
            tank.make_attack_step(competitors)

        return all(pos < self._track_len for pos in self._tank_positions) and any(tank.is_alive() for tank in self._tanks)
    def get_winner(self):
        return max(zip(self._tanks, self._tank_positions), key=lambda v: v[1])[0]
    def print_state(self):
        for i, (tank, pos) in enumerate(sorted(zip(self._tanks, self._tank_positions), key=lambda v: v[1], reverse=True)):
            print('{}: {:.1f}/{} passed, {}: {}'.format(i + 1, min(self._track_len, pos), self._track_len, tank.name, tank.state_to_str()))

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        random.seed(int(sys.argv[1]))
    tanks = [
#        Tank(name='Jaguar C-X75', max_speed=8.6, acceleration=8.5, control=8.3, strength=4.2, durability=3.8),
        Tank(name='T34', max_speed=8.4, acceleration=8.1, control=4.8, strength=2.3, durability=3.6, at_strategy='nearest'),
        Tank(name='T72', max_speed=6.1, acceleration=6.9, control=5.7, strength=7.4, durability=4.0, at_strategy='highest_acceleration'),
        Tank(name='Matilda', max_speed=5.6, acceleration=7.8, control=6.2, strength=7.3, durability=4.8, at_strategy='highest_max_speed'),
        Tank(name='Sherman', max_speed=6.0, acceleration=5.8, control=8.0, strength=6.4, durability=7.8, at_strategy='highest_max_speed'),
        Tank(name='Hellcat', max_speed=6.7, acceleration=6.6, control=6.0, strength=3.4, durability=3.0, at_strategy='highest_cur_speed'),
        Tank(name='Vickers', max_speed=4.2, acceleration=8.0, control=3.9, strength=6.7, durability=4.2, at_strategy='highest_acceleration'),
    ]

    battle = Battle(tanks=tanks, track_len=100)

    battle.print_state()
    print('')
    i = 0
    r = True
    while r:
        i += 1
        print('Step {}\n'.format(i))
        r = battle.make_step()
        battle.print_state()
        print('')
    print('Winner: {}'.format(battle.get_winner().name))
    import os
    os.system('say "Tank {} won the battle!"'.format(battle.get_winner().name))