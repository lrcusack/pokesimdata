from pokedatasim import FullFactPokeDataSim

name = 'orig166_1v1'

n = 166
originalidx = list(range(n))
pds = FullFactPokeDataSim(originalidx, simname=name)
pds.run_simulation()
pds.save_results_to_tinydb()
