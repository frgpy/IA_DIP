#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "29.01.20"
__usage__ = "Model for the DIP Project: provides m1, m2, m3 & m4"
__update__ = "10.01.24 20:35"

try:
    from ezCLI import testcode
except:
    from tools.ezCLI import testcode
from numbers import Number
#============================= Le Modèle du Jeu ========================#
class Model:
    def __init__(self, rewards:dict, values:dict):
        """ 
            from rewards and values
            build ro attributes (property)
	        self.rewards : 
                 the rewards and actions 
	        self.values : 
                 the numerical values
	        self.actions : 
                 the authorized actions
	        self.reward_names : 
                 rewards' names

            one method
	        self.get_actions(rew:str) -> str : 
                  given rewards provides the actions involved
        """
        self.__recompenses = set(''.join([x for x in rewards.values()]))
        self.__actions = set(''.join([x for x in rewards.keys()]))
        if len(rewards) != len(self.__actions)**2:
            raise Exception("Actions inconsistency")
        if len(self.__recompenses) != len(values):
            raise Exception("Rewards inconsitency")
        self.__rewards = rewards
        self.__values = values
        self.__rewact = {}
        for k,v in rewards.items():
            for (i,x) in enumerate(v):
                _old = self.__rewact.get(x, set())
                if i == 0: _old.add(k)
                else: _old.add(k[::-1])
                self.__rewact[x] = _old

        for k in self.__rewact:
            if len(self.__rewact[k]) != 1:
                self.__rewact[k] = list(self.__rewact[k])
            else:
                self.__rewact[k] = self.__rewact[k].pop()

        self.__keys = None

    @property
    def rewards(self) -> dict:
        """ dict: keys are 2actions, values are 2 rewards """
        return self.__rewards.copy()
    @property
    def values(self) -> dict:
        """ dict: keys are rewards, values are numeric """
        return self.__values.copy()
    @property
    def actions(self) -> str:
        """ the actions as string in lexicographic reverse order """
        return ''.join(sorted(list(self.__actions), reverse=True))
    @property
    def reward_names(self) -> str:
        """ the rewards as string in lexicographic order """
        return ''.join(sorted(list(self.__recompenses)))

    def get_actions(self, rew) -> str:
        """ for a given reward send the actions involved 
            1st is mine, 2nd is adversary
        """
        return self.__rewact.get(rew,'')


    def __build_keys(self):
        """ set self.__keys once """
        self.__keys = ''.join(sorted(self.reward_names,
                                     key=lambda x: self.values[x],
                                     reverse=True))
        if len(self.__keys) == 5:
            self.__keys = self.__keys[:2]+self.__keys[3:]
        
    def encoding(self, word:str) -> int:
        """ given a word of rews, 
           return its index if exists else -1 """
        def oneKey(rew:str) -> int:
            """ the index of rew in self.__keys, else -1 """
            return (self.__keys.find(rew)
                    if rew in self.reward_names else -1)
            
        if self.__keys is None: self.__build_keys()
        _ = [oneKey(x) for x in word]
        if any([i<0 for i in _]): return -1
        _1 = 0
        for x in _:
            _1 = _1*4+(x+1)
        return _1

    def decoding(self, idx:int) -> str:
        """ return the memory values corresponding to idx """
        if self.__keys is None: self.__build_keys()
        _mem = ''
        while idx > 0:
            _ = (idx-1)%4
            idx = (idx-1)//4
            _mem = self.__keys[_]+_mem
        return _mem
            
    def __repr__(self) -> str:
        return ("{0}({1.rewards}, {1.values})"
                .format(self.__class__.__name__, self))
    def __str__(self) -> str:
        _str = ""
        _str += "{:<19s} '{}'\n".format("actions authorized:",
                                        self.actions)
        _str += "{:<19s} '{}'\n".format("rewards' names:",
                                        self.reward_names)
        _str += "{:<19s} {}\n".format("rewards' values:",
                                      list(self.values.items()))
        return _str

#===============  models m1 et m2 ===============#
class Factory:
    def __init__(self, standard:bool=True):
        """
        standard is True only D(uplicity) and C(ooperation)
        else: R(efuse) is added and stop the competition
              nb the reward when one Refuses is A(borting)
        """
        self.__default = { 'DD': 'PP', 'DC': 'TS', 'CD': 'ST', 'CC': 'RR' }
        self.__default_val = { 'T': 7, 'R': 5, 'P': 2, 'S': 0}
        self.__order = "TRPS"
        if not standard:
            for x in 'DC':
                self.__default[x+'R'] = "AA"
                self.__default['R'+x] = "AA"
            self.__default["RR"] = "AA"
            self.__default_val['A'] = 3
            self.__order = "TRAPS"

    def change_val(self, rew:str, val:Number):
        """ for a given reward, modify its value
            raises exception if rew does not exist
            check that the new value is consistent with pre and post
            to prevent inconsistency
        """
        try:
            p = self.__order.index(rew)
            _prev = None
            _post = None
            if p==0: _post = self.__order[p+1]
            elif p == len(self.__order)-1:
                _prev = self.__order[p-1]
            else:
                _prev=self.__order[p-1]
                _post=self.__order[p+1]
                
            if _prev is not None and val > self.__default_val[_prev]:
                raise ValueError(
                    f"{rew}: {val} is bigger than {self.__default_val[_prev]}")

            if _post is not None and val < self.__default_val[_post]:
                raise ValueError(
                    f"{rew}: {val} is lower than {self.__default_val[_post]}")

        except Exception as _e:
            print(_e) ; return
        self.__default_val[rew] = val

    def build(self) -> Model:
        """ provides a new Model with rewards' names and values """
        return Model(self.__default.copy(), self.__default_val.copy())

#========================== predefined models =======================#    
m1 = Factory().build()
m2 = Factory(False).build()
_0 = Factory()
for i,x in enumerate("SPRT"):
    _0.change_val(x, i*.25)
m3 = _0.build()
_1 = Factory(False)
for i,x in enumerate("SPART"):
    _1.change_val(x, i*.25)
m4 = _1.build()

if __name__ == "__main__":
    print("expected failure message")
    for i,x in enumerate("PSRT"):
        _0.change_val(x, i*.25)
        
    code = """
sorted(m1.actions) == sorted("DC")
sorted(m1.reward_names) == sorted("TRPS")
isinstance(m1.rewards, dict)
len(m1.rewards) == len(m1.actions)**2
isinstance(m1.values, dict)
len(m1.values) == len(m1.reward_names)
all([m1.values[x]>m1.values[y] for i,x in enumerate("TRP") for j,y in enumerate("RPS") if i<=j])
all([ all([m1.get_actions(x)[i] in m1.actions for i in range(2) if hasattr(m1.get_actions(x),'__len__') and len(m1.get_actions(x))==2]) for x in m1.reward_names])
m1.decoding(m1.encoding("TTPRST")) == "TTPRST"
m1.encoding("A") == -1

sorted(m2.actions) == sorted("DCR")
sorted(m2.reward_names) == sorted("ATRPS")
isinstance(m2.rewards, dict)
len(m2.rewards) == len(m2.actions)**2
isinstance(m2.values, dict)
len(m2.values) == len(m2.reward_names)
all([m2.values[x]>m2.values[y] for i,x in enumerate("TRAP") for j,y in enumerate("RAPS") if i<=j])
all([ all([m2.get_actions(x)[i] in m2.actions for i in range(2) if hasattr(m2.get_actions(x),'__len__') and len(m2.get_actions(x))==2]) for x in m2.reward_names])
m2.decoding(m2.encoding("TTPRST")) == "TTPRST"
m1.encoding("A") == -1

import itertools
entiers = [ _ for _ in range(250)]
entiers == sorted(entiers)
mots_m1 = [m1.decoding(_) for _ in entiers ]
mots_m2 = [m2.decoding(_) for _ in entiers ]
len(entiers) == len(mots_m1)
mots_m1 == mots_m2
int_m1 = [m1.encoding(_) for _ in mots_m1]
int_m2 = [m2.encoding(_) for _ in mots_m2]
int_m1 == int_m2
int_m1 == entiers
_1 = [ '', 'T', 'R', 'P', 'S']
_1.extend([ "".join(_) for _ in itertools.product("TRPS", repeat=2) ])
_1.extend([ "".join(_) for _ in itertools.product("TRPS", repeat=3) ])
_2 = [ m1.encoding(_) for _ in _1 ]
_2 == list(range(85))
_3 = [m1.decoding(_) for _ in _2]
_3 == _1
""" ; testcode(code)
