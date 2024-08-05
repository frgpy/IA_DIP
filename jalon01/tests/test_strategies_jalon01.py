#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "28.01.20"
__usage__ = "Project 2024: tests jalon 01"
__update__ = "17.01.24 13h22"


import os
import unittest
from unittest.mock import patch
from  tests.tools import checkTools as chk


"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

def mock_prn(*args, **kwargs):
    """ no output allowed during tests """
    pass

class TestStrategie(unittest.TestCase):
    """ pré-requis pour pouvoir tester les sous classes """
    def make_variables(self):
        """ build attributes that might or might not change """
        # what attributes should be checked
        _affected = "count"
        _possible = "memory_size memory "
        _unaffected = "color name surname idnum style actions"
        self.o = self.K()
        for x in _affected.split(): chk.guard_att(self, x)
        for x in _possible.split(): chk.guard_att(self, x)
        for x in _unaffected.split(): chk.guard_att(self, x)
        return {"without": (_affected, _possible+_unaffected),
                "with": (_possible+_affected, _unaffected)}

    def setUp(self):
        chk.check_class(tp, "Strategy")
        self.K = getattr(tp, "Strategy")
        self.args = ((), (0,), (-1,), (1,),
                     (0, -42,), (1, 3,), (-1, 5, tp.m2))
        # style, memory_limit, actions have context
        self.defaults = {"idnum": 42,
                        "memory_size": 0,
                        "memory": '',
                        "count": 0,
                        "color": 42,
                        "name" : "Strat_042",
                        "surname": "Strat_042",}
        self.context = ({"style": 'C', "memory_limit": 0,
                         "actions": tp.m1.actions},
                        {"style": 'a', "memory_limit": 0,
                         "actions": tp.m1.actions},
                        {"style": 'D', "memory_limit": 0,
                         "actions": tp.m1.actions},
                        {"style": 'C', "memory_limit": 0,
                         "actions": tp.m1.actions},
                        {"style": 'a', "memory_limit": -1,
                         "actions": tp.m1.actions},
                        {"style": 'C', "memory_limit": 3,
                         "actions": tp.m1.actions},
                        {"style": 'D', "memory_limit": 5,
                         "actions": tp.m2.actions})
        self.variables = self.make_variables() # avec et sans mémoire
        # history is specific
        self.methods = {"__str__": (None, str),
                        "__repr__": (None, str),
                        "adv_action": (('P',), str),
                        "my_action": (('T',), str),
                        "reset": (None, type(None)),}

        
    def subtest_def(self, idx:int):
        for k,v in self.context[idx].items():
            if k == "actions": continue
            self.defaults[k] = v
        chk.sub_default(self)

    def test_default(self):
        """ default values 7 subcases """
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                self.subtest_def(i)
                _att = "actions"
                _0 = sorted(getattr(self.o, _att))
                _1 = sorted(self.context[i][_att])
                self.assertEqual(_0, _1,
                                 "found '{}', expecting '{}'")


    def compteur(self):
        """ find the sum of history """
        _att = "history"
        chk.guard_meth(self, _att, None)
        _0 = self.o.history()
        if not hasattr(_0, "__len__"):
            self.skipTest("history has type {} which is not iterable"
                          "".format(type(_0)))
        _1 = 0
        for k,v in _0: _1 += v
        return _0,_1

    def test_signature(self):
        """ signature 7 subcases """
        for i,args in enumerate(self.args):
            self.o = self.K(*args)
            with self.subTest(arg=args):
                chk.sub_signature(self)
                _0,_sum = self.compteur()
                self.assertEqual(_sum, 0,
                                     "history do not fill requirement\n{}"
                                     "".format(_0))

        
    def subtest_get_reward(self, idx, yes, no):
        """ test what get_reward do """
        _old = dict()
        _new = dict()
        for i,rew in enumerate("PATRES"):
            for x in yes.split(): _old[x] = getattr(self.o, x)
            for x in no.split():  _old[x] = getattr(self.o, x)
            _,_old['h'] = self.compteur()
            _0 = getattr(self.o, "get_reward")(rew)
            for x in yes.split(): _new[x] = getattr(self.o, x)
            for x in no.split():  _new[x] = getattr(self.o, x)
            _,_new['h'] = self.compteur()
            for x in no.split():
                self.assertEqual(_old[x], _new[x],
                                 "trouble for '{}' at step {}"
                                 "".format(x, i))
            self.assertEqual(_old['h']+1, _new['h'],
                             "history is wrong at step {} for rew='{}'"
                             "".format(i,rew))
            for y in yes.split():
                if self.o.memory_limit < 0 or i < self.o.memory_limit:
                    if y in ("memory_size", "count"):
                        self.assertEqual(_old[y]+1, _new[y],
                                    "trouble for '{}' at step {}"
                                    "found {} expecting {}"
                                    "".format(y, i, _old[y]+1, _new[y]))
                    elif y == "memory":
                        self.assertEqual(len(_old[y])+1, len(_new[y]),
                                        "trouble for '{}' at step {}"
                                        "".format(y, i))
                    else:
                        self.skipTest("'{}' is not handled".format(y))
                else:
                    if y == "memory":
                        self.assertEqual(len(_old[y]), len(_new[y]),
                                        "trouble for '{}' at step {}"
                                        "".format(y, i))
                    elif y == "memory_size":
                        self.assertEqual(_old[y], _new[y],
                                        "trouble for '{}' at step {}"
                                        "found {} expecting {}"
                                        "".format(y, i, _old[y]+1, _new[y]))
                    else:
                        self.assertEqual(_old[y]+1, _new[y],
                                        "trouble for '{}' at step {}"
                                        "found {} expecting {}"
                                        "".format(y, i, _old[y]+1, _new[y]))


    
    def test_get_reward(self):
        """ test if get_reward satisfy our expectation """
        self.o = self.K()
        chk.guard_meth(self, "get_reward", ('T',))
        _variables = [self.variables['without']
                      if x['memory_limit'] == 0 else self.variables['with']
                      for x in self.context]
        for i,args in enumerate(self.args):
            self.o = self.K(*args)
            with self.subTest(constructeur_args=args):
                self.subtest_get_reward(i, *_variables[i])

    def subtest_reset(self, idx, yes, no):
        _old = dict()
        _new = dict()
        for x in yes.split(): _old[x] = getattr(self.o, x)
        for x in no.split():  _old[x] = getattr(self.o, x)
        _,_old['h'] = self.compteur()
        for i,rew in enumerate("PATRES"):
            _0 = getattr(self.o, "get_reward")(rew)
        for x in yes.split(): _new[x] = getattr(self.o, x)
        for x in no.split():  _new[x] = getattr(self.o, x)
        _,_new['h'] = self.compteur()
        # 1/ constat du changement
        for x in yes.split():
            self.assertNotEqual(_old[x], _new[x],
                                "get_reward failed for {}".format(x))
        self.assertNotEqual(_old['h'], _new['h'],
                            "get_reward failed for history")
        for x in no.split():
            self.assertEqual(_old[x], _new[x],
                             "get_reward failed for {}".format(x))
        # 2/ constat du retour à la normal
        _0 = getattr(self.o,"reset")()
        _last = dict()
        for x in yes.split(): _last[x] = getattr(self.o, x)
        for x in no.split():  _last[x] = getattr(self.o, x)
        _,_last['h'] = self.compteur()
        for k in _last:
            with self.subTest(clef=k):
                self.assertEqual(_old[k], _last[k],
                                 "reset failed for {}".format(k))
    
    def test_reset(self):
        """ test if reset satisfy our expectation """
        self.o = self.K()
        chk.guard_meth(self, "reset", None)
        chk.guard_meth(self, "get_reward", ('T',))
        _variables = [self.variables['without']
                      if x['memory_limit'] == 0 else self.variables['with']
                      for x in self.context]
        for i,args in enumerate(self.args):
            self.o = self.K(*args)
            with self.subTest(init_args=args):
                self.subtest_reset(i, *_variables[i])

def next_action(self, model, valid=None, first=None):
    """
       require hasattr(self, 'o')

       launch 10 next_action()
    """
    import random
    _att = "next_action"
    chk.guard_meth(self, "get_reward", ('T',))
    chk.guard_meth(self, "reset")
    chk.guard_meth(self, _att)
    chk.guard_att(self, "actions")
    self.assertCountEqual(self.o.actions, model.actions,
                          "actions are not those expected")
    self.o.reset()
    _valid = model.actions if valid is None else valid
    _first = _valid if first is None else first
    # print(">>> {} valid {} first {}"
    #       "".format(self.K.__name__, _valid, _first))
    # 1st action
    _trace = {}
    for i in range(10): # needed for random case
        _0 = getattr(self.o, _att)()
        self.assertIn(_0, _first,
                      "action {} is not in {}".format(_0, _first))
        if self.o.style != 'a': continue # déterministe stop
        _trace[_0] = _trace.get(_0, 0)+1
    if self.o.style == 'a':
        self.assertTrue(sum(_trace.values()) == 10,
                        "bad count, something odd has happened")
        self.assertTrue(len(_trace) > 1,
                        "how can this be ? .. bad luck")
    self.o.get_reward(random.choice(model.reward_names))
    # 2..10 following
    for i in range(1,10):
        _0 = getattr(self.o, _att)()
        self.assertIn(_0, _valid,
                      "action {} is not in {}".format(_0, _valid))
        self.o.get_reward(random.choice(model.reward_names))
    

class TestHuman(TestStrategie):
    def setUp(self):
        super().setUp()
        self.args = [ (), (tp.m2,) ]
        self.context = ({"style": 'a', "memory_limit": 0,
                         "actions": tp.m1.actions},
                        {"style": 'a', "memory_limit": 0,
                         "actions": tp.m2.actions},
                        )
        self.kname = "Human"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        
    def test_klass(self):
        """ Human: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))

    @patch('builtins.input')
    def test_next_action_bad_input_m1(self, mock_input):
        """ Human: only wrong input """
        mock_input.side_effect = "d c r 12 1 42 [] R".split()
        self.o = self.K()
        chk.check_attr(self.o, "next_action")
        _rep = []
        try:
            _rep.append(self.o.next_action())
        except Exception as _e:
            self.assertTrue(isinstance(_e, StopIteration),
                            "expect failure")
        self.assertEqual(len(_rep), 0,
                         "expect no action")

    @patch('builtins.input')
    def test_next_action_bad_input_m2(self, mock_input):
        """ Human: only wrong input but last """
        mock_input.side_effect = "d c r 12 1 42 [] R".split()
        self.o = self.K(tp.m2)
        chk.check_attr(self.o, "next_action")
        _rep = []
        try:
            _rep.append(self.o.next_action())
        except Exception as _e:
            self.assertFalse(isinstance(_e, StopIteration),
                            "expect failure")
        self.assertEqual(_rep, ['R'],
                         "expect 1 action")

    @patch('builtins.input')
    def test_next_action_good_input_m1(self, mock_input):
        """ Human: default a few valid input """
        mock_input.side_effect = "R C R D R C".split()
        self.o = self.K()
        chk.check_attr(self.o, "next_action")
        _rep = []
        try:
            _rep.append(self.o.next_action())
        except Exception as _e:
            self.assertFalse(isinstance(_e, StopIteration),
                            "dont expect failure")
        self.assertEqual(len(_rep), 1,
                         "expect 1 action")
        self.assertEqual(_rep, ['C'],
                         f"expect {_rep} is ['C']")

    @patch('builtins.input')
    def test_next_action_good_input_m2(self, mock_input):
        """ Human: with model m2 a few valid input after wrong inputs"""
        mock_input.side_effect = "a b c R a C".split()
        self.o = self.K(tp.m2)
        chk.check_attr(self.o, "next_action")
        _rep = []
        try:
            _rep.append(self.o.next_action())
        except Exception as _e:
            self.assertFalse(isinstance(_e, StopIteration),
                            "dont expect failure")
        self.assertEqual(len(_rep), 1,
                         "expect 1 action")
        self.assertEqual(_rep, ['R'],
                         f"expect {_rep} is ['R']")
        
class TestGentle(TestStrategie):
    """ sans mémoire, joue toujours la coopération """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m1
        self.context = ({"style": 'C', "memory_limit": 0,
                         "actions": self.m.actions},)
        self.kname = "Gentle"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ Gentle: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))

    def test_next_action_validity(self):
        """ Gentle: verify that the chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m, "C")
        
class TestBad(TestStrategie):
    """ sans mémoire, joue toujours la duplicité """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m1
        self.context = ({"style": 'D', "memory_limit": 0,
                         "actions": self.m.actions},)
        self.kname = "Bad"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ Bad: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
        
    def test_next_action_validity(self):
        """ Bad: verify that the chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m, "D")

class TestFool(TestStrategie):
    """ sans mémoire, joue de manière équiprobable """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m1
        self.context = ({"style": 'a', "memory_limit": 0,
                         "actions": self.m.actions},)
        self.kname = "Fool"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ Fool: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
        
    def test_next_action_validity(self):
        """ Fool: verify that the chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m)

class TestGSulky(TestStrategie):
    """ 
       mémoire de taille 1, 
       joue toujours la coopération mais abandonne dès 
       que sa récompense n’est pas R
    """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m2
        self.context = ({"style": 'C', "memory_limit": 1,
                         "actions": self.m.actions},)
        self.kname = "GentleSulky"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ GentleSulky: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
        
    def test_next_action_validity(self):
        """ GentleSulky: verify chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m, "CR", "C")

    def test_rule_event(self):
        """ GentleSulky: verify that after some event, things happen """
        self.o = self.K()
        _att = "next_action"
        chk.guard_meth(self, "get_reward", ('T',))
        chk.guard_meth(self, "reset")
        for rew in self.m.reward_names:
            with self.subTest(reward=rew):
                self.o.get_reward(rew)
                _0 = getattr(self.o, _att)()
                if rew=="R": _1 = "C"
                else: _1 = "R"
                self.assertEqual(_0, _1,
                                 "Failed expect {}, found {}"
                                 "".format(_1, _0))
                    
class TestBSulky(TestStrategie):
    """ 
       mémoire de taille 1, 
       commence par duper, puis coopère,
       abandonne dès que sa récompense n’est pas T ou R
    """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m2
        self.context = ({"style": 'D', "memory_limit": 1,
                         "actions": self.m.actions},)
        self.kname = "BadSulky"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ BadSulky: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
        
    def test_next_action_validity(self):
        """ BadSulky: verify that chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m, "CR", "D")

    def test_rule_event(self):
        """ BadSulky: verify that after some event, things happen """
        self.o = self.K()
        _att = "next_action"
        chk.guard_meth(self, "get_reward", ('T',))
        chk.guard_meth(self, "reset")
        for rew in self.m.reward_names:
            with self.subTest(reward=rew):
                self.o.get_reward(rew)
                _0 = getattr(self.o, _att)()
                if rew in "TR": _1 = "C"
                else: _1 = "R"
                self.assertEqual(_0, _1,
                                 "Failed expect {}, found {}"
                                 "".format(_1, _0))
        
class TestFSulky(TestStrategie):
    """ 
       mémoire de taille 1, 
       commence par duper ou coopérer, puis coopère,
       abandonne dès que sa récompense n’est pas T ou R
    """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m2
        self.context = ({"style": 'a', "memory_limit": 1,
                         "actions": self.m.actions},)
        self.kname = "FoolSulky"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ FoolSulky: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
        
    def test_next_action_validity(self):
        """ FoolSulky: verify that the chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m, "CR", "CD")

    def test_rule_event(self):
        """ FoolSulky: verify that after some event, things happen """
        self.o = self.K()
        _att = "next_action"
        chk.guard_meth(self, "get_reward", ('T',))
        chk.guard_meth(self, "reset")
        for rew in self.m.reward_names:
            with self.subTest(reward=rew):
                self.o.get_reward(rew)
                _0 = getattr(self.o, _att)()
                if rew in "TR": _1 = "C"
                else: _1 = "R"
                self.assertEqual(_0, _1,
                                 "Failed expect {}, found {}"
                                 "".format(_1, _0))

class TestTit4Tat(TestStrategie):
    """
       mémoire de taille 1,
       coopère puis joue ce qu’a joué son adversaire au tour précédent
    """
    def setUp(self):
        super().setUp()
        self.args = [ () ]
        self.m = tp.m1
        self.context = ({"style": 'C', "memory_limit": 1,
                         "actions": self.m.actions},)
        self.kname = "Tit4Tat"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ Tit4Tat: test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
        
    def test_next_action_validity(self):
        """ Tit4Tat: verify that the chosen action is within model.actions """
        self.o = self.K()
        next_action(self, self.m,  first="C")

    def test_rule_event(self):
        """ Tit4Tat: verify that after some event, things happen """
        self.o = self.K()
        _att = "next_action"
        chk.guard_meth(self, "get_reward", ('T',))
        chk.guard_meth(self, "reset")
        chk.guard_meth(self, "adv_action", ('T',))
        for rew in self.m.reward_names:
            with self.subTest(reward=rew):
                self.o.get_reward(rew)
                _0 = getattr(self.o, _att)()
                _1 = self.o.adv_action(rew)
                self.assertEqual(_0, _1,
                                 "Failed expect {}, found {}"
                                 "".format(_1, _0))

class TestWSLS(TestTit4Tat):
    """
       mémoire de taille 1, 
       coopère puis joue la même chose qu’au tour précédent 
       si la récompense a été T ou R, 
       joue l’opposé du tour précédent si la récompense a été P ou S.
    """
    def setUp(self):
        super().setUp()
        self.kname = "WinStayLooseShift"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_rule_event(self):
        """ WinStayLooseShift: verify that after some event, things happen """
        self.o = self.K()
        _att = "next_action"
        chk.guard_meth(self, "get_reward", ('T',))
        chk.guard_meth(self, "reset")
        chk.guard_meth(self, "my_action", ('T',))
        for rew in self.m.reward_names:
            with self.subTest(reward=rew):
                self.o.get_reward(rew)
                _0 = getattr(self.o, _att)() # next
                _1 = self.o.my_action(rew) # prev
                if rew in "TR":
                    self.assertTrue(_0 == _1,
                                     "Failed expect {}, found {}"
                                      "".format(_1, _0))
                else:
                    _2 = "D" if _1 == "C" else "C"
                    self.assertTrue(_0 != _1,
                                     "Failed expect {}, found {}"
                                      "".format(_2, _0))

class TestPavlov(TestTit4Tat):
    """
       mémoire de taille 1, 
       coopère puis joue la même chose qu’au tour précédent 
       si la récompense a été P ou R, 
       joue l’opposé du tour précédent si la récompense a été T ou S.
    """
    def setUp(self):
        super().setUp()
        self.kname = "Pavlov"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        
    def test_rule_event(self):
        """ Pavlov: verify that after some event, things happen """
        self.o = self.K()
        _att = "next_action"
        chk.guard_meth(self, "get_reward", ('T',))
        chk.guard_meth(self, "reset")
        chk.guard_meth(self, "my_action", ('T',))
        for rew in self.m.reward_names:
            with self.subTest(reward=rew):
                self.o.get_reward(rew)
                _0 = getattr(self.o, _att)() # next
                _1 = self.o.my_action(rew) # prev
                if rew in "PR":
                    self.assertTrue(_0 == _1,
                                     "Failed expect {}, found {}"
                                      "".format(_1, _0))
                else:
                    _2 = "D" if _1 == "C" else "C"
                    self.assertTrue(_0 != _1,
                                     "Failed expect {}, found {}"
                                      "".format(_2, _0))
    
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestStrategie, TestHuman, TestGentle, TestBad,
               TestFool, TestGSulky, TestBSulky, TestFSulky,
               TestTit4Tat, TestWSLS, TestPavlov)
    
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass_t in klasses:
        sweet.addTest(unittest.makeSuite(klass_t))
    return sweet

if __name__ == "__main__":
    param = input("quel est le fichier à traiter ? ")
    if not os.path.isfile(param): ValueError("need a python file")

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    tp = __import__(etudiant) # revient à faire import XXX as tp

    unittest.main()
