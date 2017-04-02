from loggable import Loggable
from Pokemon import Pokemon
import numpy as np


class Trainer(Loggable):
    """ This class defines a Trainer """

    def __str__(self):
        return str(self.pokemon)

    def __repr__(self):
        return str(self)

    def to_dict_list(self):
        dl = []
        for p in self.pokemon:
            dl.append(p.to_dict())
        return dl

    @classmethod
    def from_dict_list(cls, dict_list, calculate_stat):
        pokemon = []
        for d in dict_list:
            pokemon.append(Pokemon.from_dict(d, calcstat=calculate_stat))
        return cls(pokemon)

    def compare(self, other):
        match = True
        if len(self.pokemon) == len(other.pokemon):
            for i in range(len(self.pokemon)):
                match = match and self.pokemon[i].compare(other.pokemon[i])
        else:
            match = False
        return match

    def to_str_list(self):
        sl = []
        for p in self.pokemon:
            sl.append(p.name)
        return sl

    def __init__(self, pokemonlist):
        """ Construct a Trainer

        Keyword arguments:
        pokemon -- list of Pokemon objects
        """
        if not isinstance(pokemonlist, list):
            pokemonlist = [pokemonlist]
        self.pokemon = pokemonlist
        self.active_pokemon_idx = 0
        self.dbg(str(self))

    def choose_next_pokemon(self):
        """Select next pokemon, ignore types and strategy"""
        self.active_pokemon_idx = -1
        for idx, p in enumerate(self.pokemon):
            if not p.is_ko():
                self.active_pokemon_idx = idx
                break
        self.dbg(str(self.active_pokemon()))

    def active_pokemon(self):
        """Return trainer's active pokemon"""
        if self.active_pokemon_idx >= 0:
            newpokemon = self.pokemon[self.active_pokemon_idx]
            return newpokemon
        else:
            self.dbg('No Active Pokemon')
            return None

    def reset(self):
        """restore all trainer's pokemons' health"""
        for p in self.pokemon:
            p.recover()
        self.active_pokemon_idx = 0
        self.dbg('Trainer reset')

    def take_turn(self, opponent_trainer):
        """ Process one 'turn' of pokemon battle """
        trainers = [self, opponent_trainer]
        # Compare speed of this trainer's active pokemon and opponent's
        if self.active_pokemon().speed > opponent_trainer.active_pokemon().speed:
            order = [0, 1]
        elif self.active_pokemon().speed < opponent_trainer.active_pokemon().speed:
            order = [1, 0]
        else:
            # choose randomly
            x = int(round(np.random.rand()))
            order = [x, 1 - x]
        if order == [0, 1]:
            self.dbg("Initiating trainer's " + self.active_pokemon().name + " attacks first")
        else:
            self.dbg("Non-initiating trainer's " + opponent_trainer.active_pokemon().name + ' attacks first')

        # in speed order, attack, check if there was a KO, and select next pokemon if there is
        for x in order:
            y = 1-x
            trainers[x].active_pokemon().do_attack(trainers[y].active_pokemon())
            if trainers[order[y]].active_pokemon().is_ko():
                self.dbg(trainers[x].active_pokemon().name + ' knocked out ' + trainers[y].active_pokemon().name)
                trainers[order[y]].choose_next_pokemon()
                if not trainers[order[y]].active_pokemon():
                    return
                else:
                    break

    def fight(self, opponent_trainer):
        """This method fights the opponent_trainer until one trainer has no conscious pokemon
        Returns True if this trainer wins and false if they lose
        """
        # while both trainers have active pokemon, take another turn
        while self.active_pokemon() and opponent_trainer.active_pokemon():
            self.take_turn(opponent_trainer)

        # decide winner
        if self.active_pokemon():
            self.dbg('Initiating trainer won')
            return True
        else:
            self.dbg('Initiating trainer lost')
            return False
