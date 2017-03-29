import pandas as pd
import numpy as np
import sqlite3
import logging

DEBUG = 10
INFO = 20
logging.basicConfig(level=DEBUG)


def load_type_modifier_table_from_db():
    """load type modifier table from https://www.math.miami.edu/~jam/azure/compendium/typechart.htm,
    with added fields for Dark, Steel and Fairy"""
    db = sqlite3.connect("pokedex.sqlite")
    tmt = pd.read_sql_query("SELECT * FROM TypeModifier", db, index_col="index")
    db.close()
    return tmt


def load_pokemon_table_from_db():
    """load pokemon table from kaggle dataset"""
    db = sqlite3.connect("pokedex.sqlite")
    poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")
    db.close()
    return poketable


class BigFullFactorial:
    """Class to define a full factorial experimental design with too many cases for storing them as a data frame"""

    def __init__(self, levels):
        self.levels = levels
        self.idxrange = range(np.prod(levels))

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
        return case

    def get_index_from_case(self, case):
        """Method for defining an index for a given case
        like a hash function"""
        result_idx = 0
        for idx in range(len(case)):
            if case[idx] not in range(self.levels[idx]):
                return None
            result_idx += case[idx] * np.prod(self.levels[idx:]) / self.levels[idx]
        return int(result_idx)


class Pokemon:
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

        return int(((2 * statbase) + iv + int(ev / 4)) * level / 100 + modifier)

    def __init__(self, name, type1, type2, hp,
                 attack, defense, spatk, spdef, speed):
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
        self.name = name
        # print("Name =", name, "| Type1 =",type1,type(type1),"| Type2 =",type2,type(type2))
        self.type = [x for x in [type1, type2] if x in self.allTypes]
        self.maxhp = Pokemon.calculate_stat(hp, statname='hp')
        self.hp = self.maxhp
        self.attack = Pokemon.calculate_stat(attack)
        self.defense = Pokemon.calculate_stat(defense)
        self.spatk = Pokemon.calculate_stat(spatk)
        self.spdef = Pokemon.calculate_stat(spdef)
        self.speed = Pokemon.calculate_stat(speed)
        self.level = Pokemon.standardLevel

    def __str__(self):
        return (self.name + ":" + " hp-" + str(self.hp) + " maxhp-" + str(self.maxhp) + " atk-" + str(self.attack) +
                " def-" + str(self.defense) + " spatk-" + str(self.spatk) + " spdef-" + str(self.spdef) +
                " speed-" + str(self.speed))

    def __repr__(self):
        return str(self)

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
        return pokemonlist

    @classmethod
    def create_pokemon_generator(cls, pokemon_table):
        """This returns a function that takes a list of (possibly non-unique) indices for the given poketable
        returns a list of those pokemon"""
        return lambda x: [cls.from_data_frame(pokemon_table.loc[i]) for i in x] if isinstance(x, list) \
            else cls.from_data_frame(pokemon_table.loc[x])

    def is_ko(self):
        """Returns true if this pokemon is knocked out, false otherwise"""
        return self.hp == 0

    def deterministically_inferior_to(self, other):
        """If this pokemon has the same types and strictly lower stats, return true"""
        return \
            ((set(self.type) == set(other.type))
             and (self.maxhp < other.maxhp)
             and (self.attack < other.attack)
             and (self.defense < other.defense)
             and (self.spatk < other.spatk)
             and (self.spdef < other.spdef)
             and (self.speed < other.speed))

    def take_damage(self, damage):
        """apply damage, make sure lowest hp is 0"""
        self.hp = max(0, self.hp - damage)

    def recover(self):
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
            if not set(Pokemon.specialTypes).intersection(attackType):
                b = self.attack  # attack score
                d = other_pokemon.defense  # defense score
            else:  # otherwise use special attack
                b = self.spatk
                d = other_pokemon.spdef

            # calculate damage for this attack type
            damage[idx] = Pokemon.damage_equation(a, b, c, d, x, y, z)
            """
            print("A: " + str(A))
            print("b: " + str(b))
            print("C: " + str(C))
            print("d: " + str(d))
            print("X: " + str(X))
            print("y: " + str(y))
            print("Z: " + str(Z))
            print("Damage: " + str(damage[idx]))
            """

        # Add entry for non-same-type physical attack
        x = 1  # no STAB
        b = self.attack  # attack score
        d = other_pokemon.defense  # defense score
        y = 1  # no type modifier
        default_damage = Pokemon.damage_equation(a, b, c, d, x, y, z)
        damage.append(default_damage)
        """
        print("A: " + str(A))
        print("b: " + str(b))
        print("C: " + str(C))
        print("d: " + str(d))
        print("X: " + str(X))
        print("y: " + str(y))
        print("Z: " + str(Z))
        print("Damage: " + str(default_damage))
        """

        # return maximum damage
        return max(damage)

    def do_attack(self, other_pokemon):
        """This pokemon attacks other_pokemon"""
        # print(self.name + " is attacking " + other_pokemon.name)
        damage = self.calculate_damage(other_pokemon)
        other_pokemon.take_damage(damage)
        """
        print(self.name + " attacks " + other_pokemon.name + " for " + str(damage) + " damage")
        if other_pokemon.is_ko() :
            print(self.name + " is knocked out!")
        """
        return damage


class Trainer:
    """ This class defines a Trainer """

    def __init__(self, pokemon):
        """ Construct a Trainer

        Keyword arguments:
        pokemon -- list of Pokemon objects
        """
        self.pokemon = pokemon
        self.active_pokemon_idx = 0

    def choose_next_pokemon(self):
        """Select next pokemon, ignore types and strategy"""
        self.active_pokemon_idx = -1
        for idx, p in enumerate(self.pokemon):
            if not p.is_ko():
                self.active_pokemon_idx = idx
                break

    def active_pokemon(self):
        """Return trainer's active pokemon"""
        if self.active_pokemon_idx >= 0:
            return self.pokemon[self.active_pokemon_idx]
        else:
            return

    def reset(self):
        """restore all trainer's pokemons' health"""
        for p in self.pokemon:
            p.recover()
        self.active_pokemon_idx = 0

    def take_turn(self, opponent_trainer):
        """ Process one 'turn' of pokemon battle """
        trainers = [self, opponent_trainer]
        # Compare speed of this trainer's active pokemon and opponent's
        if trainers[0].active_pokemon().speed > trainers[1].active_pokemon().speed:
            order = [0, 1]
        elif trainers[0].active_pokemon().speed < trainers[1].active_pokemon().speed:
            order = [1, 0]
        else:
            # choose randomly
            x = int(round(np.random.rand()))
            order = [x, 1 - x]
        # in speed order, attack, check if there was a KO, and select next pokemon if there is
        trainers[order[0]].active_pokemon().do_attack(trainers[order[1]].active_pokemon())
        if trainers[order[1]].active_pokemon().is_ko():
            trainers[order[1]].choose_next_pokemon()
            if not trainers[order[1]].active_pokemon():
                return
        else:
            trainers[order[1]].active_pokemon().do_attack(trainers[order[0]].active_pokemon())
            if trainers[order[0]].active_pokemon().is_ko():
                trainers[order[0]].choose_next_pokemon()

    def fight(self, opponent_trainer):
        """This method fights the opponent_trainer until one trainer has no conscious pokemon
        Returns True if this trainer wins and false if they lose
        """
        # while both trainers have active pokemon, take another turn
        while self.active_pokemon() and opponent_trainer.active_pokemon():
            """
            print("############################################\nNew turn\n")
            print("Self active pokemon: " + self.active_pokemon().name + " HP: " + str(self.active_pokemon().hp))
            print("Opponent active pokemon: " + opponent_trainer.active_pokemon().name + " HP: " 
            + str(opponent_trainer.active_pokemon().hp))
            """
            self.take_turn(opponent_trainer)
            # print("Turn over \n ############################################\n")

        # decide winner
        if self.active_pokemon():
            return True
        else:
            return False


def clear_db_tables(db, tablenames):
    cursor = db.cursor()
    for tn in tablenames:
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table' and name=?", (tn,))
        if cursor.fetchone():
            cursor.execute("DROP TABLE ?", (tn,))


class PokeDataSimulation:
    def __init__(self, pokemon_indices, simname="", n_pokemon_team=1, dbname="pokedex.sqlite"):
        if simname == "":
            self.simname = "Sim_" + str(len(pokemon_indices)) + "pokemon_" + str(n_pokemon_team) + "perteam"
        else:
            self.simname = simname
        self.index_lookuptablename = self.simname+"_index_lookup"
        self.resultstablename = self.simname + "_results"

        self.dbname = dbname
        db = sqlite3.connect(self.dbname)
        cursor = db.cursor()
        sql = ["DROP TABLE IF EXISTS " + self.index_lookuptablename, "DROP TABLE IF EXISTS " + self.resultstablename,
               "CREATE TABLE " + self.resultstablename + " (caseidx int, result bool)"]
        for s in sql:
            cursor.execute(s)
        poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")

        self.pokemon_indices = pokemon_indices
        index_lookup = pd.DataFrame(self.pokemon_indices, columns=["PokemonIdx"])
        index_lookup.to_sql(self.index_lookuptablename, db, index_label="FactorialIdx")

        self.experiment = BigFullFactorial([len(pokemon_indices)]*n_pokemon_team*2)
        self.n_pokemon_team = n_pokemon_team
        self.pokegen = Pokemon.create_pokemon_generator(poketable)
        db.commit()
        db.close()

    def run_case(self, caseidx):
        case = self.experiment.get_case_from_index(caseidx)
        caset1 = case[:self.n_pokemon_team]
        caset2 = case[self.n_pokemon_team:]
        if np.array_equal(caset1, caset2):
            return  # trainer 1 == trainer 2, no point in running
        elif self.experiment.get_index_from_case(caset2+caset1) < caseidx:
            return  # Trainer 2 vs trainer 1 has already been simulated
        else:
            t1 = Trainer(self.pokegen(caset1))
            t2 = Trainer(self.pokegen(caset2))
            if t1.fight(t2):
                result = 1
            else:
                result = 0
            sqlstring = "INSERT INTO " + self.resultstablename + " VALUES (" + str(caseidx) + "," + str(result) + ")"
            print(sqlstring)
            db = sqlite3.connect(self.dbname)
            cursor = db.cursor()
            cursor.execute(sqlstring)
            db.commit()
            db.close()

    def run_simulation(self):
        for i in self.experiment.idxrange:
            self.run_case(i)
