#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "18.02.20"
__usage__ = "Model for the DIP: spatial evolution"
__update__ = "22.03.24 16:35"

#========================== import ===========================#
from typing import Iterable
from numbers import Number

try:
    from model import *
except:
    from tools.model import *

try:
    from ezCLI import grid
except:
    from tools.ezCLI import grid

try:
    from evaluations_muettes import adaptive_evaluation as evaluation
except:
    from tools.evaluations_muettes import adaptive_evaluation as evaluation

try:
    from base import Strategy
except:
    try:
        from tools.base import Strategy
    except:
        print("No class 'Strategy' found")
        Strategy = 'Strategy'
    
import random
import numpy as np

try:
    import matplotlib.pyplot as plt
    HASPLOT = True
except:
    HASPLOT = False

#=============================================================#

#====================== helpers vicinity =====================#
def cyclic(sz, x, dx):
    """ image for an infinite world """
    return (x+dx)%sz

def mirror(sz, x, dx):
    """ image for a finite world with mirroring boundaries 
        requires dx <= sz/2
    """
    if x+dx < 0:
        target = abs(x+dx) -1
    elif x+dx >= sz:
        target = (sz-1) - (x+dx -sz)
    else:
        target = x+dx
    return target

def symetric(sz, x, dx):
    """ image for a finite world with symetric boundaries 
        requires dx <= sz/2
    """
    if x+dx < 0:
        target = abs(x+dx)
    elif x+dx >= sz:
        target = (sz-1) - (x+dx -sz +1)
    else:
        target = x+dx
    return target

def fixe(sz, x, dx):
    """ boundaries cant be bypassed """
    if 0 <= x+dx < sz: return x+dx
#=============================================================#

class World:
    FUNS = (fixe, mirror, symetric, cyclic)
    def __init__(self, lstOfStrat:Iterable, vicinity:Iterable,
                nbl:int, nbc:int, constraint:int):
        """ requires: what is the world populated with
                  the vicinity
                  the number of lines
                  the number of columns
                  the constraint to apply

            constraint are 0 : line_fixe column_fixe
                           1 : line_fixe column_mirror
                           2 : line_fixe column_symetric
                           3 : line_fixe column_cyclic
        """
        self.__constraint = min(len(self.FUNS)**2-1, max(constraint, 0))
        self.__nbl = max(3, nbl)
        self.__nbc = max(3, nbc)
        self.__lig_fun = self.FUNS[self.__constraint//len(self.FUNS)]
        self.__col_fun = self.FUNS[self.__constraint%len(self.FUNS)]
        self.__neighborhood = vicinity
        self.__sz_vicinity = len(vicinity)
        # define the parameters of the simulation
        # 1st the Model
        # 2nd the seed aka 'random_state'
        # 3rd the noise value
        # 4th the number of matches
        # 5th the minimum number of iterations for a match
        # 6th the maximum number of iterations for a match
        self.__sim_params = [None, None, 0, 5, 1, 11]
        self.__strategies = lstOfStrat
        self.__agents_names = {x.idnum: x.__class__.__name__
                               for x in self.__strategies}
        self.reset()
        
    def reset(self):
        ''' flush the world and agents' location '''
        # the dictionnary of strategies, indexed by their idnum
        self.__pop = {x.idnum: x for x in self.__strategies}
        # the grid is a np.array of empty cells
        self.__grid = -1 * np.ones(shape=(self.__nbl, self.__nbc))
        print(self.__grid.shape)
        self.__scores = {}
        self.__store = None
        
    def __str__(self):
        """ display the colors of the inhabitants """
        _tmp = np.zeros(shape=self.__grid.shape, dtype=int)
        for i in range(self.nb_lines):
            for j in range(self.nb_columns):
                try:
                    _tmp[i,j] = self.__pop[self.__grid[i,j]].color
                except:
                    pass
        return grid(_tmp, label=True, size=5)
        
    def lines(self,*args) -> int:
        """ op on lines """
        return self.__lig_fun(self.__nbl, *args)

    @property
    def lines_name(self) -> str:
        """ which function is in use for lines """
        return self.__lig_fun.__name__
    
    def columns(self,*args) -> int:
        """ op on columns """
        return self.__col_fun(self.__nbc, *args)    

    @property
    def columns_name(self) -> str:
        """ which function is in use for columns """
        return self.__col_fun.__name__

    @property
    def nb_lines(self) -> int:
        """ number of lines """
        return self.__nbl
    @property
    def nb_columns(self) -> int:
        """ number of columns """
        return self.__nbc
    @property
    def area(self) -> int:
        """ superficy lines*columns """
        return self.__nbl * self.__nbc
    
    @property
    def neighbors(self) -> tuple:
        """ relative neighborhood """
        return tuple(self.__neighborhood)

    def vicinity(self, *coord) -> list:
        """ compute the absolute coords of neighborhood 
            for a given x, y drop non coordinates 
        """
        x,y = coord
        return [(a,b) for a,b in [ (self.lines(x,dx), self.columns(y,dy))
                                 for dx,dy in self.neighbors ]
                if a is not None and b is not None ]

    @property
    def population(self) -> dict:
        """ the repartition of the population """
        _sz = {}
        for i in range(self.nb_lines):
            for j in range(self.nb_columns):
                x = self.__grid[i,j]
                x = x if x >= 0 else 'vide'
                _sz[x] = _sz.get(x, 0) +1
        return _sz

    def describe(self):
        ''' display the class name of agents '''
        return self.__agents_names
    def save(self):
        """ save the current repartition """
        self.__store = self.__grid[:]

    def restore(self):
        """ restore the previous state if it exists """
        if self.__store is not None: self.__grid = self.__store[:]
    #============= simulations parameters ===================#
    def __get_params(self, idx): return self.__sim_params[idx]
    def __set_params(self, idx, v): self.__sim_params[idx] = v
    #========================================================#
    @property
    def model(self) -> Model:
        """ requires a Model to work """
        return self.__get_params(0)
    @model.setter
    def model(self, m:Model):
        """ check that its a Model and set it """
        if isinstance(m, Model): self.__set_params(0, m)

    @property
    def random_state(self) -> int:
        """ for replication purpose """
        return self.__get_params(1)
    @random_state.setter
    def random_state(self, v:int):
        """ if u want redo, set it """
        if isinstance(v, int):  self.__set_params(1, v)

    @property
    def noise(self) -> float:
        """ 0: no noise, otherwise miscomprehension might happen """
        return self.__get_params(2)
    @noise.setter
    def noise(self, v):
        """ make the world less automatic, error occurs
            force value in [0,1]
        """
        if isinstance(v, Number):
            self.__set_params(2, min(max(v, 0.), 1.))

    @property
    def nbMatch(self) -> int:
        """ number of matches """
        return self.__get_params(3)
    @nbMatch.setter
    def nbMatch(self, v:int):
        """ force value to be at least 5 """
        if isinstance(v, int): self.__set_params(3, max(5, v))

    @property
    def min_iter(self) -> int:
        """ number of min iteration """
        return self.__get_params(4)
    @min_iter.setter
    def min_iter(self, v:int):
        """ force value to be at least 1 and at most max_iter -1 """
        if isinstance(v, int):
            self.__set_params(4, min(max(1, v), self.max_iter-1))

    @property
    def max_iter(self) -> int:
        """ number of max iterations """
        return self.__get_params(5)
    @max_iter.setter
    def max_iter(self, v:int):
        """ force value to be at least min_iter+1 """
        if isinstance(v, int):
            self.__set_params(5, max(self.min_iter+1, v))

    @property
    def parameters(self) -> str:
        """ all parameters at once """
        _latt = "model random_state noise nbMatch min_iter max_iter"
        _str =''
        for k,v in zip(_latt.split(), self.__sim_params):
            _str += f">> {k:<15s} -> {v}\n"
        return _str
    
    @parameters.setter
    def parameters(self, values:Iterable):
        """ global parameters' setter """
        _latt = "model random_state noise nbMatch min_iter max_iter"
        for att,v in zip(_latt.split(), values):
            setattr(self, att, v)

    def __evaluation(self, st1:Strategy, st2:Strategy):
        """ evaluates and stores """
        _1 = self.__scores.get((st1.idnum, st2.idnum), None)
        if _1 is None:
            _1 = evaluation(st1, st2, self.nbMatch, self.min_iter,
                            self.max_iter, self.model, self.noise)
            self.__scores[(st1.idnum, st2.idnum)] = _1
            self.__scores[(st2.idnum, st1.idnum)] = _1[::-1]
        return _1
            
    #======================== placement ==========================#
    def locate_agent(self, a:Strategy, x:int, y:int):
        """ set agent a in locus (x,y) """
        if a.idnum not in self.__pop:
            self.__pop[a.idnum] = a
        self.__grid[x,y] = a.idnum

    def locate_idnum(self, idnum:int, x:int, y:int):
        """ set idnum in locus (x,y) """
        if idnum in self.__pop:
            self.__grid[x,y] = idnum

    def cluster_agent(self, a:Strategy, lstOfCoords:Iterable):
        """ set agent in multiple positions """
        if a.idnum not in self.__pop:
            self.__pop[a.idnum] = a
        for x,y in lstOfCoords: self.__grid[x,y] = a.idnum

    def cluster_idnum(self, idnum:int, lstOfCoords:Iterable):
        """ set agent in multiple positions """
        if idnum in self.__pop:
            for x,y in lstOfCoords: self.__grid[x,y] = idnum

    def focus(self, *coord) -> str:
        """ get the focus at some point """
        a,b = coord
        _str = str(self.__pop[self.__grid[a,b]])+"\n"
        for x,y in self.vicinity(*coord):
            _str += "at ({}, {}) found {}\n".format(x,y,self.__grid[x,y])
        return _str

    def change_color(self, color:int, *coord):
        """ find someone and changes color value """
        agent = self.get_agent(*coord)
        if agent is not None:
            agent.color = color

    def get_agent(self, *coord) -> (Strategy, None):
        """ retrieve the agent from locus """
        a,b = coord
        return self.__pop.get(self.__grid[a,b], None)

    @property
    def free_cells(self) -> tuple:
        """ return the positions with no agent """
        return tuple([self.__p2c(p) for p in range(self.area)
                      if self.get_agent(*self.__p2c(p)) is None])

    def random_placement(self):
        """ each agent will be randomly placed """
        _n = len(self.__strategies)
        _places = random.sample(self.free_cells, k=min(_n, self.area))
        _who = list(range(_n))
        random.shuffle(_who)
        for a,p in zip(_who, _places):
            self.locate_agent(self.__strategies[a], *p)
    #======================== eval part ==========================#
    def oneStep(self, stepByStep:bool=False) -> bool:
        """
           foreach cell compute the average score
           foreach cell 
              find the highest val in neighborhood
              replace the idnum by one of the highest
           :return: True if no change, False otherwise

        ex: 7, 5, 2 0 // vicinity = von Neumann, fixe
        g b b
        g g b
        5+0 7+7+2 2+2 => 2.5 5.3 2    => b     b     b
        5+5 5+0+0 7+2    5   1.6 4.5     g     b     b
        0   0     0      0   0   0       (5,0) (1.6) (0,4.5)
        """

        if self.model is None:
            print("a Model is required, process halted ...")
            return False
        # we have a grid[idnum] to scan
        # self.__scores memorize values
        _scores = np.zeros(shape = (self.nb_lines, self.nb_columns))
        for i in range(self.nb_lines):
            for j in range(self.nb_columns):
                _nb = 0
                _agent = self.get_agent(i,j)
                if _agent is None: continue
                _others = self.vicinity(i,j)
                for a,b in _others:
                    _adv = self.get_agent(a,b)
                    if _adv is None: continue
                    _scores[i,j] += self.__evaluation(_agent, _adv)[0]
                    _nb += 1
                if _nb > 0: _scores[i,j] /= _nb

        # knowing _scores we have to dispatch info

        if stepByStep:
            print("\tscores\n{}".format(grid(np.round(_scores,2))))
            
        _grid = np.zeros(shape = (self.nb_lines, self.nb_columns),
                         dtype=int)
        for i in range(self.nb_lines):
            for j in range(self.nb_columns):
                _0 = max([_scores[a,b] for a,b in self.vicinity(i,j)])
                if _0 <= _scores[i,j]: # old resident stays
                    _grid[i,j] = self.__grid[i,j]
                else: # choose one of the best
                    _grid[i,j] = random.choice([ self.__grid[a,b]
                                                for a,b in self.vicinity(i,j)
                                                if _scores[a,b] == _0])
        _rep = np.all([self.__grid == _grid])
        self.__grid = _grid # change repartition
        return _rep

    def __p2c(self, pos:int) -> tuple:
        """ given 1D loc provides 2D loc """
        return pos//self.nb_columns, pos%self.nb_columns
    def __c2p(self, *coord) -> int:
        """ given 2D loc provides 1D loc """
        return coord[0]*self.nb_columns+coord[1]
    def __rand_vicinity(self, *coord) -> tuple:
        """ given 2D loc provides some random ennemies """
        p = self.__c2p(coord[0], coord[1])
        _l = set(range(self.area))
        _l.discard(p)
        return tuple([self.__p2c(x)
                for x in random.sample(list(_l), k=self.__sz_vicinity)])
    
    def oneRandStep(self, stepByStep:bool=False) -> bool:
        """
           foreach cell compute the average score
           foreach cell 
              find the highest val in neighborhood
              replace the idnum by one of the highest
           :return: True if no change, False otherwise
        """

        if self.model is None:
            print("a Model is required, process halted ...")
            return False
        # we have a grid[idnum] to scan
        # self.__scores memorize values
        _scores = np.zeros(shape = (self.nb_lines, self.nb_columns))
        _vicinity = [None for i in range(self.area)]
        for i in range(self.nb_lines):
            for j in range(self.nb_columns):
                _nb = 0
                _agent = self.get_agent(i,j)
                _others = self.__rand_vicinity(i,j)
                _vicinity[self.__c2p(i,j)] = _others
                if _agent is None: continue # pas de match
                for a,b in _others:
                    _adv = self.get_agent(a,b)
                    if _adv is None: continue
                    _scores[i,j] += self.__evaluation(_agent, _adv)[0]
                    _nb += 1
                if _nb > 0: _scores[i,j] /= _nb

        # knowing _scores we have to dispatch info

        if stepByStep:
            print("\tscores\n{}".format(grid(np.round(_scores,2))))
            
        _grid = np.zeros(shape = (self.nb_lines, self.nb_columns),
                         dtype=int)
        for i in range(self.nb_lines):
            for j in range(self.nb_columns):
                _voisins = _vicinity[self.__c2p(i,j)]
                if _voisins is None: continue
                _0 = max([_scores[a,b] for a,b in _voisins])
                if _0 <= _scores[i,j]: # old resident stays
                    _grid[i,j] = self.__grid[i,j]
                else: # choose one of the best
                    _grid[i,j] = random.choice([ self.__grid[a,b]
                                for a,b in _vicinity[self.__c2p(i,j)]
                                                if _scores[a,b] == _0])
        _rep = np.all([self.__grid == _grid])
        self.__grid = _grid # change repartition
        return _rep

    def loop(self, atMost:int=100, kind:bool=True,
             stepByStep:bool=True, withPlot:bool=False) -> (list, np.array):
        """ 
           atMost: number max of iteration
           kind: True 'oneStep', False 'oneRandStep'
           stepByStep: True stop at each generation and display world data
           withPlot: True plot the evolution

           algorithm:
           k = 0 ; stable = False
           display
           repeat
               stable = oneXXX
               display
               population update
               k ++
            until k == atMost or stable
            return (order, tuple(array))
        """
        random.seed(self.random_state)
        _one = self.oneStep if kind else self.oneRandStep
        _iter = 0 ; _stability = False
        _order = ['vide']
        _order.extend(sorted(self.__pop.keys()))
        _evol = []
        _current = self.population
        _evol.append([_current.get(x, 0) for x in _order])
        while _iter < atMost and not _stability:
            _msg = "start" if _iter == 0 else "iter {:03d}".format(_iter)
            if stepByStep: print("{}\n{}".format(_msg, self))
            _stability = _one(stepByStep)
            _current = self.population
            if stepByStep:
                print("repartition", _current) 
            _evol.append([_current.get(x, 0) for x in _order])
            if stepByStep and not _stability: input("<next step>")
            _iter += 1

        _h = np.array(_evol[:], dtype=int)

        # and now the graph of evolution
        # if HASPLOT is True and withPlot is 'on'
        if HASPLOT and withPlot:
            fig = plt.figure()
            _str = "{} [{}]"
            ax = fig.add_subplot(1,2,1)
            for i,x in enumerate(_order):
                if x == 'vide': ax.plot(_h[:,i], label='{}'.format(x))
                else:
                    ax.plot(_h[:,i],
                            label=_str.format(
                                self.__pop[x].__class__.__name__,
                                x))
            ax.set_xlabel('generations')
            ax.set_ylabel('population  with noise {}'
                          ''.format(self.noise))
            ax.set_title('Evolution of population with {} vicinity'
                         ''.format("structured" if kind else "random"))
            # (0,0) en bas à gauche
            # (1,0) en bas à droite
            plt.legend(bbox_to_anchor=(1.05, .75),
                       loc='best', borderaxespad=0.1)
            plt.grid(True)
            plt.show()

        return _order, _h
            
            
            
    def plot_simulation(self, atMost:int=100, stepByStep:bool=False,
                        noise:float=1e-2):
        """
           4 simulations are done and plotted
             - with vicinity, with and without noise
             - without vicinity, with and without noise
        """
        def do_plot(idx:int, ax:np.array, datas:tuple):
            """ sub meth devoted to plot """
            _noise, _order, _h = datas
            _str = "{} [{}]"
            for i,x in enumerate(_order):
                if x == 'vide': ax.plot(_h[:,i], label='{}'.format(x))
                else:
                    ax.plot(_h[:,i],
                            label=_str.format(
                                self.__pop[x].__class__.__name__,
                                x))

            if idx >= 2:
                ax.set_xlabel('generations')
            if idx%2 == 0:
                ax.set_ylabel('population with noise {}'
                              ''.format(_noise))
            if idx < 2:
                ax.set_title('Evolution of population with {} vicinity'
                            ''.format("structured" if idx == 0 else "random"))
            ax.grid(True)
            
        if not HASPLOT:
            print("No plotting available, stop")
            return
        
        _old = self.noise
        # 1st collect datas
        self.save() # we need to spare the current state
        _values = []
        for _noise in (0., noise):
            self.noise = _noise
            for kind in (True, False):
                _1 = [_noise]            
                _1.extend(self.loop(atMost, kind, stepByStep, True))
                _values.append(_1)
                self.restore()

        self.noise = _old
        # 2nd go for plotting
        fig = plt.figure()
        axes = [fig.add_subplot(2,2,i+1) for i in range(4)]
        for i in range(4):
            do_plot(i, axes[i], _values[i])
        plt.legend(bbox_to_anchor=(0.05, 0.75), loc='best', borderaxespad=0.1)
        plt.show()
