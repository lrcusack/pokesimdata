import pandas as pd
import numpy as np
from copy import deepcopy
import sqlite3


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

    def getCaseFromIndex(self, idx):
        """Method for defining cases based on an index
        like a de-hash function"""
        if idx not in self.idxrange:
            return None
        remainder = idx
        case = []
        for i in range(len(self.levels)):
            divisor = np.prod(self.levels[i:]) / self.levels[i]
            case.append(int(remainder // divisor))
            remainder = remainder % divisor
        return case

    def getIndexFromCase(self, case):
        """Method for defining an index for a given case
        like a hash function"""
        resultIdx = 0
        for idx in range(len(case)):
            if case[idx] not in range(self.levels[idx]):
                return None
            resultIdx += case[idx] * np.prod(self.levels[idx:]) / self.levels[idx]
        return int(resultIdx)


class Pokemon:
    """ This class defines a Pokemon """
    standardLevel = 50
    standardAttackPower = 30
    standardIV = 15 # average from genIII up on http://bulbapedia.bulbagarden.net/wiki/Individual_values
    standardEV = round(510/6) # even distribution of EV across stats from http://bulbapedia.bulbagarden.net/wiki/Effort_values
    typeModifierTable = load_type_modifier_table_from_db()

    specialTypes = ['Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Psychic']
    physicalTypes = ['Normal', 'Fighting', 'Flying', 'Ground',
                     'Rock', 'Bug', 'Poison', 'Ghost', 'Dragon', 'Dark', 'Steel', "Fairy"]
    allTypes = set(specialTypes + physicalTypes)

    @classmethod
    def calculateStat(cls, statbase, level=None, iv=None, ev=None, statname=''):
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
        self.maxhp = Pokemon.calculateStat(hp, statname='hp')
        self.hp = self.maxhp
        self.attack = Pokemon.calculateStat(attack)
        self.defense = Pokemon.calculateStat(defense)
        self.spatk = Pokemon.calculateStat(spatk)
        self.spdef = Pokemon.calculateStat(spdef)
        self.speed = Pokemon.calculateStat(speed)
        self.level = Pokemon.standardLevel

    def __str__(self):
        return (self.name + ":" + " hp-" + str(self.hp) + " maxhp-" + str(self.maxhp) + " atk-" + str(self.attack) +
                " def-" + str(self.defense) + " spatk-" + str(self.spatk) + " spdef-" + str(self.spdef) +
                " speed-" + str(self.speed))

    def __repr__(self):
        return str(self)

    @classmethod
    def fromDataFrame(cls, poketable):
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
            hp = poketable["hp"]
            attack = poketable["attack"]
            defense = poketable["defense"]
            spatk = poketable["spatk"]
            spdef = poketable["spdef"]
            speed = poketable["speed"]
            pokemonlist = cls(name, type1, type2, hp, attack, defense, spatk, spdef, speed)
        return pokemonlist

    @classmethod
    def createPokemonGenerator(cls, pokemon_table):
        """This returns a function that takes a list of (possibly non-unique) indices for the given poketable
        returns a list of those pokemon"""
        return lambda x: [cls.fromDataFrame(pokemon_table.loc[i]) for i in x] if isinstance(x,list) \
                else cls.fromDataFrame(pokemon_table.loc[x])


    def isKO(self):
        """Returns true if this pokemon is knocked out, false otherwise"""
        return self.hp == 0

    def deterministicallyInferiorTo(self, other):
        """If this pokemon has the same types and strictly lower stats, return true"""
        return \
            ((set(self.type) == set(other.type))
             and (self.maxhp < other.maxhp)
             and (self.attack < other.attack)
             and (self.defense < other.defense)
             and (self.spatk < other.spatk)
             and (self.spdef < other.spdef)
             and (self.speed < other.speed))

    def takeDamage(self, damage):
        """apply damage, make sure lowest hp is 0"""
        self.hp = max(0, self.hp - damage)

    def recover(self):
        self.hp = self.maxhp

    @staticmethod
    def damageEquation(A, B, C, D, X, Y, Z):
        """This algorithm is based on https://www.math.miami.edu/~jam/azure/compendium/battdam.htm"""
        return int(int(int(int(int(int(int(int(int(int(2 * A / 5 + 2) * B) * C) / D) / 50) + 2) * X) * Y) * Z) / 255)

    def calculateDamage(self, otherPokemon):
        """Calculate the damage this pokemon can do to otherPokemon"""
        # Set independent values (pokemon-agnostic)
        """# use random critical hit
        if np.random.rand() < .05:
            criticalHit = 1
        else:
            criticalHit = 0
        """
        # no critical hit
        criticalHit = 0

        A = self.level * (1 + criticalHit)  # level of pokemon
        C = Pokemon.standardAttackPower  # power of attack
        X = 1.5
        """# use true random attack value
        Z = int(217 + (255 - 217) * np.random.rand())  # random value  between 217 and 255
        """
        # use average attack value
        Z = round((217+255)/2)
        damage = [0] * len(self.type)
        # calculate estimated attack score for each attack type
        for idx, attackType in enumerate(self.type):
            # calculate type modifier Y
            Y = 1
            for defenseType in otherPokemon.type:
                # lookup type modifier
                thisModifier = Pokemon.typeModifierTable[defenseType][attackType]
                Y = Y * thisModifier

            # if this attack type is a physical attack, use attack stat
            if not set(Pokemon.specialTypes).intersection(attackType):
                B = self.attack  # attack score
                D = otherPokemon.defense  # defense score
            else:  # otherwise use special attack
                B = self.spatk
                D = otherPokemon.spdef

            # calculate damage for this attack type
            damage[idx] = Pokemon.damageEquation(A, B, C, D, X, Y, Z)
            """
            print("A: " + str(A))
            print("B: " + str(B))
            print("C: " + str(C))
            print("D: " + str(D))
            print("X: " + str(X))
            print("Y: " + str(Y))
            print("Z: " + str(Z))
            print("Damage: " + str(damage[idx]))
            """

        # Add entry for non-same-type physical attack
        X = 1  # no STAB
        B = self.attack  # attack score
        D = otherPokemon.defense  # defense score
        Y = 1  # no type modifier
        defaultDamage = Pokemon.damageEquation(A, B, C, D, X, Y, Z)
        damage.append(defaultDamage)
        """
        print("A: " + str(A))
        print("B: " + str(B))
        print("C: " + str(C))
        print("D: " + str(D))
        print("X: " + str(X))
        print("Y: " + str(Y))
        print("Z: " + str(Z))
        print("Damage: " + str(defaultDamage))
        """

        # return maximum damage
        return max(damage)

    def doAttack(self, otherPokemon):
        """This pokemon attacks otherPokemon"""
        # print(self.name + " is attacking " + otherPokemon.name)
        damage = self.calculateDamage(otherPokemon)
        otherPokemon.takeDamage(damage)
        """
        print(self.name + " attacks " + otherPokemon.name + " for " + str(damage) + " damage")
        if otherPokemon.isKO() :
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
        self.activePokemonIdx = 0

    def chooseNextPokemon(self):
        """Select next pokemon, ignore types and strategy"""
        self.activePokemonIdx = -1
        for idx, p in enumerate(self.pokemon):
            if not p.isKO():
                self.activePokemonIdx = idx
                break

    def activePokemon(self):
        """Return trainer's active pokemon"""
        if self.activePokemonIdx >= 0:
            return self.pokemon[self.activePokemonIdx]
        else:
            return

    def reset(self):
        """restore all trainer's pokemons' health"""
        for p in self.pokemon:
            p.recover()
        self.activePokemonIdx = 0

    def takeTurn(self, opponentTrainer):
        """ Process one 'turn' of pokemon battle """
        trainers = [self, opponentTrainer]
        # Compare speed of this trainer's active pokemon and opponent's
        if trainers[0].activePokemon().speed > trainers[1].activePokemon().speed:
            order = [0, 1]
        elif trainers[0].activePokemon().speed < trainers[1].activePokemon().speed:
            order = [1, 0]
        else:
            # choose randomly
            x = int(round(np.random.rand()))
            order = [x, 1 - x]
        # in speed order, attack, check if there was a KO, and select next pokemon if there is
        trainers[order[0]].activePokemon().doAttack(trainers[order[1]].activePokemon())
        if trainers[order[1]].activePokemon().isKO():
            trainers[order[1]].chooseNextPokemon()
            if not trainers[order[1]].activePokemon():
                return
        else:
            trainers[order[1]].activePokemon().doAttack(trainers[order[0]].activePokemon())
            if trainers[order[0]].activePokemon().isKO():
                trainers[order[0]].chooseNextPokemon()

    def fight(self, opponentTrainer):
        """This method fights the opponentTrainer until one trainer has no conscious pokemon
        Returns True if this trainer wins and false if they lose
        """
        # while both trainers have active pokemon, take another turn
        while self.activePokemon() and opponentTrainer.activePokemon():
            """
            print("############################################\nNew turn\n")
            print("Self active pokemon: " + self.activePokemon().name + " HP: " + str(self.activePokemon().hp))
            print("Opponent active pokemon: " + opponentTrainer.activePokemon().name + " HP: " + str(opponentTrainer.activePokemon().hp))
            """
            self.takeTurn(opponentTrainer)
            # print("Turn over \n ############################################\n")

        # decide winner
        if self.activePokemon():
            return True
        else:
            return False

def clearDatabaseTables(db,tablenames):
    cursor = db.cursor()
    for tn in tablenames:
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table' and name=?", (tn,))
        if cursor.fetchone():
            cursor.execute("DROP TABLE ?",(tn,))


class PokeDataSimulation:
    def __init__(self,simname = "", pokemonIndices=[2,6,11], nPokemonTeam=1, dbname = "pokedex.sqlite"):
        if simname == "":
            self.simname = "Sim_" + len(pokemonIndices) + "pokemon_" + nPokemonTeam + "perteam";
        else:
            self.simname = simname
        self.indexlookuptablename = self.simname+"_indexLookup"
        self.resultstablename = self.simname + "_results"

        self.dbname = dbname
        db = sqlite3.connect(self.dbname)
        cursor = db.cursor()
        sql = ["DROP TABLE IF EXISTS " + self.indexlookuptablename,
                "DROP TABLE IF EXISTS " + self.resultstablename,
                "CREATE TABLE " + self.resultstablename + " (caseidx int, result bool)"]
        for s in sql:
            cursor.execute(s)
        poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")

        self.pokemonIndices = pokemonIndices
        indexLookup = pd.DataFrame(self.pokemonIndices,columns=["PokemonIdx"])
        indexLookup.to_sql(self.indexlookuptablename,db,index_label="FactorialIdx")

        self.experiment = BigFullFactorial([len(pokemonIndices)]*nPokemonTeam*2)
        self.nPokemonTeam = nPokemonTeam
        self.pokegen = Pokemon.createPokemonGenerator(poketable)
        db.commit()
        db.close()

    def runCase(self,caseidx):
        case = self.experiment.getCaseFromIndex(caseidx)
        caset1 = case[:self.nPokemonTeam]
        caset2 = case[self.nPokemonTeam:]
        if np.array_equal(caset1, caset2):
            return #trainer 1 == trainer 2, no point in running
        elif self.experiment.getIndexFromCase(caset2+caset1) < caseidx:
            return # Trainer 2 vs trainer 1 has already been simulated
        else :
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

    def runSimulation(self):
        for i in self.experiment.idxrange:
            self.runCase(i)





