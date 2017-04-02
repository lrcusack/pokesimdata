from loggable import Loggable
import pandas as pd
import numpy as np
import sqlite3
from time import time
from tinydb import TinyDB


def load_type_modifier_table_from_db():
    """load type modifier table from https://www.math.miami.edu/~jam/azure/compendium/typechart.htm,
    with added fields for Dark, Steel and Fairy"""
    db = sqlite3.connect("pokedex.sqlite")
    tmt = pd.read_sql_query("SELECT * FROM TypeModifier", db, index_col="index")
    db.close()
    # logging.debug("Type Modifier Table Database Loaded:")
    # logging.debug(tmt)
    return tmt


def load_pokemon_table_from_db():
    """load pokemon table from kaggle dataset"""
    db = sqlite3.connect("pokedex.sqlite")
    poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")
    db.close()
    # logging.debug("Pokemon Database Loaded (sample shown):")
    # logging.debug(poketable.sample(10))
    return poketable


class BigFullFactorial(Loggable):
    """Class to define a full factorial experimental design with too many cases for storing them as a data frame"""

    def __init__(self, levels):
        self.levels = levels
        ncases = np.prod(levels)
        self.idxrange = range(ncases)
        self.dbg('levels: ' + str(levels) + ' -- number of cases: ' + str(ncases))

    def get_case_from_index(self, idx):
        """Method for defining cases based on an index
        like a de-hash function"""
        if idx not in self.idxrange:
            return None
        remainder = idx
        case = []
        for i in range(len(self.levels)):
            divisor = np.prod(self.levels[i:]) / self.levels[i]
            case.append(int(remainder // divisor))
            remainder %= divisor
        self.dbg('index: ' + str(idx) + ' -- case: ' + str(case))
        return case

    def get_index_from_case(self, case):
        """Method for defining an index for a given case
        like a hash function"""
        result_idx = 0
        for idx in range(len(case)):
            if case[idx] not in range(self.levels[idx]):
                return None
            result_idx += case[idx] * np.prod(self.levels[idx:]) / self.levels[idx]
        result_idx = int(result_idx)
        self.dbg('case: ' + str(case) + ' -- index: ' + str(result_idx))
        return result_idx


class Pokemon(Loggable):
    """ This class defines a Pokemon """
    standardLevel = 50
    standardAttackPower = 30
    # average from genIII up on http://bulbapedia.bulbagarden.net/wiki/Individual_values
    standardIV = 15
    # even distribution of EV across stats from http://bulbapedia.bulbagarden.net/wiki/Effort_values
    standardEV = round(510/6)
    typeModifierTable = load_type_modifier_table_from_db()

    specialTypes = ['Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Psychic']
    physicalTypes = ['Normal', 'Fighting', 'Flying', 'Ground',
                     'Rock', 'Bug', 'Poison', 'Ghost', 'Dragon', 'Dark', 'Steel', "Fairy"]
    allTypes = set(specialTypes + physicalTypes)

    def to_dict(self):
        return {'name': self.name, "hp": self.hp, "maxhp": self.maxhp, "atk": self.attack, "def": self.defense,
                "spatk": self.spatk, "spdef": self.spdef, "speed": self.speed}

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)

    @classmethod
    def calculate_stat(cls, statbase, level=None, iv=None, ev=None, statname=''):
        if not level:
            level = cls.standardLevel
        if not iv:
            iv = cls.standardIV
        if not ev:
            ev = cls.standardEV
        if statname == 'hp':
            modifier = level + 10
        else:
            modifier = 5
        stat = int(((2 * statbase) + iv + int(ev / 4)) * level / 100 + modifier)
        cls.dbg(statname +
                ' -- base: ' + str(statbase) +
                ' -- iv: ' + str(iv) +
                ' -- ev: ' + str(ev) +
                ' -- level: ' + str(level) +
                ' -- result: ' + str(stat))
        return stat

    def __init__(self, name, type1, type2, hp,
                 attack, defense, spatk, spdef, speed,
                 level=0, iv=0, ev=0):
        """ Construct a Pokemon

        Keyword arguments:
        name -- name of the Pokemon
        type1 -- type of Pokemon (e.g. Grass)
        type2 -- second type of Pokemon ("" if pokemon has one type)
        hp -- number of hit points the pokemon has
        attack -- attack stat
        defense -- defense stat
        spatk -- special attack stat
        spdef -- special defense stat
        speed -- speed stat
        """
        if level == 0:
            level = self.standardLevel
        if iv == 0:
            iv = self.standardIV
        if ev == 0:
            ev = self.standardEV
        self.name = name
        self.type = [x for x in [type1, type2] if x in self.allTypes]
        self.maxhp = Pokemon.calculate_stat(hp, level, iv, ev, statname='hp')
        self.hp = self.maxhp
        self.attack = Pokemon.calculate_stat(attack, level, iv, ev, statname='attack')
        self.defense = Pokemon.calculate_stat(defense, level, iv, ev, statname='defense')
        self.spatk = Pokemon.calculate_stat(spatk, level, iv, ev, statname='spatk')
        self.spdef = Pokemon.calculate_stat(spdef, level, iv, ev, statname='spdef')
        self.speed = Pokemon.calculate_stat(speed, level, iv, ev, statname='speed')
        self.level = level

        self.dbg(str(self))

    @classmethod
    def from_data_frame(cls, poketable):
        """Create a list of pokemon from a dataframe describing the pokemon
        this function does not work if you want to repeat pokemon..."""
        pokemonlist = []
        if isinstance(poketable, pd.DataFrame):
            for i in poketable.index:
                name = poketable.name[i]
                type1 = poketable.type1[i]
                type2 = poketable.type2[i]
                hp = poketable.hp[i]
                attack = poketable.attack[i]
                defense = poketable.defense[i]
                spatk = poketable.spatk[i]
                spdef = poketable.spdef[i]
                speed = poketable.speed[i]
                pokemonlist.append(cls(name, type1, type2, hp, attack, defense, spatk, spdef, speed))
        else:
            poketable = poketable.to_dict()
            name = poketable["name"]
            type1 = poketable["type1"]
            if "type2" in poketable:
                type2 = poketable["type2"]
            else:
                type2 = ''
            hp = poketable["hp"]
            attack = poketable["attack"]
            defense = poketable["defense"]
            spatk = poketable["spatk"]
            spdef = poketable["spdef"]
            speed = poketable["speed"]
            pokemonlist = cls(name, type1, type2, hp, attack, defense, spatk, spdef, speed)
        cls.dbg(str(pokemonlist))
        return pokemonlist

    @classmethod
    def create_pokemon_generator(cls, pokemon_table):
        """This returns a function that takes a list of (possibly non-unique) indices for the given poketable
        returns a list of those pokemon"""
        return lambda x: [cls.from_data_frame(pokemon_table.loc[i]) for i in x] if isinstance(x, list) \
            else cls.from_data_frame(pokemon_table.loc[x])

    def is_ko(self):
        """Returns true if this pokemon is knocked out, false otherwise"""
        ko = self.hp == 0
        if ko:
            self.dbg(self.name + ' ' + str(ko))
        return ko

    def deterministically_inferior_to(self, other):
        """If this pokemon has the same types and strictly lower stats, return true"""
        inferior = \
            ((set(self.type) == set(other.type))
             and (self.maxhp < other.maxhp)
             and (self.attack < other.attack)
             and (self.defense < other.defense)
             and (self.spatk < other.spatk)
             and (self.spdef < other.spdef)
             and (self.speed < other.speed))
        self.dbg(self.name + ' inferior to ' + other.name + ': ' + str(inferior))
        return inferior

    def take_damage(self, damage):
        """apply damage, make sure lowest hp is 0"""
        newhp = max(0, self.hp - damage)
        self.dbg(self.name + ' takes ' + str(damage) + ' hp reduced to ' + str(newhp))
        self.hp = newhp

    def recover(self):
        self.dbg(self.name + ' recovered')
        self.hp = self.maxhp

    @staticmethod
    def damage_equation(a, b, c, d, x, y, z):
        """This algorithm is based on https://www.math.miami.edu/~jam/azure/compendium/battdam.htm"""
        return int((((((((((2 * a // 5 + 2) * b) * c) // d) // 50) + 2) * x) * y) * z) // 255)

    def calculate_damage(self, other_pokemon):
        """Calculate the damage this pokemon can do to other_pokemon"""
        # Set independent values (pokemon-agnostic)
        """# use random critical hit
        if np.random.rand() < .05:
            critical_hit = 1
        else:
            critical_hit = 0
        """
        # no critical hit
        critical_hit = 0

        a = self.level * (1 + critical_hit)  # level of pokemon
        c = Pokemon.standardAttackPower  # power of attack
        x = 1.5
        """# use true random attack value
        Z = int(217 + (255 - 217) * np.random.rand())  # random value  between 217 and 255
        """
        # use average attack value
        z = round((217+255)/2)
        damage = [0] * len(self.type)
        # calculate estimated attack score for each attack type
        for idx, attackType in enumerate(self.type):
            # calculate type modifier y
            y = 1
            for defenseType in other_pokemon.type:
                # lookup type modifier
                y *= Pokemon.typeModifierTable[defenseType][attackType]

            # if this attack type is a physical attack, use attack stat
            if attackType in Pokemon.physicalTypes:
                b = self.attack  # attack score
                d = other_pokemon.defense  # defense score
            else:  # otherwise use special attack
                b = self.spatk
                d = other_pokemon.spdef

            # calculate damage for this attack type
            damage[idx] = Pokemon.damage_equation(a, b, c, d, x, y, z)

            self.dbg(self.name + ' evaluates ' + attackType + ' attack against ' + other_pokemon.name +
                     " A: " + str(a) + " B: " + str(b) + " C: " + str(c) + " D: " + str(d) +
                     " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + ' damage: ' + str(damage[idx]))

        # Add entry for non-same-type physical attack
        x = 1  # no STAB
        b = self.attack  # attack score
        d = other_pokemon.defense  # defense score
        y = 1  # no type modifier
        default_damage = Pokemon.damage_equation(a, b, c, d, x, y, z)
        self.dbg(self.name + ' evaluates attack against ' + other_pokemon.name +
                 " A: " + str(a) + " B: " + str(b) + " C: " + str(c) + " D: " + str(d) +
                 " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + ' damage: ' + str(default_damage))
        damage.append(default_damage)
        # return maximum damage
        return max(damage)

    def do_attack(self, other_pokemon):
        """This pokemon attacks other_pokemon"""
        damage = self.calculate_damage(other_pokemon)
        self.dbg(self.name + " attacks " + other_pokemon.name + " for " + str(damage) + " damage")
        other_pokemon.take_damage(damage)

        return damage


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


class PokeDataSimulation(Loggable):
    def __init__(self, idxrange, simname=''):
        self.results = []
        self.idxrange = idxrange
        if simname == '':
            self.simname = "NewSim"
        else:
            self.simname = simname

    def setup_case(self, caseidx):
        return {}

    def run_case(self, case):
        if not case:
            return None
        tic = time()
        t1 = case['t1']
        t2 = case['t2']
        t1win = t1.fight(t2)
        if t1win:
            record = {'Winner': t1.to_dict_list(), 'Loser': t2.to_dict_list()}
            winner = str(t1.to_str_list())
            loser = str(t2.to_str_list())
        else:
            record = {'Winner': t2.to_dict_list(), 'Loser': t1.to_dict_list()}
            winner = str(t2.to_str_list())
            loser = str(t1.to_str_list())
        toc = time()
        self.info(winner + ' beat ' + loser + ' in ' + str(toc-tic) + 's')
        return record

    def record_result(self, result):
        if result:
            self.results.append(result)

    def run_simulation(self):
        tic = time()
        self.results = []
        for i in self.idxrange:
            self.record_result(self.run_case(self.setup_case(i)))
        toc = time()
        telapsed = toc - tic
        self.info("sim time: " + str(telapsed) + 's')
        self.info("avg time per case: " + str(telapsed/(len(self.idxrange)**2)))

    def save_results_to_tinydb(self, tinydbfname='PokeDataSimResults.json'):
        tic = time()
        tdb = TinyDB(tinydbfname)
        tdb.purge_table(self.simname)
        results_table = tdb.table(name=self.simname)
        results_table.insert_multiple(self.results)
        toc = time()
        self.info("db time: " + str(toc-tic) + 's')


class FullFactPokeDataSim(PokeDataSimulation):
    def __init__(self, pokemon_indices, simname="", n_pokemon_team=1):
        experiment = BigFullFactorial([len(pokemon_indices)] * n_pokemon_team * 2)
        super().__init__(experiment.idxrange, simname)

        self.pokemon_indices = pokemon_indices
        self.index_lookup = pd.DataFrame(self.pokemon_indices, columns=["PokemonIdx"])
        self.experiment = experiment
        self.idxrange = self.experiment.idxrange
        self.n_pokemon_team = n_pokemon_team
        self.pokegen = Pokemon.create_pokemon_generator(load_pokemon_table_from_db())

    def setup_case(self, caseidx):
        case = self.experiment.get_case_from_index(caseidx)
        caset1 = case[:self.n_pokemon_team]
        caset2 = case[self.n_pokemon_team:]
        if np.array_equal(caset1, caset2):
            return None  # trainer 1 == trainer 2, no point in running
        elif self.experiment.get_index_from_case(caset2 + caset1) < caseidx:
            return None  # Trainer 2 vs trainer 1 has already been simulated
        else:
            t1idx = list(self.index_lookup.loc[caset1, 'PokemonIdx'])
            t2idx = list(self.index_lookup.loc[caset2, 'PokemonIdx'])

            return {'t1': Trainer(self.pokegen(t1idx)), 't2': Trainer(self.pokegen(t2idx))}
