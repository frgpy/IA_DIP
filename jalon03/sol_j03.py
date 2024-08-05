#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from tools.ezCLI import testcode
from tools.base import Strategy, AbstractLearner
from tools.model import Model, m1, m2
from tools.evaluations import evaluation, multi_eval, tournament, learning
from typing import Iterable
from tools.utility import update_storage, backward_search, adv_memory
import itertools

class Automaton(Strategy):
    """
    need a default behavior
    need a string of actions wrt model.actions (no verification)
         the string is of len sum(4**i for i in range(memory_limit)
    0, 4, 16, 64, 256
    -> 0, 4, 16+4, 64+16+4, 256+64+16+4
    need a model, default is 2actions' model
    """
    def __init__(self, styl:int, rules:str, model:Model=m1):
        """ memory_limit is defined as the smallest int with no missing
            values
        """
        _szr = len(rules)
        _sz = [sum([4**j for j in range(i)])-1 for i in range(1,6)]
        #similaire à [0, 4, 4+16, 20+64, 84+256]
        _mem = 0
        while _szr > _sz[_mem] and _mem < 4: _mem += 1
        if _szr != _sz[_mem] : _mem -= 1
        super().__init__(styl, _mem, model)
        # ne garde que les valeurs correctes
        self.__rules = rules[:_sz[_mem]]
        # crée une variable booléenne qui vérifie que les actions sont bonnes
        self.__diag = all([x in self.actions for x in self.__rules])

    @property
    def rules(self) -> str: return self.__rules
    def auto_test(self) -> bool: return self.__diag
    def next_action(self) -> str:
        if self.memory_size == 0:
            if self.style =='a': return random.choice("CD")
            return self.style
        return self.rules[self.encoding(self.memory)-1]
        

class Mime(AbstractLearner):
    """ observe opponent behavior """

    def reset_learning(self):
        """ this is where specific variables are initialized
            when we want to learn a NEW behavior
        """
        self.__rules = [0 for _ in range(85)]
        self.__changed = True
        self.__steps = 0
    
    def next_action(self) -> str:
        """ my action by default if no observation made """
        _i = self.encoding(adv_memory(self.memory))
        _act = self.__rules[_i]
        if _act != 0: return _act
        # else
        self.default_behavior += 1
        return self.default.next_action()

    def update_knowledge(self, rew):
        """ what to do for learning """
        self.__steps += 1
        if __debug__ and self.__changed:
            print(f">> avant step {self.__steps:02d}")
            print(self.rules_system)
        _i = self.encoding(adv_memory(self.memory))
        _his = self.adv_action(rew)
        self.__changed = True
        if self.__rules[_i] == _his:# if equal then != 0 then used
            self.good_guess += 1
            self.__changed = False
        self.__rules[_i] = _his
        if __debug__ and self.__changed:
            print(f">> après\n{self.rules_system}")

    @property
    def learned_rules(self) -> tuple:
        ''' just a property '''
        return tuple(self.__rules)

    def build_automaton(self) -> Automaton:
        ''' return style {1,-1}, rules(size 84) '''
        # non set rules are set to style aka head
        head, tail = self.learned_rules[0], self.learned_rules[1:]
        rules = ''.join([x if isinstance(x,str) else head
                         for x in tail])
        style = 2*int(head=='C')-1
        return Automaton(style, rules, self._model)

    @property
    def rules_system(self) -> str:
        _str = ''
        for i,x in enumerate(self.__rules):
            if self.__rules[i] == 0: continue
            if i == 0: _str += f"vide --> {x}\n"
            else: _str += f"{self.decoding(i):<4s} --> {x}\n"
        return _str

class Motif(AbstractLearner):
    """ similar pattern have similar consequence """

    def specific_reset(self):
        """ this is where specific variables are initialized
            when we want to learn a NEW behavior
        """
        self.__last = None
        self.__pattern = ''
        
    def reset_learning(self):
        """ this is where specific variables are initialized
            when we want to learn a NEW behavior
        """
        self.__working_memory = ''
        
    def next_action(self) -> str:
        """ search in memory backward """
        _last, _v = backward_search(self.__working_memory)
        if _last == []:
            self.__pattern = ''
            self.__last = None
            self.default_behavior += 1
            return self.default.next_action()
        else:
            self.__pattern = self.__working_memory[-_v:]
            _act = [self.adv_action(self.__working_memory[_+1]) for _ in _last]
            _C = _act.count('C') ; _D = _act.count('D')
            if _C > _D:    self.__last = 'C' ; return 'C'
            elif _D > _C:  self.__last = 'D' ; return 'D'
            else:
                self.__last = None
                self.default_behavior += 1
                return self.default.next_action()

    def update_knowledge(self, rew):
        """ what to do for learning """
        _his = self.adv_action(rew)
        if _his == self.__last: self.good_guess += 1
        self.__working_memory = update_storage(self.__working_memory,
                                               rew, self.memory_limit)
            

    @property
    def rules_system(self) -> str:
        """ last pattern found """
        szp, szw = len(self.__pattern), len(self.__working_memory)
        return (f"last pattern found: '{self.__pattern}'\n"+
                f"size: {szp} memory {szw}")

class Shannon(AbstractLearner):
    """ Observe behavior after win/loss """

    def specific_reset(self):
        """ this is where specific variables should be initialized 
            after each Match
        """
        self.__last_index = ''
        
    def reset_learning(self):
        """ this is where specific variables are initialized
            when we want to learn a NEW behavior
        """
        # the eight memories
        # 0:loss or 1:win, 0:change or 1:keep, 0:loss or 1:win
        self.__shannon_memory = {
            ''.join(_): None for _ in itertools.product('01', repeat=3) }
        # victories, behaviors and actions of opponent
        self.__victories = ''
        self.__behaviors = ''
        self.__actions = ''
        
    def __follow_rule(self) -> bool:
        """ True if we follow some rule 
            ie : shannon[last_index] is odd
        """
        return not (self.__shannon_memory.get(self.__last_index, None) is None
                    or
                    self.__shannon_memory[self.__last_index]%2 == 0)


    def __build_key(self) -> str:
        ''' get the key for shannon memory '''
        if len(self.__victories) != 2: return ''
        _ = self.__victories
        return _[0]+self.__behaviors[-1]+_[1]
    
    def next_action(self) -> str:
        """ my action by default if no observation made """
        # rule possible
        self.__last_index = self.__build_key()
        if not self.__follow_rule():
            self.default_behavior += 1
            return self.default.next_action()
        # a rule is known, and usable
        if self.__shannon_memory[self.__last_index] == 1: # change repeated
            _act = "C" if self.__actions[-1] == 'D' else 'D'
        else: # keep repeated
            _act = self.__actions[-1]
        return _act
    
    def update_knowledge(self, rew):
        """ what to do for learning """
        if rew not in 'TRSP': return # no update if reward is not valid
        # decision about victory/defeat
        self.__victories = update_storage(self.__victories,
                                          '01'[rew in "SR"])
        # store his action
        self.__actions = update_storage(self.__actions,
                                        self.adv_action(rew))
        if len(self.__actions) > 1:
            _b = '01'[self.__actions[-2] == self.__actions[-1]]
            self.__behaviors = update_storage(self.__behaviors, _b)
        # was we acting according to rules or not
        if len(self.__last_index) < 3: return # nothing more
        if self.__follow_rule() and rew in "RP":
            if __debug__:
                print('good rule {}'.format(self.__last_index))
            self.good_guess += 1
            return
        if self.__shannon_memory.get(self.__last_index, None) is None:
            if __debug__:
                print('1st time {}'.format(self.__last_index))
            _value = int(_b+'0', 2)
        elif self.__shannon_memory[self.__last_index] % 2 == 0:
            # 2nd update
            if __debug__:
                print('2nd time {}'.format(self.__last_index), end=' ')
            if self.__shannon_memory[self.__last_index] == int(_b+'0', 2):
                if __debug__: print('same behavior, reinforcement')
                _value = int(_b+'1', 2)
            else:
                if __debug__: print('new behavior, redo')
                _value = int(_b+'0', 2)
        else: # rule is wrong
            if __debug__: print('bad status, remove')
            _value = int(_b+'0', 2)
        self.__shannon_memory[self.__last_index] = _value
        
    @property
    def rules_system(self) -> str:
        """ Get the rules status """
        def translate(key:str) -> str:
            ''' transform 0/1 with words '''
            _v = {'0': 'loss', '1': 'win'}
            _a = {'0': 'change', '1': 'keep'}
            _rep = ''
            #key/dictionnary/max size of words+1 for spacing
            for k,d,s in zip(key, (_v,_a,_v), (5,7,5)):
                _rep += f"{d[k]:<{s}}"
            return _rep
        _val = ['change, new', 'change, repeated',
                'keep, new', 'keep, repeated']
        _str = ''
        for k,v in self.__shannon_memory.items():
            _ = ('NA' if v is None
                 else _val[v])
            _str += f"Rule {translate(k)} status is {_}\n"
        return _str

    @property
    def last_index(self) -> str:
        """ the last memory used """
        return self.__last_index
    @property
    def shannon_memories(self) -> tuple:
        """ a view of the eight Shannon's memories """
        _val = ['cn', 'cr', 'gn', 'gr']
        return tuple(['NA' if x is None else _val[x]
                      for x in self.__shannon_memory.values() ])
    
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

def test_motif(st:Strategy, memsz:int=15):
    """ given some Strategy, mimics with Motif """
    def simulation(rewards) -> Motif:
        """ given many rewards play a fake game """
        o = Motif(Gentle(), memsz)
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

def test_shannon(st:Strategy, noise:float=.1):
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

learning(m, st, 5, 50, 51, epsilon=noise)
m.rules_system
m.last_index
m.shannon_memories

m = Shannon(Gentle())
learning(m, Gentle(), 5, 50, 51)
m.rules_system
m.last_index
m.shannon_memories

learning(m, Bad(), 5, 50, 51, epsilon=noise)
m.rules_system
m.last_index
m.shannon_memories

m = Shannon(Bad())
learning(m, Gentle(), 5, 50, 51)
m.rules_system
m.last_index
m.shannon_memories

learning(m, Bad(), 5, 50, 51, epsilon=noise)
m.rules_system
m.last_index
m.shannon_memories
''' ; testcode(code)

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
    
if __name__ == "__main__":
    for meth in (test_reward,test_automaton,  test_mime,
                 test_motif, test_shannon):
        print(f">>> {meth.__name__}:\n{meth.__doc__}\n{'='*75}")

    random.seed(42)

    # these are some basic classes we want to work with
    # instead of
    # from sol_j01 import Gentle, Bad, Fool, Tit4Tat
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

