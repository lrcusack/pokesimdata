import pandas as pd
import sqlite3


def load_type_modifier_table_from_db():
    """load type modifier table from https://www.math.miami.edu/~jam/azure/compendium/typechart.htm,
    with added fields for Dark, Steel and Fairy"""
    db = sqlite3.connect("pokedex.sqlite")
    tmt = pd.read_sql_query("SELECT * FROM TypeModifier", db, index_col="index")
    db.close()
    # logging.debug("Type Modifier Table Database Loaded:")
    # logging.debug(tmt)
    return tmt


def load_pokemon_table_from_db():
    """load pokemon table from kaggle dataset"""
    db = sqlite3.connect("pokedex.sqlite")
    poketable = pd.read_sql_query("SELECT * FROM Pokemon", db, index_col="index")
    db.close()
    # logging.debug("Pokemon Database Loaded (sample shown):")
    # logging.debug(poketable.sample(10))
    return poketable
