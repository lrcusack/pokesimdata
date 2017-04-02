from pokedatasim import FullFactPokeDataSim

name = 'vcb_3v3'

originalidx = [2, 6, 11]  # venusaur charizard blastoise
pds = FullFactPokeDataSim(originalidx, simname=name, n_pokemon_team=3)
pds.run_simulation()
pds.save_results_to_tinydb()