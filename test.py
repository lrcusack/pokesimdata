"""
import pandas as pd
import numpy as np
"""

from PokemonClass import Pokemon

"""
typeModifierTable = pd.read_table("type_modifiers.csv", index_col = 0,sep=",")

print (typeModifierTable)

for i in range(100) :
    print(str(int(217 + (255-217)*np.random.rand())))
"""
def printHitPoints(pokemon) :
    print(pokemon.name + " has " + str(pokemon.hp) + " hit points")

bulba = Pokemon("Bulbasaur","Grass","Poison",45,49,49,65,65,45)
print(bulba.name)

charm = Pokemon("Charmander","Fire","",39,52,43,60,50,65)
print (charm.name)

printHitPoints(charm)
bulba.doAttack(charm)
printHitPoints(charm)

printHitPoints(bulba)
charm.doAttack(bulba)
printHitPoints(bulba)
