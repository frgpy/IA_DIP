#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from tools.ezCLI import testcode
from tools.base import Strategy
from tools.model import Model, m1, m2
from tools.evaluations import evaluation, multi_eval, tournament


class Gentle(Strategy):
    """ always Cooperates """
    def next_action(self): return self.style

class Bad(Strategy):
    """ always Defects """
    def __init__(self):
        super().__init__(-1)
        
    def next_action(self): return self.style

class Fool(Strategy):
    """ plays at random """
    def __init__(self):
        super().__init__(0)
        
    def next_action(self): return random.choice(self.actions)

class Human(Strategy):
    """ Human Interface """
    def __init__(self, model:Model=m1):
        super().__init__(0, 0, model)

    def next_action(self):
        _rep = ""
        while _rep not in self.actions or len(_rep) != 1:
            _rep = input(f"Donnez votre action parmi {self._model.actions} ")
        return _rep
    

class GentleSulky(Strategy):
    """ Sulky if model has 3 actions """
    def __init__(self, model=m2):
        super().__init__(1,1,model)
    def next_action(self):
        if self.memory_size == 0: return self.style
        if 'R' in self.actions and self.memory != "R": return 'R'
        return "C"

class BadSulky(Strategy):
    """ Sulky if model has 3 actions """
    def __init__(self, model=m2):
        super().__init__(-1,1,model)
    def next_action(self):
        if self.memory_size == 0: return self.style
        if 'R' in self.actions and self.memory not in "TR": return 'R'
        return "C"


class FoolSulky(Strategy):
    def __init__(self,model=m2):
        super().__init__(0,1,model)
    def next_action(self):
        if self.memory_size == 0: return random.choice("CD")
        if 'R' in self.actions and self.memory not in "TR": return 'R'
        return "C"


class Tit4Tat(Strategy):
    """ play the last action of adv """
    def __init__(self, model:Model=m1):
        super().__init__(1,1,model)
    def next_action(self):
        if self.memory_size == 0: return self.style
        return self.adv_action(self.memory)

class WinStayLooseShift(Strategy):
    """ When loosing changes the action """
    def __init__(self, model:Model=m1):
        super().__init__(1,1,model)
    def next_action(self):
        if self.memory_size == 0: return self.style
        _default = self.my_action(self.memory)
        _oppose = "C" if _default == "D" else "D"
        if self.memory in "TR": return _default
        else: return _oppose
            
class Pavlov(Strategy):
    """ when adv switches I switch """
    def __init__(self, model:Model=m1):
        super().__init__(1,1,model)
    def next_action(self):
        if self.memory_size == 0: return self.style
        _default = self.my_action(self.memory)
        _oppose = "C" if _default == "D" else "D"
        if self.memory in "PR": return _default
        else: return _oppose
    
    

if __name__ == "__main__":
    code = """    
x = Strategy(0)
y = Strategy(-1)
z = Strategy()
x.surname = 'Lunatique'
y.surname = 'Méchant'
z.surname = 'Gentil'
x.surname == 'Lunatique'
y.surname == 'Méchant'
z.surname == 'Gentil'
# this should fail as no next_action is defined
evaluation(y,z) == (m1.values['T'], m1.values['S'])
g = Gentle()
b = Bad()
f = Fool()
f.surname = 'Lunatique'
b.surname = 'Méchant'
g.surname = 'Gentil'
f.surname == 'Lunatique'
b.surname == 'Méchant'
g.surname == 'Gentil'
evaluation(b,g) == (m1.values['T'], m1.values['S'])

print(f"{g.idnum=}, {b.idnum=}, {f.idnum=}")
multi_eval(g, [b, f])

print(f"{g.idnum=}, {b.idnum=}, {f.idnum=}")
tournament([g,b,f])
""" ; testcode(code)
