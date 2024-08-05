#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__usage__ = """
base contains: classes with no method predefined 'next_action'
"""

import random
try:
    from model import *
except:
    try:
        from tools.model import *
    except:
        print("model.py missing")
        
try:
    from ezCLI import testcode
except:
    try: from tools.ezCLI import testcode
    except: print("ezCLI.py missing")

def main():
    print(__usage__)
    
class Strategy:
    """ Main class: 
    idnum: unique identifier
    """
    ID = 0
    def __init__(self, styl:int=1, maxsz:int=0, model:Model=m1):
        """
        styl in {-1, 0, 1} defines the default behavior
        - -1: Defect
        - +1: Cooperate
        - 0: Random

        maxsz in Z defines the limit of memory size
        if < 0 : an infinite memory is available
        if 0: no memory available
        else: a few element are accessible

        model: defines both actions either (DC or DCR) and values of rewards
               T (you Defect and he Cooperates)
               R (both Cooperate)
               P (both Defect)
               S (you Cooperate, he Defects)
               A (one Renounces)
        """
        self.__idnum = self.ID
        Strategy.ID += 1
        self.__styl = styl
        self.__size = -1 if maxsz < 0 else maxsz
        self._model = model
        self.__color = self.idnum
        self.__name = self.__surname = f"Strat_{self.idnum:03d}"
        self.reset()
        
    def reset(self):
        """ reset:
        clear memory, history and played encounters """
        self._memory = ""
        self._cpt = 0
        self._history = {}

    @property
    def idnum(self) -> int:
        """ unique identifier """
        return self.__idnum
    @property
    def memory(self) -> str:
        """ memory is a string of rewards received """
        return self._memory[:]
    @property
    def memory_size(self) -> int:
        """ return the memory used """
        return len(self._memory)
    @property
    def memory_limit(self) -> int:
        """ return the memory max size available 
        -1: infinite
        0: no memory
        k>0 the size allotted
        """
        return self.__size
    @property
    def has_memory(self) -> bool:
        """ True if memory exists """
        return self.__size != 0
    @property
    def actions(self) -> str:
        """ the authorized actions according to the model """
        return self._model.actions
    @property
    def count(self) -> int:
        """ number of games done """
        return self._cpt
    @property
    def name(self) -> str:
        """ default naming using the idnum property """
        return self.__name
    @property
    def surname(self) -> str:
        """ the surname of the strategy """
        return self.__surname
    @surname.setter
    def surname(self, surname:str):
        """ change the surname of the current strategy """
        self.__surname = str(surname)
    @property
    def style(self) -> str:
        """ a is for random action, C for cooperation, D for defection """
        return "aCD"[self.__styl]

    @property
    def color(self) -> int:
        """ this property is used in eco_evolution for display """
        return self.__color
    @color.setter
    def color(self, v):
        if v in range(256): self.__color = v

    def __repr__(self) -> str:
        """ display """
        return ("{0}({1.style}, {1.memory_limit}, {2})"
                .format(self.__class__.__name__, self, repr(self._model)))

    def __str__(self) -> str:
        """ short display about the strategy """
        return "coups joués {0.count}\nétat mémoire '{0.memory}'".format(self)

    def get_reward(self, rew:str):
        """ collect reward from game
        add reward in history and update the count
        if strategy has a memory, update memory
        if memory is limited, remove the oldest
        """
        _o = self._history.get(rew, 0)
        self._history[rew] = _o+1
        self._cpt += 1
        if self.memory_limit != 0:
            self._memory += rew
            if self.memory_limit > 0 and self.memory_size > self.memory_limit:
                self._memory = self._memory[1:]
                
    def history(self) -> list:
        """ return for each reward, the occurence during one game """
        return self._history.items()
    
    def __action(self, rew:str, i:int):
        """ helper:
        rew is some reward, i is in {0,1}
        return the action associated
        0 is always Your action, 1 is always His/Her
        """
        if rew not in self._model.reward_names: return 
        _ = self._model.get_actions(rew)
        return 'R' if len(_) != 2 else _[i]
    
    def my_action(self, rew:str) -> str:
        """ get my last action """
        _ = self.__action(rew, 0)
        return '' if _ is None else _
        
    def adv_action(self, rew:str) -> str:
        """ get her last action """
        _ = self.__action(rew, 1)
        return '' if _ is None else _

    def next_action(self) -> str:
        """ this is an abstract method, to be set """
        raise ValueError("'next_action' is not defined")


    
