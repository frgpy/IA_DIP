#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from tools.ezCLI import testcode
from tools.base import Strategy
from tools.model import Model, m1, m2
from tools.evaluations import evaluation, multi_eval, tournament
from typing import Iterable
from tools.utility import probability_vector

#============ PLACEZ VOS CODE ICI AVANT testcodes ===============#
# RAPPEL: Une classe à la fois pas de nouvelle classe
#         tant que la classe de travail n'a pas été validée avec
#         main_tests
#=================================================================#

        
#=========================== testcodes ===========================#
# Vous avez tout à fait la possibilité d'ajouter vos propres tests
#=================================================================#

def test_reward(st:Strategy):
    """ reçoit un joueur et teste la réponse pour chaque récompense 
        ::HOWTO::
        >>> s = Periodic('DDC')
        >>> test_reward(s)
    """
    st.reset() # clean situation
    print(f"{st.memory=} state -> {st.next_action()=}")
    for rew in "TSPR":
        st.get_reward(rew)
        print(f"{st.memory=} state -> {st.next_action()=}")
        
def test_periodic():
    """ tests Periodic pour J02 """
    code = '''
x = Periodic("C")
x.style == 'C'
x.memory_limit == 0
x.word == "C"
x.word = 'D' # tentative de modification provoque erreur

y = Strategy()
issubclass(x.__class__, y.__class__)

p = Periodic('')
p.__class__.__name__
p.memory_limit == 0
p.word == 'D'
p.style == 'D'
''' ; testcode(code)
    
def test_majority():
    """ tests Majority pour le J02 """
    code = '''
x = Periodic("C")
x.style == 'C'
x.memory_limit == 0
x.word == "C"
x.word == 'C'
x.word = 'D' # tentative de modification

y = Strategy()
issubclass(x.__class__, y.__class__)

p = Periodic('')
p.__class__.__name__
p.memory_limit == 0
p.word == 'D'
p.style == 'D'

u = Majority()
u.__class__.__name__
p.__class__.__name__
issubclass(u.__class__, p.__class__)
y.__class__.__name__
issubclass(u.__class__, y.__class__)
u.memory_limit
u.get_reward('T')
u.majority

for r in "TRPS": u.get_reward(r) ; print(u.majority)

u = Majority(maxsz=2)
issubclass(u.__class__, p.__class__)
u.memory_limit
u.get_reward('T')
u.majority
u.style

msg = "memory {0.memory}, maj {0.majority:+0d}"
print(msg.format(u))
for r in "PSRT": u.get_reward(r) ; print(msg.format(u),f"-> {u.next_action()}")
''' ; testcode(code)

def test_markov():
    """ tests Markov pour le J02 """
    code = '''
m = Markov() # failure

m = Markov(0, [.5, 1.]) # Fool with a few probabilities
m.probabilities
m.probabilities = [.3, .2, .5, .9]
m.probabilities[0] = .75
m.auto_test()
m.style
m.next_action()
m.memory_limit
for r in "TRPS": m.get_reward(r) ; print(f"{m.memory=} I choose {m.next_action()}")

m = Markov(0, [.5, .9, 1.5]) # Fool with a few probabilities
m.probabilities
m.auto_test()
m.style
m.next_action()
m.memory_limit
for r in "TRPS": m.get_reward(r) ; print(f"{m.memory=} I choose {m.next_action()}")
''' ; testcode(code)

def test_stochastic():
    """ tests Stochastic pour le J02 """
    code = '''
b = Stochastic([1])
b.probabilities == (1, -1, -1, -1, -1)
b.auto_test() == True
b.style == "C"
b.memory_limit == 1
b.get_probabilities('')
b.get_probabilities('R')

c = Stochastic([-1], model=m2)
c.probabilities == (-1, -1, -1, -1, -1, -1, -1, -1, -1)
c.auto_test() == True
c.style == "a"
c.memory_limit == 1
c.get_probabilities('')
c.get_probabilities('S')

d = Stochastic([-1, 1, -1, -1, 1/4, .5], model=m2)
d.probabilities == (-1, 1, -1, -1, 0.25, .5, -1, -1, -1)
d.auto_test() == False
d.style == "a"
d.memory_limit == 1
d.get_probabilities('')
d.get_probabilities('S')
d.get_probabilities('RS')

a = Stochastic( (1, 1/2, -1, -1, -1) )
a.probabilities
a.get_probabilities('T')

a = Stochastic( (1, -1, -1, -1, -1, -1, 1, -1, 2/3), m2)
a.probabilities
a.get_probabilities('S')

a = Stochastic( (1, 1/2, 1/3) )
a.probabilities
a.get_probabilities('T')

a = Stochastic( (1, 1/2, 1/3, 1/2), m1 )
a.probabilities
a.get_probabilities('T')

a = Stochastic( (1, 1/2, 1/3), m2 )
a.probabilities
a.get_probabilities('T')

a = Stochastic( (1, 1/4, 1/3, -1, 1/10, -1, -1, -1, 1), m2 )
a.probabilities
a.get_probabilities('S')

''' ; testcode(code)

def test_getproba():
    """ tests Stochastic & get_probabilities pour le J02 """
    code = '''
a = Stochastic([1, -1, -1, 0, 0])
a.get_probabilities('T') == (0,1,0)
a.get_probabilities('S') == (0,1,0)

b = Stochastic([1, -1, -1, -1, 0])
b.get_probabilities('T') == (1/2, 1/2, 0)
b.get_probabilities('S') == (0, 1, 0)

c = Stochastic((1, 1/2, 1/3, 1/2), m2)
c.probabilities
c.auto_test()
c.get_probabilities('S') == (1/2, 1/4, 1/4)
c.get_probabilities('T') == (2/3, 1/6, 1/6)
for v,w in zip(c.get_probabilities('T'),(2/3, 1/6, 1/6)): print(abs(v-w)<1e-5)

d = Stochastic((1, -1, -1, -1, -1, -1, 1, -1, 2/3), m2)
d.probabilities
d.auto_test()
d.get_probabilities('S') == (1/6, 1/6, 2/3)
for v,w in zip(d.get_probabilities('S'),(1/6, 1/6, 2/3)): print(f"{abs(v-w)}")
d.get_probabilities('T') == (0, 0, 1)
'''; testcode(code)

def test_gradual():
    """ tests Gradual pour le J02 """
    code = '''
g = Gradual(True, 1, 1) # additive, 1C, rate =1
g.make_prediction() == g.style
g.memory_limit == 1
g.memory == ''
g.state == 0
g.duplicity == 0
g.rate == 1
g.cooling == 1
g.time_left == 0
g.next_action() == 'C'

g.get_reward('S')
g.memory == 'S' # actions were CD
g.make_prediction() # dont access to memory
g.time_left # clock remains the same before next action
g.next_action() == 'D' # 'coz memory and state 0
# g should play DDC
g.state == -1
g.duplicity == 1
g.time_left == 2  # expect 3 -1
g.make_prediction()
len(g.make_prediction()) == g.time_left

g.get_reward('T')
g.memory == 'T' # actions were DC
g.make_prediction() # DC left
g.time_left == 2 # clock hasnt changed yet
g.next_action() == 'D' # clock changed, state remains
g.state == -1
g.duplicity == 1
g.time_left == 1
g.make_prediction()
len(g.make_prediction()) == g.time_left

g.get_reward('T')
g.memory == 'T' # actions were DC
g.make_prediction()
g.time_left == 1 # clock hasnt changed yet
g.next_action() == 'C' # blind state
g.state == 1
g.duplicity == 1
g.time_left == 0
g.make_prediction()
g.time_left == 0

g.get_reward('S')
g.memory == 'S' # CD
g.make_prediction() # should play C before accessing memory
g.time_left == 0 # memory hanst been seen
g.next_action() == 'D' # memory seen
g.state == -1
g.duplicity == 2
g.time_left # expect 4 -1
g.make_prediction()

''' ; testcode(code)
if __name__ == "__main__":
    for meth in (test_reward, test_periodic, test_majority,
                 test_markov, test_stochastic, test_getproba, test_gradual):
        print(f">>> {meth.__name__}:\n{meth.__doc__}\n{'='*75}")
