from pokedatasim import *
import pandas as pd
import numpy as np
import sqlite3
import unittest


class TestPokemonClass(unittest.TestCase):
    """This class tests the Pokemon class for basic functionality"""
    def checkPokemon(self, pokemonobjects, pokemonnames):
        if not isinstance(pokemonobjects, list):
            pokemonobjects = [pokemonobjects]
        if not isinstance(pokemonnames,list):
            pokemonnames = [pokemonnames]
        for idx, p in enumerate(pokemonobjects):
            with self.subTest(i=idx):
                self.assertIsInstance(p, Pokemon)
                self.assertEqual(p.name, pokemonnames[idx])

    def test_constructor(self):
        name = "Bulbasaur"
        type1 = "Grass"
        type2 = "Poison"
        hp = 45 # should become 149
        attack = 49 # should become 98
        defense = 49 # should become 98
        spatk = 65 # should become 114
        spdef = 65 # should become 114
        speed = 45 # should become 94
        bulba = Pokemon(name, type1, type2, hp, attack, defense, spatk, spdef, speed)
        self.checkPokemon(bulba, "Bulbasaur")
        self.assertEqual(bulba.type, ["Grass", "Poison"])
        self.assertEqual(bulba.hp, 149)
        self.assertEqual(bulba.attack, 98)
        self.assertEqual(bulba.defense, 98)
        self.assertEqual(bulba.spatk, 114)
        self.assertEqual(bulba.spdef, 114)
        self.assertEqual(bulba.speed, 94)

    def test_dynamic_creation(self):
        # setup test variables
        db = sqlite3.connect('pokedex.sqlite')
        poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")
        pikachuindex = 30  # pikachu
        vcbIndices = [2, 6, 11]  # Venusaur, Charizard, Blastoise
        checklist = ['Venusaur', 'Charizard', 'Blastoise']
        fullpokegen = Pokemon.createPokemonGenerator(poketable)
        cutpokegen = Pokemon.createPokemonGenerator(poketable.iloc[vcbIndices + [pikachuindex]])

        # test single row creation from Data frame
        pikachu = Pokemon.fromDataFrame(poketable.iloc[pikachuindex])
        self.checkPokemon(pikachu, "Pikachu")

        # test multi row creation from data frame
        vcb = Pokemon.fromDataFrame(poketable.iloc[vcbIndices])
        self.assertIsInstance(vcb, list)
        self.checkPokemon(vcb, checklist)

        # test single row pokegen with full df
        pikachufullgen = fullpokegen(pikachuindex)
        self.checkPokemon(pikachufullgen, "Pikachu")

        # test multi row pokegen with full df
        vcbfullgen = fullpokegen(vcbIndices)
        self.assertIsInstance(vcbfullgen, list)
        self.checkPokemon(vcbfullgen, checklist)

        # test single row pokegen with cut df
        pikachucutgen = cutpokegen(pikachuindex)
        self.checkPokemon(pikachucutgen, "Pikachu")

        # test multi row pokegen with cut df
        vcbcutgen = cutpokegen(vcbIndices)
        self.assertIsInstance(vcbcutgen, list)
        self.checkPokemon(vcbcutgen, checklist)

    def test_battlemechanics(self):
        b = Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45)
        inferiorb = Pokemon("Bulbasaur", "Grass", "Poison", 44, 48, 48, 64, 64, 44)
        c = Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65)
        s = Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43)

        # test damage
        orighp = b.hp
        damage = 15
        b.takeDamage(damage)
        self.assertEqual(b.hp, orighp - damage)

        # test isKO
        b.hp = 0
        self.assertTrue(b.isKO())

        # test recover
        b.recover()
        self.assertEqual(b.hp, b.maxhp)

        # test inferior
        self.assertTrue(inferiorb.deterministicallyInferiorTo(b))

        # test damage (numbers from azure heights lab battle damage calculator
        # bulbasaur attacks charmander 22
        self.assertEqual(b.doAttack(c), 22)
        # bulbasaur attacks squirtle 41
        self.assertEqual(b.doAttack(s), 41)
        # charmander attacks bulbasaur 39
        self.assertEqual(c.doAttack(b), 39)

        b.recover()
        s.recover()
        c.recover()

        # charmander attacks squirtle 11
        self.assertEqual(c.doAttack(s), 11)
        # squirtle attacks bulbasaur 14
        self.assertEqual(s.doAttack(b), 14)
        # squirtle attacks charmander 15
        self.assertEqual(s.doAttack(c), 15)


class TestTrainerClass(unittest.TestCase):
    """This class tests the Trainer class for basic functionality"""
    def test_constructor(self):
        b = Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45)
        c = Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65)
        s = Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43)
        t = Trainer([b, c, s])

        self.assertIsInstance(t.pokemon, list)
        self.assertIsInstance(t.pokemon[0], Pokemon)

    def test_selectionmechanics(self):
        b = Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45)
        c = Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65)
        s = Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43)

        # test select next conscious pokemon
        t = Trainer([b, c, s])
        t.pokemon[0].hp = 0 # knock out first pokemon
        t.chooseNextPokemon()
        self.assertEqual(t.activePokemonIdx, 1)

        # test activePokemon
        self.assertEqual(t.activePokemon().name,"Charmander")

        # test that -1 is returned if all pokemon are KOed
        for p in t.pokemon:
            p.hp = 0
        t.chooseNextPokemon()
        self.assertEqual(t.activePokemonIdx,-1)

        # test reset
        t.reset()
        self.assertEqual(t.activePokemonIdx, 0)
        self.assertEqual(t.activePokemon().hp, t.activePokemon().maxhp)

    def test_battlemechanics(self):
        bs = []
        cs = []
        ss = []
        for i in range(6):
            bs.append(Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45))
            cs.append(Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65))
            ss.append(Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43))
        btrainer = Trainer(bs)
        ctrainer = Trainer(cs)
        strainer = Trainer(ss)

        # test correct order, whoever has higher speed will attack first and KO opponent
        ctrainer.activePokemon().hp = 1
        btrainer.activePokemon().hp = 1
        ctrainer.takeTurn(btrainer)
        self.assertEqual(btrainer.activePokemonIdx,1)
        self.assertEqual(ctrainer.activePokemonIdx,0)

        # test type effectiveness (sanity check)
        ctrainer.reset()
        btrainer.reset()
        self.assertTrue(btrainer.fight(strainer))
        btrainer.reset()
        strainer.reset()
        self.assertTrue(ctrainer.fight(btrainer))
        btrainer.reset()
        ctrainer.reset()
        self.assertTrue(strainer.fight(ctrainer))


class TestWorkerFunctions(unittest.TestCase):
    """This class tests the Big Factorial Class"""
    samplelevels = [[4, 2, 3],[2, 2],[3, 3, 3],[2, 5, 4]]

    @staticmethod
    def standardFullFact(levels):
        nfact = len(levels)
        ncases = np.prod(levels)
        casematrix = np.zeros((ncases, nfact))

        lev_repeat = 1
        pattern_repeat = ncases
        for fact in range(nfact):
            pattern_repeat //= levels[fact]
            level = []
            for val in range(levels[fact]):
                level += [val] * lev_repeat
            pattern = level * pattern_repeat
            lev_repeat *= levels[fact]
            casematrix[:, fact] = pattern

        return [list(casematrix[i, :]) for i in range(ncases)]

    def test_BigFullFactClass(self):
        for levels in self.samplelevels:
            with self.subTest(i=levels):
                bff = BigFullFactorial(levels)
                bff_cases = [bff.getCaseFromIndex(i) for i in bff.idxrange]
                sff_cases = self.standardFullFact(levels)

                # check that standard full factorial and big full factorial are identical
                for bffc in bff_cases:
                    self.assertTrue(bffc in sff_cases)
                    sff_cases.remove(bffc)

                # check that getIndexFromCase and getCaseFromIndex are inverse
                for idx in bff.idxrange:
                    self.assertEqual(bff.getIndexFromCase(bff.getCaseFromIndex(idx)), idx)

    def test_db_loading(self):
        # test load poketable
        poketable = load_pokemon_table_from_db()
        self.assertEqual(list(poketable), ['num', 'name', 'type1', 'type2', 'total', 'hp', 'attack', 'defense',
                                          'spatk', 'spdef', 'speed', 'generation', 'legendary'])
        self.assertEqual(len(poketable), 800)

        # test load type modifier table
        typemodifiertable = load_type_modifier_table_from_db()
        types = list(typemodifiertable)
        self.assertEqual(types, list(typemodifiertable.index))

if __name__ == "__main__":
    unittest.main()


"""
pds = PokeDataSimulation("test")
pds.runSimulation()

db = sqlite3.connect("pokedex.sqlite")
resultstable = pd.read_sql_query("SELECT * FROM test_results", db,index_col="caseidx")
print(resultstable)
indexlookup = pd.read_sql_query("SELECT * FROM test_indexLookup", db,index_col="FactorialIdx")
print(indexlookup)


for i in resultstable.index:
    case = pds.experiment.getCaseFromIndex(i)
    middle = int(len(case)/2)
    print([pds.pokegen([pds.pokemonIndices[case[c]]])[0].name for c in case[:middle]],\
          'vs', [pds.pokegen([pds.pokemonIndices[case[c]]])[0].name for c in case[middle:]])

"""
