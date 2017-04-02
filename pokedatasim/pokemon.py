from pokedatasim.loggable import Loggable
from pokedatasim.sqlmethods import *


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
        type1 = self.type[0]
        if len(self.type) < 2:
            type2 = None
        else:
            type2 = self.type[1]
        return {'name': self.name, 'level': self.level, 'type1': type1, 'type2': type2, "hp": self.hp,
                "maxhp": self.maxhp, "attack": self.attack, "defense": self.defense, "spatk": self.spatk,
                "spdef": self.spdef, "speed": self.speed}

    @classmethod
    def from_dict(cls, d, calcstat=True):
        return cls(d['name'], d['type1'], d['type2'], d['maxhp'], d['attack'], d['defense'],
                   d['spatk'], d['spdef'], d['speed'], calcstat=calcstat)

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
                 level=0, iv=0, ev=0, calcstat=True):
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
        if calcstat:
            self.maxhp = Pokemon.calculate_stat(hp, level, iv, ev, statname='hp')
            self.attack = Pokemon.calculate_stat(attack, level, iv, ev, statname='attack')
            self.defense = Pokemon.calculate_stat(defense, level, iv, ev, statname='defense')
            self.spatk = Pokemon.calculate_stat(spatk, level, iv, ev, statname='spatk')
            self.spdef = Pokemon.calculate_stat(spdef, level, iv, ev, statname='spdef')
            self.speed = Pokemon.calculate_stat(speed, level, iv, ev, statname='speed')
        else:
            self.maxhp = hp
            self.attack = attack
            self.defense = defense
            self.spatk = spatk
            self.spdef = spdef
            self.speed = speed
        self.level = level
        self.hp = self.maxhp

        self.dbg(str(self))

    def compare(self, other):
        return (other.name == self.name and other.type == self.type and other.maxhp == self.maxhp
                and other.attack == self.attack and other.defense == self.defense and other.spatk == self.spatk
                and other.spdef == self.spdef and other.speed == self.speed)

    @classmethod
    def from_data_frame(cls, poketable, level=0, iv=0, ev=0, calcstat=True):
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
                pokemonlist.append(cls(name, type1, type2, hp, attack, defense, spatk, spdef, speed,
                                       level=level, iv=iv, ev=ev, calcstat=calcstat))
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
            pokemonlist = cls(name, type1, type2, hp, attack, defense, spatk, spdef, speed,
                              level=level, iv=iv, ev=ev, calcstat=calcstat)
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
