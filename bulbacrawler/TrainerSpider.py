import requests
from bs4 import BeautifulSoup
from pokedatasim.sqlmethods import load_pokemon_table_from_db
from pokedatasim.pokemon import Pokemon
from pokedatasim.trainer import Trainer
from tinydb import TinyDB

tdb = TinyDB('PokeDataSim.json')
tdb.purge_table('trainer')
tdb_trainers = tdb.table('trainers')

poketable = load_pokemon_table_from_db()


def strsearchfcngen(string):
    return lambda s: string in s if isinstance(s, str) else False

bulbapedia = "http://bulbapedia.bulbagarden.net"

page1url = "/wiki/Category:Trainer_classes"
page2url = "/w/index.php?title=Category:Trainer_classes&" + \
                      "pagefrom=Pokémon+Center+Lady+%28Trainer+class%29#mw-pages"

tcpage1 = requests.get(bulbapedia + page1url)
tcpage2 = requests.get(bulbapedia + page2url)

soup1 = BeautifulSoup(tcpage1.content, 'html.parser')
soup2 = BeautifulSoup(tcpage2.content, 'html.parser')

tcstr = '(Trainer class)'

trainerclasslinks = soup1.find_all('a', title=strsearchfcngen(tcstr)) \
                    + soup2.find_all('a', title=strsearchfcngen(tcstr))


trainerclasspageurls = []
for link in trainerclasslinks:
    trainerclasspageurls.append(link['href'])

#trainerclasspageurls = trainerclasspageurls[0:2]

trainers = []

for url in trainerclasspageurls:
    soup = BeautifulSoup(requests.get(bulbapedia + url).content, 'html.parser')
    if soup.find_all('h2', string=lambda s: strsearchfcngen('Trainer List')(s) or strsearchfcngen('Trainer list')(s)):
        attrs = {'align': 'center'}
        tables = soup.find_all('table', attrs=attrs)
        for tab in tables:
            rows = tab.find_all('tr')
            rows = rows[1:(len(rows)-1)]
            trainername = ''
            for r in rows:
                candidatetrainer = list(r.children)[1]
                if candidatetrainer.has_attr('rowspan'):
                    trainername = candidatetrainer.get_text()
                    trainername = trainername[:(len(trainername)-1)]
                    while trainername[0] == ' ':
                        trainername = trainername[1:len(trainername)]
                pokemon = r.find_all('td', align='center')
                pokelist = []
                for p in pokemon:
                    link = p.find('a')
                    if link:
                        pokenamestr = link['href']
                        pokenamestr = pokenamestr[6:pokenamestr.index('_')]
                        try:
                            level = int(p.get_text()[4:])
                        except ValueError:
                            level = 50
                        pokelist += Pokemon.from_data_frame(poketable.loc[poketable.name == pokenamestr], level=level)
                print(trainername)
                tdb_trainers.insert(Trainer(pokelist, trainername).to_dict())
