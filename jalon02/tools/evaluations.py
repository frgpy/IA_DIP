#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "12.02.20"
__update__ = "16.01.24 19:15"
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

    * evaluation(st1, st2, nbMatch, min_iter, max_iter, model, epsilon)
    except the 1st 2 parameters, all have default values
    stop computation as soon as one 'Renoncement' found
    it corresponds to a battle one against one
 
    * multi_eval(st1, lstOfStrat, nbMatch, min_iter, max_iter, model, epsilon)
    it corresponds to a battle (evaluation) one against many

    * tournament(lstOfStrat, nbMatch, min_iter, max_iter, model, 
                 epsilon, random_state)
    it is a battle many against many, no evolution, it's a snapshot

    * learning is identical to evaluation, except that the 1st
      strategy is required to be a learner

    * adaptive_evaluation:
        if any strategy is a learner -> learning
        otherwise -> evaluation
"""


#--------------- import -----------------#
import random
from typing import Iterable

try:
    from model import Model, m1, m2
except:
    try:
        from tools.model import Model, m1, m2
    except:
        print("model.py is missing")
try:
    from base import Strategy
except:
    try:
        from tools.base import Strategy
    except:
        print("No class 'Strategy' found")
        Strategy = 'Strategy'
    
DEBUG = __debug__
#========================================#

def evaluation(st1:Strategy, st2:Strategy, nbMatch:int=10, 
               min_iter:int=1, max_iter:int=100, model:Model=m2,
               epsilon:float=0) -> tuple:
    """ given 2 Strategies st1, st2
        given nbMatch [the encounter repetition]
        given min_iter, max_iter [the interval length of encounters]
        given a Model model [with or without giving up]

        return the points for st1 and st2 of nbMatch with at least min_iter 
        at most max_iter iterations, their might be miscomprehension if
        epsilon is not 0
    """
    _epsilon = min(max(epsilon, 0), 1) # 0 <= eps <= 1
    rewards = model.rewards
    valeurs = model.values
    _sts = st1, st2
    total_st = [0, 0]
    total_iter = 0
    total_noise = [0, 0]
    for i in range(nbMatch):
        eval_st = [0,0]
        for k in range(2): _sts[k].reset() # reset the info
        nb_iter = random.randrange(min_iter, max_iter) # random val

        total_iter += nb_iter
        for j in range(nb_iter):
            _act = [_sts[k].next_action() for k in range(2)]
            for k in range(2):
                if DEBUG and hasattr(_sts[k], 'state'):
                    print(f"Tour {j+1}, state = {_sts[k].state}"
                          f" prediction = {_sts[k].make_prediction()}")
                # noisy communication
                if _act[k] in "CD" and random.random() <= _epsilon:
                    total_noise[k] += 1
                    _act[k] = "CD"[("CD".index(_act[k])+1)%2]
            gains = rewards[''.join(_act)]
            for k in range(2): _sts[k].get_reward(gains[k])
            if "R" in _act: break # stop the computation
        if DEBUG and total_noise != [0,0]:
            print("Match {}, noises {}".format(i+1, total_noise))
        # do the numeric part of the played games
        for k in range(2):
            eval_st[k] += sum([valeurs[key]*v
                                for (key, v) in _sts[k].history()])
        # do the numeric part for the unplayed games
        if j < nb_iter-1:
            for k in range(2):
                eval_st[k] += valeurs['A']*(nb_iter -j-1)
                
        # compute the average
        for k in range(2): total_st[k] += eval_st[k]/nb_iter

    # if strategies are identical, the total is twice the value
    if st1 == st2:
        total_st[0] = total_st[1] = total_st[0]/2
    if DEBUG:
        if total_noise == [0,0]:
            print(f"{nbMatch=} noise free")
        else:
            print("Match {}, noises {}".format(nbMatch, total_noise))
    # mean score
    mean_st = [ round(total_st[k] / nbMatch, 3) for k in range(2) ]
    return tuple(mean_st)


def multi_eval(st1:Strategy, lstOfStrat:Iterable,
               nbMatch:int=10, min_iter:int=1, max_iter:int=100,
               model:Model=m2, epsilon:float=0) -> list:
    """ we want to perform a multi-evaluation
        st1: the strategy we are focusing on
        lstOfStrat: iterable of Strategies
        nbMatch, min_iter, max_iter, model are required for evaluation
        default model is set to the 3 actions situations
        default battle is noise free (epsilon=0)
    """
    _scores = {}
    for adv in lstOfStrat:
        _scores[adv.idnum] = adaptive_evaluation(st1, adv, nbMatch,
                                        min_iter, max_iter, model, epsilon)
    return sorted(list(_scores.items()), key=lambda x:x[0])


def tournament(lstOfStrat:Iterable,
               nbMatch:int=10, min_iter:int=1, max_iter:int=100,
               model:Model=m2, epsilon:float=0,
               random_state:int=None) -> list:
    """
       compute the scores among n species
       epsilon is the amount of noise during battle
       random_state specified you can reproduce the results
            None means: no replication
    """
    #1 initiate the seed
    random.seed(random_state)
    # 2 initiate local vars
    _scores = {}
    _who = {x.idnum: set([y.idnum for y in lstOfStrat]) for x in lstOfStrat}
    # 3 perform multi_eval

    if DEBUG: _match = {x.idnum:0 for x in lstOfStrat}

    for w in lstOfStrat:
        lst = [x for x in lstOfStrat if x.idnum in _who[w.idnum]]
        for _ in lstOfStrat: _who[_.idnum].discard(w.idnum)
        _score = multi_eval(w, lst, nbMatch, min_iter, max_iter, model, epsilon)
        if DEBUG: print(">> résultat ", _score)
        for x,v in _score: #idnum, (v1, v2)
            _scores[w.idnum] = _scores.get(w.idnum, 0)+v[0]
            if x != w.idnum: # do not count twice
                _scores[x] = _scores.get(x, 0)+v[1]
            if DEBUG:
                _match[w.idnum] += 1 
                if x != w.idnum: _match[x] +=1

    if DEBUG:  print(">> rencontres ", _match)
    return sorted(list(_scores.items()), key=lambda x:x[0])
            

def is_learner(st:Strategy):
    """ find if some strategy has the appropriate attributes 
        to be considered as learner
    """
    _latt = "good_guess default_behavior reset_learning rate"
    return all([hasattr(st, att) for att in _latt.split()])

def learning(st1:Strategy, st2:Strategy, nbMatch:int=10, 
               min_iter:int=1, max_iter:int=100, model:Model=m2,
               epsilon:float=0) -> tuple:
    """ given 2 Strategies st1, st2
              requires st1 to be a learner
        given nbMatch [the encounter repetition]
        given min_iter, max_iter [the interval length of encounters]
        given a Model model [without or with action 'GiveUp']

        return the points for st1 and st2 of nbMatch with at least min_iter 
        at most max_iter iterations, their might be miscomprehension if
        epsilon is not 0
    """
    if not is_learner(st1):
        raise TypeError("'{}' is not a learner".format(st1.__class__.__name__))

    _st2_learner = is_learner(st2)

    if _st2_learner and st1 == st2:
        raise ValueError("can't have the same instance for both")
        
    _epsilon = min(max(epsilon, 0), 1)
    rewards = model.rewards
    valeurs = model.values
    _sts = st1, st2
    total_st = [0, 0]
    total_iter = 0
    total_noise = [0, 0]
    total_guess = [] if not _st2_learner else [ [], [] ]
    total_default = [] if not _st2_learner else [ [], [] ]
    st1.reset_learning()
    if _st2_learner: st2.reset_learning()
    for i in range(nbMatch):
        eval_st = [0,0]
        for k in range(2): _sts[k].reset() # reset the info
        nb_iter = random.randrange(min_iter, max_iter)

        total_iter += nb_iter
        for j in range(nb_iter):
            _act = [_sts[k].next_action() for k in range(2)]
            for k in range(2):
                if _act[k] in "CD" and random.random() <= _epsilon:
                    total_noise[k] += 1
                    _act[k] = "CD"[("CD".index(_act[k])+1)%2]
            gains = rewards[''.join(_act)]
            for k in range(2): _sts[k].get_reward(gains[k])
            if "R" in _act: break # stop the computation

        # do the numeric part of the played part
        for k in range(2):
            eval_st[k] += sum([valeurs[key]*v
                                for (key, v) in _sts[k].history()])
        # do the numeric part for the unplayed part
        if j < nb_iter-1:
            for k in range(2):
                eval_st[k] += valeurs['A']*(nb_iter -j-1)
                
        # compute the average
        for k in range(2): total_st[k] += eval_st[k]/nb_iter
        # store the guesses' rate
        if not _st2_learner:
            total_guess.append(st1.rate)
            total_default.append(st1.default_behavior)
        else:
            total_guess[0].append(st1.rate)
            total_default[0].append(st1.default_behavior)
            total_guess[1].append(st2.rate)
            total_default[1].append(st2.default_behavior)
            

    if DEBUG:
        print("Match {}, noises {}".format(nbMatch, total_noise))
    # if strategies are identical, the total is twice the value
    if not _st2_learner and st1.default == st2: total_st[1] /= 2
    # mean score
    mean_st = [ round(total_st[k] / nbMatch, 3) for k in range(2) ]
    return tuple(total_default), tuple(total_guess), tuple(mean_st)

def adaptive_evaluation(st1:Strategy, st2:Strategy, nbMatch:int=10, 
               min_iter:int=1, max_iter:int=100, model:Model=m2,
               epsilon:float=0) -> tuple:
    """ works as a safe switch to provide the correct call """

    if not (is_learner(st1) or is_learner(st2)):
        _rep = evaluation(st1, st2, nbMatch, min_iter, max_iter, model,
                          epsilon)
    else: # at least one learner
        if not is_learner(st1):
            _0, _1, _rep = learning(st2, st1, nbMatch, min_iter, max_iter,
                                    model, epsilon)
            _rep = _rep[1], _rep[0]
            _st_id = st2.idnum
        else:
            _st2 = st2.clone() if st1 == st2 else st2
            _0, _1, _rep = learning(st1, _st2, nbMatch, min_iter, max_iter,
                                    model, epsilon)
            _st_id = st1.idnum
            
        if len(_0) == 2:
            for _ in range(2):
                print(">> default behavior(s) strat {}: {}".format(_, _0[_]))
                print(">> good guess(es) strat {}: {}".format(_, _1[_]))
        else:
            print(">> default behavior(s) strat {}".format(_st_id), _0)
            print(">> good guess(es) strat {}".format(_st_id), _1)

    return _rep

if __name__ == "__main__":
    print(__usage__)
