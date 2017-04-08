import pandas as pd
import os
# import sqlite3

dir_path = os.path.dirname(os.path.realpath(__file__))


def load_type_modifier_table(fname=dir_path+'/type-modifier-table.csv'):
    return pd.DataFrame.from_csv(fname)


def load_pokemon(fname=dir_path+'/pokemon.csv'):
    return pd.DataFrame.from_csv(fname, index_col=None)


# def load_type_modifier_table_from_db(dbfname="pokedex.sqlite"):
#     """load type modifier table from https://www.math.miami.edu/~jam/azure/compendium/typechart.htm,
#     with added fields for Dark, Steel and Fairy"""
#     db = sqlite3.connect(dbfname)
#     tmt = pd.read_sql_query("SELECT * FROM TypeModifier", db, index_col="index")
#     db.close()
#     # logging.debug("Type Modifier Table Database Loaded:")
#     # logging.debug(tmt)
#     return tmt
#
#
# def load_pokemon_table_from_db(dbfname="pokedex.sqlite"):
#     """load pokemon table from kaggle dataset"""
#     db = sqlite3.connect(dbfname)
#     poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")
#     db.close()
#     # logging.debug("Pokemon Database Loaded (sample shown):")
#     # logging.debug(poketable.sample(10))
#     return poketable
