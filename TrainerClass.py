import itertools as it
import numpy as np

class Trainer :
    """ This class defines a Trainer """
    newid = it.count()

    def __init__(self, p1,p2,p3,p4,p5,p6) :
        """ Construct a Trainer

        Keyword arguments:
        p1 -- first pokemon
        p2 -- second pokemon
        p3 -- third pokemon
        p4 -- fourth pokemon
        p5 -- fifth pokemon
        p6 -- sixth pokemon
        """
        self.pokemon = [p1,p2,p3,p4,p5,p6]
        self.id = next(Trainer.newid)
        self.activePokemonIdx = 0

    def chooseNextPokemon(self) :
        """Select next pokemon, ignore types and strategy"""
        self.activePokemonIdx = -1
        for idx, p in enumerate(self.pokemon) :
            if not p.isKO() :
                self.activePokemonIdx = idx
                break

    def activePokemon(self) :
        """Return trainer's active pokemon"""
        if self.activePokemonIdx >= 0 :
            return self.pokemon[self.activePokemonIdx]
        else:
            return

    def reset(self) :
        """restore all trainer's pokemons' health"""
        for p in self.pokemon :
            p.recover()
        self.activePokemonIdx = 0

    def takeTurn(self,opponentTrainer) :
        """ Process one 'turn' of pokemon battle """
        trainers = [self, opponentTrainer]
        # Compare speed of this trainer's active pokemon and opponent's
        if trainers[0].activePokemon().speed > trainers[1].activePokemon().speed:
            order = [0, 1]
        elif trainers[0].activePokemon().speed < trainers[1].activePokemon().speed :
            order = [1, 0]
        else :
            #choose randomly
            x = int(round(np.random.rand()))
            order = [x, 1-x]
        # in speed order, attack, check if there was a KO, and select next pokemon if there is
        trainers[order[0]].activePokemon().doAttack(trainers[order[1]].activePokemon())
        if trainers[order[1]].activePokemon().isKO() :
            trainers[order[1]].chooseNextPokemon()
            if not trainers[order[1]].activePokemon() :
                return
        else :
            trainers[order[1]].activePokemon().doAttack(trainers[order[0]].activePokemon())
            if trainers[order[0]].activePokemon().isKO() :
                trainers[order[0]].chooseNextPokemon()

    def fight(self,opponentTrainer) :
        """This method fights the opponentTrainer until one trainer has no conscious pokemon
        Returns True if this trainer wins and false if they lose
        """
        # while both trainers have active pokemon, take another turn
        while self.activePokemon() and opponentTrainer.activePokemon():
            """
            print("############################################\nNew turn\n")
            print("Self active pokemon: " + self.activePokemon().name + " HP: " + str(self.activePokemon().hp))
            print("Opponent active pokemon: " + opponentTrainer.activePokemon().name + " HP: " + str(opponentTrainer.activePokemon().hp))
            """
            self.takeTurn(opponentTrainer)
            #print("Turn over \n ############################################\n")

        # decide winner
        if self.activePokemon() :
            return True
        else :
            return False
