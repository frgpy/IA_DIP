#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "12.02.20"
__update__ = "02.02.24 11:55"
__usage__ = """ 

    CAUTION: we assume that the 'language' of actions is restricted to
    {'C', 'D' 'R'} where 
        C stands for Cooperate, D for Defect, R for Renouncement

    This code contains a lot of print, to get a silent process
    set DEBUG as False or call python with -O

    the noise parameter (epsilon)
    given strategies, it changes the action C <-> D at low rate
    as its default value is 0, the evaluations are free from noise

    the random_state (default is None) can be useful for replication
    if None, no replication available since seed is based on clock


    * eco_evol(nbIter, lstOfStrat, szPop, nbMatch, min_iter, max_iter, model,
               epsilon, random_state)
    it is a battle many against many with population evolution
    pop evolves according to their scores against the others
    to accelerate the process, one true battle is done, then we adjust
    the results according to the pop at hand
    if matplotlib is present, draw the pop evolution

"""


#--------------- import -----------------#
try:
    from evaluations import *
except:
    from tools.evaluations import *

try:
    import numpy as np
except:
    print("numpy is required")
    
try:
    import matplotlib.pyplot as plt
    HASPLOT = True
except:
    HASPLOT = False
    
DEBUG = __debug__
#========================================#

def eco_evol(nbIter:int, lstOfStrat: Iterable,
             szPop:Iterable=[],
             nbMatch:int=5, min_iter:int=10, max_iter:int=100,
             model:Model=m2, epsilon:float=0,
             random_state:int=None) -> np.array:
    """
        compute the evolution of population during nbIter generations
        the trick is to compute _scores once and update according to
        the respective size of Pop
        szPop is the start of pop for each species
        epsilon: amount of noise during battles
        random_state: value for replication ; None=no replication
        @return the evolution of the pop for each species
    """
    if len(lstOfStrat) != len(szPop):
        _szPop = {_.idnum:10 for _ in lstOfStrat}
    else: _szPop = {_.idnum:v for _,v in zip(lstOfStrat, szPop)}
    _initial_pop = sum(_szPop.values())
    _nbM = max(5, nbMatch) # at least 5 matches
    _h = np.zeros(shape=(nbIter+1, len(_szPop)))
    # 0 initiate the seed
    random.seed(random_state)
    # 1 perform tournament
    _scores = {}
    _who = {x.idnum: set([y.idnum for y in lstOfStrat]) for x in lstOfStrat}
    # 3 perform multi_eval

    for w in lstOfStrat:
        lst = [x for x in lstOfStrat if x.idnum in _who[w.idnum]]
        for _ in lstOfStrat: _who[_.idnum].discard(w.idnum)
        _score = multi_eval(w, lst, _nbM, min_iter, max_iter, model, epsilon)
        for x,v in _score: #idnum, (v1, v2)
            _scores[(w.idnum, x)] = v[0]
            _scores[(x, w.idnum)] = v[1]

    if DEBUG:
        print("résultat 1 contre 1")
        print(_scores)
    # _scores are known for each, we can simulate evolution
    for i in range(nbIter):
        _h[i,:] = [_[1] for _ in sorted(_szPop.items())] # oldpop
        _global_pop = np.sum(_h[i,:])
        if DEBUG: print("pop avant {:2d} {}".format(i, _global_pop))
        _score_gen = {}
        _score_iter = {}
        for _0,w in enumerate(_who):
            _score_gen[ (w, w) ] = _scores[(w,w)] * _szPop[w]**2
            for _1,x in enumerate(_who):
                if _1 <= _0: continue
                _pop_wx = _szPop[w] * _szPop[x]
                _score_gen[(w,x)] = _scores[(w,x)] * _pop_wx
                _score_gen[(x,w)] = _scores[(x,w)] * _pop_wx

            _score_iter[w] = sum([_score_gen[(w,_)] for _ in _who])
        if DEBUG: print('scores', sorted(_score_iter.items()))
        # update pop
        _score_total = sum(_score_iter.values())
        for _ in _szPop:
            _szPop[_] = _initial_pop * _score_iter[_] / _score_total

    _h[-1,:] = [_[1] for _ in sorted(_szPop.items())] # lastpop

    # and now the graph of evolution
    if HASPLOT:
        fig = plt.figure()
        _str = "{} [{}]"
        ax = fig.add_subplot(1,1,1)
        for j,l in enumerate(lstOfStrat):
            ax.plot(_h[:,j], label=_str.format(l.__class__.__name__, l.idnum))
        ax.set_xlabel('générations')
        ax.set_ylabel('population')
        ax.set_title('Evolution of population with noise {}'.format(epsilon))
        ax.legend(loc='best')
        plt.show()

    return _h

if __name__ == "__main__":
    print(__usage__)
