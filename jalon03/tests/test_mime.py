#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "02.03.20"
__usage__ = "Project 2024: tests jalon 03"
__update__ = "12.02.24 17h50"


import os
import unittest
from unittest.mock import patch
from tests.tools import checkTools as chk
from tools.model import Model, m1, m2, m3, m4
from tools.base import Strategy
from tools.evaluations import adaptive_evaluation as evaluate
import random

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

data = chk.Data()

def mock_prn(*args, **kwargs):
    """ no output allowed during tests """
    pass

#### Basic strategies ####
class Gentle(Strategy):
    """ always C """
    def next_action(self): return self.style
class Bad(Strategy):
    """ always D """
    def __init__(self, m:Model=m1):
        super().__init__(-1, 0, m)
    def next_action(self): return self.style


class TestDefault(unittest.TestCase):
    """ find the attributes and methods fullfilled """
    def setUp(self):
        """ init """
        self.kname = "Mime"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.rews = m3.reward_names
        
    @patch('builtins.print')    
    def test_check(self, mock_prn):
        """ collect datas """
        _latt = "learned_rules rules_system"
        _lmeth0 = "reset_learning next_action"
        _lmeth1 = "update_knowledge"
        try:
            self.o = self.K(Bad())
        except NotImplementedError as _e:
            print(_e)
            self.skipTest(">>> '{}' is missing!".format("reset_learning"))
                          
        for att in _latt.split():
            try:
                getattr(self.o, att)
                data.yes += 1
                data.subtests.add(att)
                if chk.check_flush(): print('.', flush=True, end='')
            except Exception as _e:
                data.no += 1
                data.report[att] = str(_e)

        for att in _lmeth0.split():
            try:
                getattr(self.o, att)()
                data.yes += 1
                data.subtests.add(att)
                if chk.check_flush(): print('.', flush=True, end='')
            except Exception as _e:
                data.no += 1
                data.report[att] = str(_e)

        for att in _lmeth1.split():
            
            _rew = random.choice(self.rews)
            try:
                getattr(self.o, att)(_rew)
                data.yes += 1
                data.subtests.add(att)
                if chk.check_flush(): print('.', flush=True, end='')
            except Exception as _e:
                data.no += 1
                data.report[att] = str(_e)

        print(data)
                
        
class TestMime(unittest.TestCase):
    """ follow the rules """
    def setUp(self):
        class BabaYaGa(tp.Strategy):
            def __init__(self, st, model):
                super().__init__(0, 3, model)
                self.surname = "Lunatic"
                self.opponent = st
                self.flush()
            def flush(self):
                self.__trace = [0 for _ in range(85)]
            @property
            def trace(self): return tuple(self.__trace)
            def next_action(self):
                """ Im lunatic """
                def opp(x):
                    """ easy contradiction """
                    return 'C' if x=='D' else 'D'
                _idx = self._model.encoding(self.memory)
                if self.trace[_idx] == 0: 
                    if self.count < 5: _act = opp(self.opponent.next_action())
                    else: _act = random.choice(self._model.actions)
                    self.__trace[_idx] = _act
                return self.trace[_idx]

        self.st = [Gentle(), None]
        self.st[1] = BabaYaGa(self.st[0], m4)
        self.kname = "Mime"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.required = "reset_learning"

    def subtest_klass(self, kname:str):
        self.assertTrue(issubclass(self.K, getattr(tp,kname)),
                        "{0.kname} is not a subclass of {1}"
                        "".format(self, kname))
        
    def test_klass_std(self):
        """ test if subclass of Strategy """
        self.subtest_klass('Strategy')

    def test_klass_learner(self):
        """ test if subclass of AbstractLearner """
        self.subtest_klass('AbstractLearner')

    def sub_required(self):
        """ helper for automatic tests """
        for att in self.required.split():
            self.subtest_missing(att, "'{}' is required!!!")
        
    def subtest_missing(self, att, msg=None):
        """ verify that att has been seen """
        _msg = "'{}' not properly set" if msg is None else msg
        if att not in data.subtests:
            self.skipTest(_msg.format(att))

    @patch('builtins.print')    
    def test_learned_rules(self, mock_prn):
        """ check learned_rules default """
        self.sub_required()
        _att = 'learned_rules'
        self.subtest_missing(_att)
        # attribute exists
        self.o = self.K(self.st[0])
        chk.guard_ro(self, _att)
        _1 = getattr(self.o, _att)
        self.assertIsInstance(_1, tuple,
                              "expect tuple, found {}".format(type(_1)))
        self.assertEqual(len(_1), 85,
                              "expect 85, found {}".format(len(_1)))
        self.assertTrue(all([x==0 for x in _1]),
                        "found {} non-0".format(85-_1.count(0)))

    @patch('builtins.print')    
    def test_learned_rules_changes(self, mock_prn):
        """ learned_rules should be modified """
        self.required = self.required + ' update_knowledge'
        self.sub_required()
        _att = 'learned_rules'
        self.subtest_missing(_att)
        # attribute exists
        self.o = self.K(self.st[0])
        self.o.get_reward('R')
        _1 = getattr(self.o, _att)
        self.assertFalse(all([x==0 for x in _1]),
                        "found {} non-0".format(85-_1.count(0)))
        self.assertEqual(_1[0], 'C',
                         "found '{}' expecting '{}'"
                         "".format(_1[0], 'C'))
        self.o.reset()
        _1 = getattr(self.o, _att)
        self.assertFalse(all([x==0 for x in _1]),
                        "after reset: found {} non-0"
                         "".format(85-_1.count(0)))
        self.assertEqual(_1[0], 'C',
                         "after reset: found '{}' expecting '{}'"
                         "".format(_1[0], 'C'))
        self.o.reset_learning()
        _1 = getattr(self.o, _att)
        self.assertTrue(all([x==0 for x in _1]),
                        "after reset_learning: found {} non-0"
                        "".format(85-_1.count(0)))

    @patch('builtins.print')    
    def test_learned_rules_values(self, mock_prn):
        """ verify information in learned_rules """
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        _att = 'learned_rules'
        self.subtest_missing(_att)
        # attribute exists, makes some evaluation
        self.o = self.K(self.st[0])
        _adv = self.st[1]
        _0 = evaluate(self.o, _adv, 5, 4, 5)
        # verify rules
        _diff = [_ for _ in range(85)
                 if self.o.learned_rules[_] != _adv.trace[_]]
        self.assertEqual(self.o.learned_rules, _adv.trace,
                         "Rules are different at positions {}"
                         "".format(_diff))

    @patch('builtins.print')    
    def test_compteurs_get_reward(self, mock_prn):
        """ expect some changes in guess, none for behavior """
        self.required = self.required + ' update_knowledge'
        self.sub_required()
        _att = 'learned_rules'
        self.subtest_missing(_att)
        # attribute exists
        self.o = self.K(self.st[0])
        _1 = getattr(self.o, _att)
        self.o.get_reward('R')
        _1 = self.o.good_guess
        _2 = self.o.default_behavior
        self.assertEqual(_1, 0,
                         "init gg: 1st time expect 0, found {}"
                         "".format(_1))
        self.assertEqual(_2, 0,
                         "init db: 1st time expect 0, found {}"
                         "".format(_1))
        # reset
        self.o.reset()
        self.o.get_reward('R')
        _1 = self.o.good_guess
        _2 = self.o.default_behavior
        self.assertEqual(_1, 1,
                         "reset gg: 2nd time expect 1, found {}"
                         "".format(_1))
        self.assertEqual(_2, 0,
                         "reset db: 2nd time expect 0, found {}"
                         "".format(_1))
        # reset_learning and reset
        self.o.reset_learning()
        self.o.reset()
        self.o.get_reward('R')
        _1 = self.o.good_guess
        _2 = self.o.default_behavior
        self.assertEqual(_1, 0,
                         "reset_learning+reset gg: 1st time expect 0, found {}"
                         "".format(_1))
        self.assertEqual(_2, 0,
                         "reset_learning+reset db: 2nd time expect 0, found {}"
                         "".format(_1))

    @patch('builtins.print')    
    def test_compteurs_next_action(self, mock_prn):
        """ expect some changes in  behavior, none for guess """
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        _att = 'learned_rules'
        self.subtest_missing(_att)
        # attribute exists
        self.o = self.K(self.st[0])
        _1 = getattr(self.o, _att)
        _0 = self.o.next_action()
        self.o.get_reward('R')
        _1 = self.o.good_guess
        _2 = self.o.default_behavior
        self.assertEqual(_1, 0,
                         "init gg: 1st time expect 0, found {}"
                         "".format(_1))
        self.assertEqual(_2, 1,
                         "init db: 1st time expect 1, found {}"
                         "".format(_1))
        # reset
        self.o.reset()
        _0 = self.o.next_action()
        self.o.get_reward('R')
        _1 = self.o.good_guess
        _2 = self.o.default_behavior
        self.assertEqual(_1, 1,
                         "reset gg: 2nd time expect 1, found {}"
                         "".format(_1))
        self.assertEqual(_2, 0,
                         "reset db: 2nd time expect 0, found {}"
                         "".format(_1))
        # reset_learning and reset
        self.o.reset_learning()
        self.o.reset()
        _0 = self.o.next_action()
        self.o.get_reward('R')
        _1 = self.o.good_guess
        _2 = self.o.default_behavior
        self.assertEqual(_1, 0,
                         "reset_learning+reset gg: 1st time expect 0, found {}"
                         "".format(_1))
        self.assertEqual(_2, 1,
                         "reset_learning+reset db: 2nd time expect 1, found {}"
                         "".format(_1))

    @patch('builtins.print')    
    def test_compteurs_ok(self, mock_prn):
        """ good + behavior = count """
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        # attribute exists, makes some evaluation
        self.o = self.K(self.st[0])
        _adv = self.st[1]
        _expect = [4, 3, 2, 1]
        for i in range(1, 10):
            with self.subTest(nbMatch=i):
                _0 = evaluate(self.o, _adv, i, 4, 5)
                _1 = self.o.good_guess + self.o.default_behavior
                self.assertEqual(_1, self.o.count,
                                 "this is odd, got {} expect {}"
                                 "".format(_1, self.o.count))
                _e = 0 if i > len(_expect) else _expect[i-1]
                self.assertEqual(self.o.default_behavior, _e,
                                 "default_behavior should be {} found {}"
                                 "".format(_e, self.o.default_behavior))
                
    @patch('builtins.print')    
    def test_compteurs_nok(self, mock_prn):
        """ 0 = good <= behavior """
        class Parasite(tp.Strategy):
            def __init__(self, st):
                super().__init__(0, 0, st._model)
                self.adv = st
            def next_action(self):
                def opp(x):
                    """ simple refutation """
                    return 'C' if x=='D' else 'D'
                return opp(self.adv.next_action())
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        # attribute exists, makes some evaluation
        self.o = self.K(self.st[0])
        _adv = Parasite(self.o)
        for i in range(1, 10):
            with self.subTest(nbMatch=i):
                _0 = evaluate(self.o, _adv, i, 7, 8)
                _1 = self.o.good_guess 
                _2 = self.o.default_behavior
                self.assertLessEqual(_1, _2,
                                 "this is odd, got {} expect < {}"
                                 "".format(_1, _2))
                self.assertEqual(_1, 0,
                                 "no correct guess is possible but found {}"
                                     "".format(_1))

    @patch('builtins.print')    
    def test_rules_system(self, mock_prn):
        """ check basic property of rule_systems """
        _att = 'rules_system'
        self.subtest_missing(_att)
        # attribute exists, makes some evaluation
        self.o = self.K(self.st[0])
        # a string of len 0 is expected
        _0 = getattr(self.o, _att)
        self.assertIsInstance(_0, str,
                              "wrong type for '{}' found {}"
                              "".format(_att, type(_0)))
        self.assertTrue(len(_0) == 0,
                        "bad len: found {} expect 0".format(len(_0)))
        # test with game play
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        self.subtest_missing('learned_rules')
        self.o = self.K(self.st[0])
        _adv = self.st[1]
        for i,x in enumerate("TPRS"):
            self.o.get_reward(x)
            _0 = getattr(self.o, _att)
            self.assertIsInstance(_0, str,
                                "wrong type for '{}' found {}"
                                "".format(_att, type(_0)))
            self.assertTrue(_0.count('\n') == i+1,
                        "bad len: found {} expect {}"
                        "".format(_0.count('\n'), i+1))
        
        for i in range(1, 10):
            with self.subTest(nbMatch=i):
                _ = evaluate(self.o, _adv, i, 7, 8)
                _0 = getattr(self.o, _att)
                _1 = 85 - self.o.learned_rules.count(0)
                self.assertIsInstance(_0, str,
                                "wrong type for '{}' found {}"
                                "".format(_att, type(_0)))
                self.assertTrue(_0.count('\n') == _1,
                                "bad len: found {} expect {}"
                                "".format(_0.count('\n'), _1))
            
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestDefault, TestMime, )
    
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
    
