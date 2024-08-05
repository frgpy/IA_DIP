#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from tools.ezCLI import testcode
from tools.base import Strategy
from tools.model import Model, m1, m2
from tools.evaluations import evaluation, multi_eval, tournament
from typing import Iterable
from tools.utility import probability_vector

class Periodic(Strategy):
    """
        requires an str of length p of D|C characters
        requires str to be the shortest acyclic
           CDCD is wrong since CD is sufficient
    """ 
    def __init__(self, acyclic:str):
        self.__word = acyclic if len(acyclic) > 0 else "D"
        _styl = 1 if self.__word[0]=='C' else -1
        super().__init__(_styl)
    @property
    def word(self) -> str: return self.__word

    def next_action(self) -> str:
        return self.word[self.count%len(self.word)]

class Majority(Strategy):
    @property
    def majority(self) -> int:
        """ provides summary from memory """
        _adv = [self.adv_action(x) for x in self.memory]
        _c = _adv.count('C')
        _d = _adv.count('D')
        if _c > _d: return 1
        elif _d > _c : return -1
        else: return 0

    def next_action(self):
        """ what is the next action according to majority state """
        if self.majority == 1: return 'C'
        elif self.majority == -1: return 'D'
        elif self.style == 'a': return random.choice('CD')
        return self.style
    
class Markov(Strategy):
    """ expects a vector of length 4
        values are in [0 ; 1] U {-1}
        missing values are set to -1
        expects vector’s values to be ’probabilities’
        expects a model
    """
    def __init__(self, style:int, probas:Iterable=[], model:Model=m1):
        super().__init__(style, 1, model)
        self.__diag = None
        self.__probas = tuple(list(probas[:4]) if len(probas) > 4 else 
                list(probas)+[-1 for _ in range(len(probas), 4)])

    @property
    def probabilities(self) -> tuple:
        """ the vector of probas """
        return self.__probas
    
    def auto_test(self) -> bool:
        """ we need to perform some analysis """
        if self.__diag is None:
            self.__diag = all([ 0 <= x <= 1 or x == -1
                               for x in self.probabilities])
        return self.__diag

    def next_action(self):
        """ choose action according to probas """
        # 1st action
        if self.memory_size == 0 and self.style == 'a':
            return random.choice("CD")
        elif self.memory_size == 0: return self.style

        p = self.probabilities["TRPS".index(self.memory)]
        if p == -1: return random.choice(self.actions)
        if random.random() <= p: return "C"
        else:
            return 'D' if len(self.actions)==2 else random.choice('DR')
            
    

class Stochastic(Strategy):
    """ 
        expects a vector of length at least 1 at most 9
            values are in [0 ; 1] U {-1}
            missing values are set to -1
        expects vector's values to be 'probabilities'
        expects a model to set the length of stored vector
    """
    def __init__(self, probas:Iterable, model:Model=m1):
        """
           set the probabilities to the required length
           detect the style
           call super with the required datas
        """
        _sz = 5 if len(model.actions) == 2 else 9
        self.__probas = list(probas)[:_sz]
        self.__probas.extend([-1 for i in range(len(probas), _sz)])

        if self.__probas[0] == -1 or self.__probas[0] not in (0,1):
            _styl = 0
        else:
            _styl = 2*self.__probas[0]-1
        super().__init__(_styl, 1, model)
        # pre-test
        self.__diag = all([ (0 <= x <=1 or x == -1) for x in self.__probas])
        # is pre-test enough ?
        self.__done = (len(self.__probas) == 5)
        
    @property
    def probabilities(self) -> tuple:
        return tuple(self.__probas)

    def get_probabilities(self, rew:str) -> tuple:
        """ 
            provides the probabilities for each action
        """
        if len(rew) != 1 or rew not in self._model.reward_names:
            return tuple()

        _act = "CD"
        _me = self.my_action(rew)
        _he = self.adv_action(rew)
        _pos = [_act.index(_me)+1, _act.index(_he)+3]
        if len(self.__probas) != 5: _pos.extend([_+4 for _ in _pos])
        _pr = [self.__probas[_] for _ in _pos]
        return probability_vector(*_pr)

    def auto_test(self) -> bool:
        """ we need to perform some analysis """
        # if we know its wrong say it
        if not self.__diag: return self.__diag
        # if we have already checked say it
        if self.__done: return self.__diag
        # regarder 2/6 .. 5/9 (-1)
        self.__diag = all([(self.__probas[i] + self.__probas[i+4] <= 1)
                           for i in range(1, 5)])
        # all tests have been performed
        self.__done = True
        return self.__diag

    def next_action(self):
        """ find the good recipe """
        if self.memory_size == 0:
            _1st = self.probabilities[0]
            if _1st == -1: return random.choice('CD')
            if _1st == 0: return 'D'
            if _1st == 1: return 'C'
            if random.random() <= _1st: return 'C'
            return 'D'
        else:
            _proba = self.get_probabilities(self.memory[-1])
            return random.choices("CDR", _proba)[0] # r.choices return a list


#============== Agent emotionnel =========================#
class Gradual(Strategy):
    def __init__(self, mode:bool, cool:int, rate:int,
                 abort:int=0, model:Model=m1):
        """
        mode: boolean defines (+) or (*) reaction 
        cool: period of calm
        rate: the rate of the emotional law
        abort: the threshold to give up 
        law will be defined as
            adversary_duplicity mode rate + cool

        provides:
        > state:  -1 (rage), 0 (neutral), 1 (cool)
        > duplicity: count adversary 'D'
        > additive: True (+), False (*)
        > rate: int > 0
        > cooling: int > 0 length of 'C'
        > abort: int
        > time_left: clock before state = 0
        """
        super().__init__(1, 1, model)
        self.__state = 0
        self.__duplicity = 0
        self.__linear = mode
        self.__cooling = max(1, cool)
        self.__rate = max(1, rate)
        self.__clock = 0
        self.__abort = abort

    def reset(self):
        super().reset()
        self.__state = 0
        self.__duplicity = 0
        self.__clock = 0

    @property
    def state(self) -> int: return self.__state
    @property
    def abort(self) -> int: return self.__abort
    @property
    def duplicity(self) -> int: return self.__duplicity
    @property
    def additive(self) -> bool: return self.__linear
    @property
    def cooling(self) -> int: return self.__cooling
    @property
    def rate(self) -> int: return self.__rate
    @property
    def time_left(self) -> int: return self.__clock

    def make_prediction(self) -> str:
        """ prediction of next actions, given state and clock
            this dont use the memory
        """
        if self.state == 0: return self.style
        elif self.state == 1: return 'C'*(self.cooling - self.time_left)
        elif self.duplicity >= self.abort and len(self.actions)==3:
            return 'R'
        return 'D'*(self.time_left - self.cooling)+'C'*self.cooling

    def next_action(self) -> str:
        """ decides what is the next action to provide
        if memory is empty play 'C'
        else: consider current state and memory
        """
        # state
        if self.time_left == 0: self.__state = 0
        elif self.time_left == self.cooling : self.__state = 1
        # action
        if self.memory_size == 0: _act = self.style
        elif self.state == 1: _act = self.style
        elif self.memory[-1] in "SP":
            self.__duplicity += 1
            self.__state = -1
            if self.duplicity == self.abort and len(self.actions) == 3:
                _act = 'R'
            else:
                if self.additive:
                    self.__clock = (self.duplicity + self.rate) + self.cooling
                else:
                    self.__clock = (self.duplicity * self.rate) + self.cooling
                _act = 'D'
        elif self.state == -1: _act = 'D'
        else: _act = 'C'
        # clock is ticking
        self.__clock = max(0, self.__clock -1)
        return _act

#=========================== testcodes ==========================#
# Vous avez tout à fait la possibilité d'ajouter vos propres tests
#=================================================================#

def test_reward(st:Strategy):
    """ reçoit un joueur et teste la réponse pour chaque récompense 
        ::HOWTO::
        >>> s = Periodic('DDC')
        >>> test_reward(s)
    """
    st.reset() # clean situation
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
x.word == 'C'
x.word = 'D' # tentative de modification ratée

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
x.word = 'D' # tentative de modification ratée

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

