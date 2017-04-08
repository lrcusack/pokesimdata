from pokedatasim.loggable import Loggable
import numpy as np
from time import time
from tinydb import TinyDB
from pokedatasim.trainer import Trainer
from pokedatasim.pokemon import Pokemon
from pokedatasim.dataload import *
from pokedatasim.bigfullfactorial import BigFullFactorial


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

    def cleanup_case(self, case):
        pass

    def run_case(self, case):
        if not case:
            return None
        tic = time()
        t1 = case['t1']
        t2 = case['t2']
        t1win = t1.fight(t2)
        if t1win:
            record = {'Winner': t1.to_dict(), 'Loser': t2.to_dict()}
            winner = str(t1.to_str_list())
            loser = str(t2.to_str_list())
        else:
            record = {'Winner': t2.to_dict(), 'Loser': t1.to_dict()}
            winner = str(t2.to_str_list())
            loser = str(t1.to_str_list())
        toc = time()
        self.dbg(winner + ' beat ' + loser + ' in ' + str(toc-tic) + 's')
        return record

    def record_result(self, result):
        if result:
            self.results.append(result)

    def run_simulation(self):
        tic = time()
        self.results = []
        for i in self.idxrange:
            case = self.setup_case(i)
            self.record_result(self.run_case(case))
            self.cleanup_case(case)
        toc = time()
        telapsed = toc - tic
        self.dbg("sim time: " + str(telapsed) + 's')
        self.dbg("avg time per case: " + str(telapsed/(len(self.idxrange)**2)))

    def save_results_to_tinydb(self, tinydbfname='PokeDataSim.json'):
        tic = time()
        tdb = TinyDB(tinydbfname)
        tdb.purge_table(self.simname)
        results_table = tdb.table(name=self.simname)
        results_table.insert_multiple(self.results)
        tdb.close()
        toc = time()
        self.dbg("db time: " + str(toc-tic) + 's')


class FullFactPokeDataSim(PokeDataSimulation):
    def __init__(self, pokemon_indices, simname="", n_pokemon_team=1):
        experiment = BigFullFactorial([len(pokemon_indices)] * n_pokemon_team * 2)
        super().__init__(experiment.idxrange, simname)

        self.pokemon_indices = pokemon_indices
        self.index_lookup = pd.DataFrame(self.pokemon_indices, columns=["PokemonIdx"])
        self.experiment = experiment
        self.idxrange = self.experiment.idxrange
        self.n_pokemon_team = n_pokemon_team
        self.pokegen = Pokemon.create_pokemon_generator(load_pokemon())

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


class TrainerListPokeDataSim(PokeDataSimulation):
    def __init__(self, trainer_list, simname=""):
        self.experiment = BigFullFactorial([len(trainer_list)] * 2)
        super().__init__(self.experiment.idxrange, simname)
        self.trainer_list = trainer_list

    def setup_case(self, caseidx):
        case = self.experiment.get_case_from_index(caseidx)
        if case[0] == case[1]:
            return None  # trainer 1 == trainer 2, no point in running
        elif self.experiment.get_index_from_case([case[1], case[0]]) < caseidx:
            return None  # Trainer 2 vs trainer 1 has already been simulated
        else:
            t1 = self.trainer_list[case[0]]
            t2 = self.trainer_list[case[1]]
            return {'t1': t1, 't2': t2}

    def cleanup_case(self, case):
        if case:
            case['t1'].reset()
            case['t2'].reset()
