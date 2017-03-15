from pokedatasim import Pokemon
from pokedatasim import Trainer
import pandas as pd
#import numpy as np

print("imports complete")

"""
# test typeModifierTable load
typeModifierTable = pd.read_table("type_modifiers.csv", index_col = 0,sep=",")

print (typeModifierTable)
"""

"""
# test random number generator
for i in range(100) :
    print(str(int(217 + (255-217)*np.random.rand())))
"""

"""
# test pokemon construction and interaction
def printHitPoints(pokemon) :
    print(pokemon.name + " has " + str(pokemon.hp) + " hit points")

bulba = Pokemon("Bulbasaur","Grass","Poison",45,49,49,65,65,45)
bulba2 = bulba
print(bulba.name)

charm = Pokemon("Charmander","Fire","",39,52,43,60,50,65)
print (charm.name)

printHitPoints(charm)
bulba.doAttack(charm)
printHitPoints(charm)

printHitPoints(bulba)
charm.doAttack(bulba)
printHitPoints(bulba)

printHitPoints(bulba2)
"""


# Test trainer construction and interaction, plus reset
b1 = Pokemon("Bulbasaur1","Grass","Poison",45,49,49,65,65,45)
b2 = Pokemon("Bulbasaur2","Grass","Poison",45,49,49,65,65,45)
b3 = Pokemon("Bulbasaur3","Grass","Poison",45,49,49,65,65,45)
b4 = Pokemon("Bulbasaur4","Grass","Poison",45,49,49,65,65,45)
b5 = Pokemon("Bulbasaur5","Grass","Poison",45,49,49,65,65,45)
b6 = Pokemon("Bulbasaur6","Grass","Poison",45,49,49,65,65,45)

c1 = Pokemon("Charmander1","Fire","",39,52,43,60,50,65)
c2 = Pokemon("Charmander2","Fire","",39,52,43,60,50,65)
c3 = Pokemon("Charmander3","Fire","",39,52,43,60,50,65)
c4 = Pokemon("Charmander4","Fire","",39,52,43,60,50,65)
c5 = Pokemon("Charmander5","Fire","",39,52,43,60,50,65)
c6 = Pokemon("Charmander6","Fire","",39,52,43,60,50,65)

s1 = Pokemon('Squirtle1','Water','',44,48,65,50,64,43)
s2 = Pokemon('Squirtle2','Water','',44,48,65,50,64,43)
s3 = Pokemon('Squirtle3','Water','',44,48,65,50,64,43)
s4 = Pokemon('Squirtle4','Water','',44,48,65,50,64,43)
s5 = Pokemon('Squirtle5','Water','',44,48,65,50,64,43)
s6 = Pokemon('Squirtle6','Water','',44,48,65,50,64,43)

btrainer = Trainer(b1,b2,b3,b4,b5,b6)
strainer = Trainer(s1,s2,s3,s4,s5,s6)
ctrainer = Trainer(c1,c2,c3,c4,c5,c6)

# bulbasaur vs charmander
if btrainer.fight(ctrainer) :
    print ("b won")
else :
    print ("c won")

# squirtle vs veteran charmander
if strainer.fight(ctrainer) :
    print ("s won")
else :
    print ("c won")

# defeated bulbasaur vs veteran squirtle
if btrainer.fight(strainer) :
    print ("b won")
else :
    print ("s won")

#reset bulbasaur vs veteran squirtle
btrainer.reset()
if btrainer.fight(strainer) :
    print ("b won")
else :
    print ("s won")



#test pokemon table load
poketable = pd.read_table("Pokemon.csv",sep=",")
print (poketable)
