import itertools as it
import pandas as pd
import numpy as np

# load type modifier table from https://www.math.miami.edu/~jam/azure/compendium/typechart.htm
tmt = pd.read_table("type_modifiers.csv", index_col = 0,sep=",")

class Pokemon :
    """ This class defines a Pokemon """
    newid = it.count()
    standardLevel = 50
    standardAttackPower = 30
    typeModifierTable = tmt

    specialTypes = ['Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Psychic']
    physicalTypes = ['Normal', 'Fighting', 'Flying', 'Ground',
        'Rock', 'Bug', 'Poison', 'Ghost', 'Dragon']


    def __init__(self, name, type1, type2, hp,
        attack, defense, spatk, spdef, speed) :
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
        types = set([type1, type2])
        self.type = []
        for t in types :
            if t != "" :
                self.type.append(t)
        self.hp = hp
        self.maxhp = hp
        self.attack = attack
        self.defense = defense
        self.spatk = spatk
        self.spdef = spdef
        self.speed = speed
        self.level = Pokemon.standardLevel
        self.id = next(Pokemon.newid)

    def isKO(self) :
        """Returns true if this pokemon is knocked out, false otherwise"""
        return self.hp == 0

    def takeDamage(self, damage) :
        """apply damage, make sure lowest hp is 0"""
        self.hp = max(0,self.hp-damage)

    def recover(self) :
        self.hp = self.maxhp

    @staticmethod
    def damageEquation(A,B,C,D,X,Y,Z) :
        """This algorithm is based on https://www.math.miami.edu/~jam/azure/compendium/battdam.htm"""
        return int(int(int(int(int(int(int(int(int(int(2*A/5 + 2) * B)*C) / D) / 50)+2)*X)*Y)*Z)/255)

    def calculateDamage(self,otherPokemon) :
        """Calculate the damage this pokemon can do to otherPokemon"""
        # Set independent values (pokemon-agnostic)
        if np.random.rand() < .05 :
            criticalHit = 1
        else :
            criticalHit = 0
        A = self.level *(1 + criticalHit) # level of pokemon
        C = Pokemon.standardAttackPower # power of attack
        X = 1.5
        Z = int(217 + (255-217)*np.random.rand()) #  random value  between 217 and 255

        damage = [0] * len(self.type)
        #calculate estimated attack score for each attack type
        for idx,attackType in enumerate(self.type) :
            #calculate type modifier Y
            Y = 1
            for defenseType in otherPokemon.type :
                # lookup type modifier
                Y = Y * Pokemon.typeModifierTable[defenseType][attackType]

            # if this attack type is a physical attack, use attack stat
            if not set(Pokemon.specialTypes).intersection(attackType) :
                B = self.attack #attack score
                D = otherPokemon.defense # defense score
            else : # otherwise use special attack
                B = self.spatk
                D = otherPokemon.spdef

            #calculate damage for this attack type
            damage[idx] = Pokemon.damageEquation(A,B,C,D,X,Y,Z)
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
        X = 1 # no STAB
        B = self.attack #attack score
        D = otherPokemon.defense # defense score
        Y = 1 # no type modifier
        defaultDamage = Pokemon.damageEquation(A,B,C,D,X,Y,Z)
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

        #return maximum damage
        return max(damage)

    def doAttack(self,otherPokemon) :
        """This pokemon attacks otherPokemon"""
        #print(self.name + " is attacking " + otherPokemon.name)
        damage = self.calculateDamage(otherPokemon)
        otherPokemon.takeDamage(damage)
        """
        print(self.name + " attacks " + otherPokemon.name + " for " + str(damage) + " damage")
        if otherPokemon.isKO() :
            print(self.name + " is knocked out!")
        """
        return damage
