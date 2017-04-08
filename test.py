from pokedatasim.simulation import *
from pokedatasim.pokemon import Pokemon
from pokedatasim.trainer import Trainer
from pokedatasim.bigfullfactorial import BigFullFactorial
from pokedatasim.dataload import *
from pokedatasim.loggable import Loggable
import numpy as np
import unittest


class TestPokemonClass(unittest.TestCase, Loggable):
    """This class tests the Pokemon class for basic functionality"""

    def checkPokemon(self, pokemonobjects, pokemonnames):
        if not isinstance(pokemonobjects, list):
            pokemonobjects = [pokemonobjects]
        if not isinstance(pokemonnames, list):
            pokemonnames = [pokemonnames]
        for idx, p in enumerate(pokemonobjects):
            with self.subTest(i=idx):
                self.assertIsInstance(p, Pokemon)
                self.assertEqual(p.name, pokemonnames[idx])

    # @unittest.skip('Skipping Pokemon constructor Test')
    def test_constructor(self):
        name = "Bulbasaur"
        type1 = "Grass"
        type2 = "Poison"
        hp = 45  # should become 123
        attack = 49  # should become 72
        defense = 49  # should become 72
        spatk = 65  # should become 88
        spdef = 65  # should become 88
        speed = 45  # should become 68
        bulba = Pokemon(name, type1, type2, hp, attack, defense, spatk, spdef, speed)
        self.checkPokemon(bulba, "Bulbasaur")
        self.assertEqual(bulba.type, ["Grass", "Poison"])
        self.assertEqual(bulba.hp, 123)
        self.assertEqual(bulba.attack, 72)
        self.assertEqual(bulba.defense, 72)
        self.assertEqual(bulba.spatk, 88)
        self.assertEqual(bulba.spdef, 88)
        self.assertEqual(bulba.speed, 68)

    def test_dict_operations(self):
        name = "Bulbasaur"
        type1 = "Grass"
        type2 = "Poison"
        hp = 45  # should become 123
        attack = 49  # should become 72
        defense = 49  # should become 72
        spatk = 65  # should become 88
        spdef = 65  # should become 88
        speed = 45  # should become 68
        bulba = Pokemon(name, type1, type2, hp, attack, defense, spatk, spdef, speed)
        newbulba = Pokemon.from_dict(bulba.to_dict(), calcstat=False)
        self.assertTrue(bulba.compare(newbulba))

    # @unittest.skip('Skipping Dynamic Creation Test')
    def test_dynamic_creation(self):
        # setup test variables
        poketable = load_pokemon()
        pikachuindex = 30  # pikachu
        vcb_indices = [2, 6, 11]  # Venusaur, Charizard, Blastoise
        checklist = ['Venusaur', 'Charizard', 'Blastoise']
        fullpokegen = Pokemon.create_pokemon_generator(poketable)
        cutpokegen = Pokemon.create_pokemon_generator(poketable.iloc[vcb_indices + [pikachuindex]])

        # test single row creation from Data frame
        pikachu = Pokemon.from_data_frame(poketable.iloc[pikachuindex])
        self.checkPokemon(pikachu, "Pikachu")

        # test multi row creation from data frame
        vcb = Pokemon.from_data_frame(poketable.iloc[vcb_indices])
        self.assertIsInstance(vcb, list)
        self.checkPokemon(vcb, checklist)

        # test single row pokegen with full df
        pikachufullgen = fullpokegen(pikachuindex)
        self.checkPokemon(pikachufullgen, "Pikachu")

        # test multi row pokegen with full df
        vcbfullgen = fullpokegen(vcb_indices)
        self.assertIsInstance(vcbfullgen, list)
        self.checkPokemon(vcbfullgen, checklist)

        # test single row pokegen with cut df
        pikachucutgen = cutpokegen(pikachuindex)
        self.checkPokemon(pikachucutgen, "Pikachu")

        # test multi row pokegen with cut df
        vcbcutgen = cutpokegen(vcb_indices)
        self.assertIsInstance(vcbcutgen, list)
        self.checkPokemon(vcbcutgen, checklist)

    # @unittest.skip('Skipping battle mechanics test')
    def test_battlemechanics(self):
        b = Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45)
        inferiorb = Pokemon("Bulbasaur", "Grass", "Poison", 44, 48, 48, 64, 64, 44)
        c = Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65)
        s = Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43)

        # test damage
        orighp = b.hp
        damage = 15
        b.take_damage(damage)
        self.assertEqual(b.hp, orighp - damage)

        # test is_ko
        b.take_damage(b.hp)
        self.assertTrue(b.is_ko())

        # test recover
        b.recover()
        self.assertEqual(b.hp, b.maxhp)

        # test inferior
        self.assertTrue(inferiorb.deterministically_inferior_to(b))

        # test damage (numbers from azure heights lab battle damage calculator
        # bulbasaur attacks charmander 22
        self.assertEqual(b.do_attack(c), 22)
        # bulbasaur attacks squirtle 41
        self.assertEqual(b.do_attack(s), 41)
        # charmander attacks bulbasaur 38
        self.assertEqual(c.do_attack(b), 38)

        b.recover()
        s.recover()
        c.recover()

        # charmander attacks squirtle 12
        self.assertEqual(c.do_attack(s), 12)
        # squirtle attacks bulbasaur 13
        self.assertEqual(s.do_attack(b), 13)
        # squirtle attacks charmander 41
        self.assertEqual(s.do_attack(c), 41)


class TestTrainerClass(unittest.TestCase, Loggable):
    """This class tests the Trainer class for basic functionality"""
    # @unittest.skip('Skipping Trainer Construction Test')
    def test_constructor(self):
        b = Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45)
        c = Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65)
        s = Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43)
        t = Trainer([b, c, s])

        self.assertIsInstance(t.pokemon, list)
        self.assertIsInstance(t.pokemon[0], Pokemon)

    def test_dict_operations(self):
        bs = []
        for i in range(6):
            bs.append(Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45))
        btrainer = Trainer(bs)
        copytrainer = Trainer.from_dict(btrainer.to_dict(), calculate_stat=False)
        self.assertTrue(btrainer.compare(copytrainer))

    # @unittest.skip('Skipping Trainer Selection Mechanics Test')
    def test_selectionmechanics(self):
        b = Pokemon("Bulbasaur", "Grass", "Poison", 45, 49, 49, 65, 65, 45)
        c = Pokemon("Charmander", "Fire", "", 39, 52, 43, 60, 50, 65)
        s = Pokemon('Squirtle', 'Water', '', 44, 48, 65, 50, 64, 43)

        # test select next conscious pokemon
        t = Trainer([b, c, s])
        t.pokemon[0].hp = 0  # knock out first pokemon
        t.choose_next_pokemon()
        self.assertEqual(t.active_pokemon_idx, 1)

        # test active_pokemon
        self.assertEqual(t.active_pokemon().name, "Charmander")

        # test that -1 is returned if all pokemon are KOed
        for p in t.pokemon:
            p.hp = 0
        t.choose_next_pokemon()
        self.assertEqual(t.active_pokemon_idx, -1)

        # test reset
        t.reset()
        self.assertEqual(t.active_pokemon_idx, 0)
        self.assertEqual(t.active_pokemon().hp, t.active_pokemon().maxhp)

    # @unittest.skip('skipping trainer battle mechanics test')
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
        ctrainer.active_pokemon().hp = 1
        btrainer.active_pokemon().hp = 1
        ctrainer.take_turn(btrainer)
        self.assertEqual(btrainer.active_pokemon_idx, 1)
        self.assertEqual(ctrainer.active_pokemon_idx, 0)

        # test type effectiveness (sanity check)
        self.dbg('Resetting charmander and bulbasaur trainers')
        ctrainer.reset()
        btrainer.reset()
        self.dbg('Bulbasaur trainer fights squirtle trainer')
        self.assertTrue(btrainer.fight(strainer))
        self.dbg('Resetting squirtle and bulbasaur trainers')
        btrainer.reset()
        strainer.reset()
        self.dbg('charmander trainer fights bulbasaur trainer')
        self.assertTrue(ctrainer.fight(btrainer))
        self.dbg('Resetting charmander and bulbasaur trainers')
        btrainer.reset()
        ctrainer.reset()
        self.dbg('squirtle trainer fights charmander trainer')
        self.assertTrue(strainer.fight(ctrainer))


# @unittest.skip('Skipping Worker Function Test')
class TestWorkerFunctions(unittest.TestCase, Loggable):
    """This class tests the Big Factorial Class"""
    samplelevels = [[4, 2, 3], [2, 2], [3, 3, 3], [2, 5, 4]]

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
                bff_cases = [bff.get_case_from_index(i) for i in bff.idxrange]
                sff_cases = self.standardFullFact(levels)

                # check that standard full factorial and big full factorial are identical
                for bffc in bff_cases:
                    self.assertTrue(bffc in sff_cases)
                    sff_cases.remove(bffc)

                # check that get_index_from_case and get_case_from_index are inverse
                for idx in bff.idxrange:
                    self.assertEqual(bff.get_index_from_case(bff.get_case_from_index(idx)), idx)

    def test_db_loading(self):
        # test load poketable
        poketable = load_pokemon()
        self.assertEqual(list(poketable), ['num', 'name', 'type1', 'type2', 'total', 'hp', 'attack', 'defense',
                                           'spatk', 'spdef', 'speed', 'generation', 'legendary'])
        self.assertEqual(len(poketable), 800)

        # test load type modifier table
        typemodifiertable = load_type_modifier_table()
        types = list(typemodifiertable)
        self.assertEqual(types, list(typemodifiertable.index))


# @unittest.skip('Skipping simulation Test')
class TestSimulation(unittest.TestCase, Loggable):
    def test_fullfactsimresults(self):
        vcb_indices = [2, 6, 11]  # venusaur charizard blastoise
        pds = FullFactPokeDataSim(vcb_indices)
        pds.run_simulation()

        self.assertEqual(pds.results[0]['Winner']['pokemon'][0]['name'], 'Charizard')
        self.assertEqual(pds.results[1]['Winner']['pokemon'][0]['name'], 'Venusaur')
        self.assertEqual(pds.results[2]['Winner']['pokemon'][0]['name'], 'Blastoise')

    def test_trainerlistsimresults(self):
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
        trainers = [btrainer, ctrainer, strainer]

        pds = TrainerListPokeDataSim(trainers, 'trainerlisttest')
        pds.run_simulation()

        self.assertEqual(pds.results[0]['Winner']['pokemon'][0]['name'], 'Charmander')
        self.assertEqual(pds.results[1]['Winner']['pokemon'][0]['name'], 'Bulbasaur')
        self.assertEqual(pds.results[2]['Winner']['pokemon'][0]['name'], 'Squirtle')

if __name__ == "__main__":
    unittest.main()
