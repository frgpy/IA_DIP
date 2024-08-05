#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__usage__ = """
base contains: classes with no method predefined 'next_action'
"""

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
    ID = 1
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
        
    def __getattr__(self, att:str):
        """ provides att from _model """
        return getattr(self._model, att)

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
        return ("{0.__class__.__name__}\n\tcoups joués {0.count}"
                "\nétat mémoire '{0.memory}'".format(self))

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



class AbstractLearner(Strategy):
    """ abstract class for learners """

    def __init__(self, st:Strategy, maxsz:int=0):
        """ 
            st: the default behavior
            maxsz: depends on the Learner
            Mime: 3
            Motif: infini ou grand >= 50
            Shannon: any, dont use it

        this class provides a few attributes
        + good_guess: number of good predictions
        + default_behavior: number of times default behavior has been used
        + rate: [0,1] ratio of guesses wrt actions
        """
        _stylus = {'C': 1, 'D': -1, 'a': 0}
        if not hasattr(st, 'next_action'):
            raise TypeError('{} cant mimic'.format(st.__class__.__name__))
        _maxsz = -1 if maxsz < 0 else max(3, maxsz)
        self.__default = st
        super().__init__(_stylus[st.style], _maxsz, st._model)
        self.reset_learning()

    def clone(self) -> 'AbstractLearner':
        """ a trick for evaluation we keep same idnum """
        _ID = Strategy.ID # save old value
        Strategy.ID = self.idnum
        _1 =  self.__class__(self.default, self.memory_limit)
        Strategy.ID = _ID # reinstall old value
        return _1
    
    def reset(self):
        """ reset should be done for learner and default behavior """
        super().reset()
        self.default.reset()
        del self.good_guess
        del self.default_behavior
        self.specific_reset()

    def specific_reset(self):
        """ this is where specific variables should be initialized 
            after each Match
        """
        pass

    def reset_learning(self):
        """ this is where specific variables are initialized
            when we want to learn a NEW behavior
        """
        raise NotImplementedError("reset_learning: Learning cant start")

    def update_knowledge(self, rew:str):
        """ we have a new reward, we have to update our knowledge """
        raise NotImplementedError(
            "update_knowledge: U know things, then use it"
        )
    
    def get_reward(self, rew:str):
        """ rewards are used for knowledge update
            they are also stored twice
            in self.memory and in self.default.memory
        """
        self.update_knowledge(rew)
        super().get_reward(rew)
        self.default.get_reward(rew)
        
    #======== getter & setter ===============================#
    @property
    def default(self) -> Strategy:
        """ specify who am I """
        return self.__default

    def get_good_guess(self) -> int:
        """ getter good_guess """
        return self.__goodguess
    def set_good_guess(self, v:int):
        """ setter good_guess """
        if isinstance(v, int): self.__goodguess = v
    def del_good_guess(self):
        self.__goodguess = 0

    good_guess = property(get_good_guess, set_good_guess, del_good_guess,
                          doc="store when our guess is correct")

    def get_default_behavior(self) -> int:
        return self.__default_behavior
    def set_default_behavior(self, v:int):
        if isinstance(v, int): self.__default_behavior = v
    def del_default_behavior(self):
        self.__default_behavior = 0

    default_behavior = property(get_default_behavior, set_default_behavior,
                                del_default_behavior,
                                doc="store when we use default behavior")

    @property
    def rate(self) -> float:
        """ provides the qty of guesses wrt the number of actions """
        if self.count !=0: return self.good_guess/self.count
        
    @property
    def rules_system(self) -> str:
        """ return an informative string about learning """
        raise NotImplementedError("rules_system: Cant display knowledge")

        
