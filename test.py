from pokedatasim import Pokemon
from pokedatasim import Trainer
import pandas as pd
import numpy as np
import sqlite3

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
"""

"""
# test poketable load + identify dominant pokemon
poketable = pd.read_table("Pokemon.csv",sep=";")
poketable.index = range(len(poketable.index)) # ensure index starts at 0
print(poketable)

pokemon = []
for i in range(len(poketable.index)) :
    name = poketable.name[i]
    type1 = poketable.type1[i]
    type2 = poketable.type2[i]
    hp = poketable.hp[i]
    attack = poketable.attack[i]
    defense = poketable.defense[i]
    spatk = poketable.spatk[i]
    spdef = poketable.spdef[i]
    speed = poketable.speed[i]
    pokemon.append(Pokemon(name,type1,type2,hp,attack,defense,spatk,spdef,speed))
print(len(pokemon))

dominantpokemon = []
for p1 in pokemon :
    dominant = True
    for p2 in pokemon:
        if p1.deterministicallyInferior(p2) :
            dominant = False
            break
    if dominant :
        dominantpokemon.append(p1)
print(len(dominantpokemon))

gen1dominant = []
for p in dominantpokemon:
    if p.id < 168:
        print(p.name)
        gen1dominant.append(p)
print (len(gen1dominant))

x = (800 ** 12) + 1
print(x)
"""

"""
# test sqlite, adding poketable and type modifier table to database and reading from it
db = sqlite3.connect("pokedex.sqlite")
c = db.cursor()

tmt_orig = pd.read_csv("type_modifiers.csv",sep=';', index_col = 0)
tmt_orig.to_sql("TypeModifier", db)

#poketable_orig = pd.read_table("Pokemon.csv",sep=";")
#poketable_orig.to_sql("Pokemon", db)

tmtable = pd.read_sql_query("SELECT * FROM TypeModifier", db, index_col="index")
print(tmtable)
"""

"""
# test creating trainers with Pokemon.fromDataFrame and battling
db = sqlite3.connect("pokedex.sqlite")
poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")

#print(poketable)
pokemonRanges1 = range(166,172)
pokemonRanges2 = range(6,12)
pokemonRanges2test = [6,7,8,9,10,11]

pokemonIndices1 = [x for x in [2,6,11,168,171,174]]
pokemonIndices2 = [x for x in [156,157,158,162,165,165]]

print("Pokemon Ranges 1:", str(pokemonRanges1))
print("Pokemon Ranges 2:", str(pokemonRanges1))
print("Pokemon Indices 1:", str(pokemonIndices1))
print("Pokemon Indices 2:", str(pokemonIndices1))

useRanges = False

if useRanges :
    t1_df = poketable.loc[[x for x in pokemonRanges1]]
    t2_df = poketable.loc[[x for x in pokemonRanges2]]
    t2_df_test = poketable.loc[[x for x in pokemonRanges2test]]
    print("type t2df :",type(t2_df))
    print("type t2dftest :",type(t2_df_test))
    print("test equal:",str(t2_df==t2_df_test))
    print("t2_df type 2:",type(t2_df.type2[9]))
    print("t2_dftest type 2:",type(t2_df_test.type2[9]))
else:
    t1_df = poketable.loc[[x for x in pokemonIndices1]]
    t2_df = poketable.loc[[x for x in pokemonIndices2]]

print (t1_df)
print(t2_df)

t1 = Trainer(Pokemon.fromDataFrame(t1_df))
t2 = Trainer(Pokemon.fromDataFrame(t2_df))

print(t1.pokemon[2].type)

print(t1.fight(t2))
"""

"""
#test pokegen
db = sqlite3.connect("pokedex.sqlite")
poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")
pokegen = Pokemon.createPokemonGenerator(poketable)
pokemonIndices1 = [2,6,11,168,171,174]
pokemonIndices2 = [156,157,158,162,165,165]

i = 1
pokemon = Pokemon.fromDataFrame(poketable.loc[i])

pokemon = [Pokemon.fromDataFrame(poketable.loc[x]) for x in pokemonIndices1]

t1 = Trainer(pokegen(pokemonIndices1))
t2 = Trainer(pokegen(pokemonIndices2))

print(t1.fight(t2))
t1.reset()
t2.reset()
print(t2.fight(t1))
"""


#test hashing