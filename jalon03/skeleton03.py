#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from tools.ezCLI import testcode
from tools.base import Strategy, AbstractLearner
from tools.model import Model, m1, m2
from tools.evaluations import evaluation, multi_eval, tournament, learning
from tools.utility import update_storage, backward_search, adv_memory

#============ PLACEZ VOS CODE ICI AVANT testcodes ===============#
# RAPPEL: Une classe à la fois pas de nouvelle classe
#         tant que la classe de travail n'a pas été validée avec
#         main_tests
#=================================================================#

    
#=========================== testcodes ===========================#
# Vous avez tout à fait la possibilité d'ajouter vos propres tests
#=================================================================#

def test_reward(st:Strategy):
    """ given some Strategy, tests action after each possible reward
        ::HOWTO::
        >>> s = Periodic('DDC')
        >>> test_reward(s)
    """
    st.reset() # clean situation
    for rew in "TSPR":
        st.get_reward(rew)
        print(f"{st.memory=} state -> {st.next_action()=}")

def test_automaton(prog:int, actions:Iterable='CD', model:Model=m1):
    """ basic test for Automaton 
    requires prog an int, actions an Iterable
    ::HOWTO::
    >>> test_automaton(5)
        build a random code of len 5 with default action 'CD'
    >>> test_automaton(5, 'ABC')
        build a random code of len 5 with actions in 'ABC'
    >>> test_automaton(13, m2.actions, m1)
        build a random code of len 13 with actions RCD and model m1
    """
    def local_run(agent, reward:str):
        t = agent.count
        m = agent.memory
        i = agent.encoding(m)-1
        a = agent.next_action()
        agent.get_reward(reward)
        print(f"time = {t}, mem={m}, action={a} vs {agent.rules[i]}")
        
    code = '''
import random
my_prog = random.choices(actions, k=prog)
len(my_prog) == prog # expect True
all([x in actions for x in my_prog]) # expect True

a = Automaton(-1, my_prog, m1) # focus on model m1
a.style
a.rules
a.memory_limit
a.auto_test()
a.next_action() == 'D'

a = Automaton(1, my_prog, m2) # focus on model m2
a.style
a.rules
a.memory_limit
a.auto_test()
a.next_action() == 'C'

a = Automaton(-1, my_prog, model) # focus on model provided
a.style
a.rules
a.memory_limit
a.auto_test()
a.next_action() == 'D'
a.get_reward('P')
for r in "TTRPSTRPP": local_run(a, r)
''' ; testcode(code)

def test_mime(st:Strategy):
    """ given some Strategy, mimics with Mime """
    code = '''
m = Mime(st)
st.memory_limit
m.memory_limit
m.default.memory_limit

m.next_action()
m.default.next_action()

m.rules_system

m = Mime(Fool())
learning(m, st, 5, 50, 51)
m.rules_system

learning(m, st, 5, 50, 51, epsilon=.1)
m.rules_system
''' ; testcode(code)

def test_motif(st:Strategy):
    """ given some Strategy, mimics with Motif """
    def simulation(rewards) -> Motif:
        """ given many rewards play a fake game """
        o = Motif(Gentle(), 15)
        for r in rewards:
            _ = o.next_action()
            o.get_reward(r)
        return o
    code = '''
m = Motif(st, memsz)
st.memory_limit
m.memory_limit
m.default.memory_limit

m.next_action()
m.default.next_action()
m.rules_system

m = Motif(Fool(), memsz)
learning(m, st, 5, 50, 51)
m.rules_system

learning(m, st, 5, 50, 51, epsilon=.1)
m.rules_system

rew = "TPRPRTTPR RSTPRSPRSTPRS RRRRRR".split()
pat = "TPR TPRS RRRRR".split()
act = "DDC"

o = simulation(rew[0])
_1 = o.next_action() # update pattern
_0 = o.rules_system 
pat[0] in _0
act[0] == _1

o = simulation(rew[1])
_1 = o.next_action() # update pattern
_0 = o.rules_system 
pat[1] in _0
act[1] == _1

o = simulation(rew[2])
_1 = o.next_action() # update pattern
_0 = o.rules_system 
pat[2] in _0
act[2] == _1
''' ; testcode(code)

def test_shannon(st:Strategy):
    """ given some Strategy, mimics with Shannon """
    code = '''
m = Shannon(st)
st.memory_limit
m.memory_limit
m.default.memory_limit

m.next_action()
m.default.next_action()

m.rules_system

m = Shannon(Fool())
learning(m, st, 5, 50, 51)
m.rules_system
m.last_index
m.shannon_memories

learning(m, st, 5, 50, 51, epsilon=.1)
m.rules_system
m.last_index
m.shannon_memories
''' ; testcode(code)
    
if __name__ == "__main__":
    for meth in (test_reward, test_automaton,
                 test_mime, test_motif, test_shannon):
        print(f">>> {meth.__name__}:\n{meth.__doc__}\n{'='*75}")

    random.seed(42)
    
    class Gentle(Strategy):
        """ always C """
        def next_action(self): return self.style
    class Bad(Strategy):
        """ always D """
        def __init__(self):
            super().__init__(-1)
        def next_action(self): return self.style
    class Fool(Strategy):
        """ always D """
        def __init__(self):
            super().__init__(0)
        def next_action(self):
            return random.choice(self.actions)
        
    class Tit4Tat(Strategy):
        """ starts with C then plays what has played adv """
        def __init__(self, m:Model=m1):
            return super().__init__(1, 1, m)
        def next_action(self):
            if self.memory_size == 0: return self.style
            return self.adv_action(self.memory)
