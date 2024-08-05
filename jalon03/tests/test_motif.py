#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "02.03.20"
__usage__ = "Project 2024: tests jalon 03"
__update__ = "19.02.24 16h25"


import os
import unittest
from unittest.mock import patch
from tests.tools import checkTools as chk
from tools.model import Model, m1, m2, m3, m4
from tools.base import Strategy
from tools.evaluations_muettes import adaptive_evaluation as evaluate
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
module_funs = "backward_search update_storage"

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
class Fool(Strategy):
    """ random CD """
    def __init__(self, m:Model=m1):
        super().__init__(0, 0, m)
    def next_action(self): return random.choice('CD')
class Periodique(Strategy):
    def __init__(self, mot:str):
        self.word = 'D' if mot=='' else mot
        style = 'DC'.index(self.word[0])*2 -1
        super().__init__(style)
    def next_action(self): return self.word[self.count%len(self.word)]
class Tit4Tat(Strategy):
    def __init__(self, model:Model=m1):
        super().__init__(1,1,model)
    def next_action(self):
        if self.memory_size == 0: return self.style
        return self.adv_action(self.memory[-1])
#=============================================================#

class TestDefault(unittest.TestCase):
    """ find the attributes and methods fullfilled """
    def setUp(self):
        """ init """
        self.kname = "Motif"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.rews = m4.reward_names
        
    def test_check(self):
        """ collect datas """
        _latt = "rules_system"
        _lmeth0 = "reset_learning next_action specific_reset"
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

class TestBackward(unittest.TestCase):
    """ looking for similar patterns """
    def setUp(self):
        self.att = "backward_search"
        if self.att in chk.check_module(tp, module_funs):
            raise self.skipTest("'{}' not found in {}"
                                    "".format(self.att, tp.__name__))

    def subtest_signature(self, found):
        self.assertIsInstance(found, tuple,
                              "got {} expecting {}"
                              "".format(type(found), tuple))
        self.assertEqual(len(found), 2,
                              "got len {} expecting {}"
                              "".format(len(found), 2))
        self.assertIsInstance(found[0], list,
                              "got type {} expecting {}"
                              "".format(type(found[0]), list))
        self.assertIsInstance(found[1], int,
                              "got type {} expecting {}"
                              "".format(type(found[1]), int))
        
    def test_return(self):
        """ check the signature """
        _in = "un deux trois quatre cinq 1 2 3 4 5 toto mirror"
        for arg in _in.split():
            with self.subTest(chaine=arg):
                self.subtest_signature(getattr(tp, self.att)(arg))
        self.subtest_signature(getattr(tp, self.att)(''))
                
    def test_nosol(self):
        """ check expected results when no sol exists """
        _2 = [], 0
        for arg in ('', 'R', 'X', 'AX', 'ABCD',):
            with self.subTest(chaine=arg):
                _1 = getattr(tp, self.att)(arg)
                self.assertEqual(_1, _2, "expecting {}, found {} with {}"
                                 "".format(_2, _1, arg))
                
    def test_basic_onesol(self):
        """ check expected results for unique sol of size 1 """
        _in = ('AA', "xAyA", "1212", "xXYX")
        for arg in _in:
            _2 = [arg.index(arg[-1])], 1
            with self.subTest(chaine=arg):
                _1 = getattr(tp, self.att)(arg)
                self.assertEqual(_1, _2, "expecting {}, found {} with {}"
                                 "".format(_2, _1, arg))

    def subtest_samples(self, un, deux, trois=None):
        for x,y,z in zip(un, deux, deux if trois is None else trois):
            if trois is None: z += 1
            _2 = ([y], z) if not isinstance(y, list) else (y, z)
            with self.subTest(chaine=x):
                _1 = getattr(tp, self.att)(x)
                self.assertEqual(_1, _2, "expecting {}, found {} with {}"
                                 "".format(_2, _1, x))


    def test_onesol(self):
        """ check expected results with unique sol of size > 1 """
        _in = ('AAA', '12323123', '13412313', '12345545345234543212345')
        _out = (1, 2, 1, 4)
        self.subtest_samples(_in, _out)

    def test_onesol_speedup(self):
        """ check expected results with unique sol speedup case """
        _in = ('1233123', '12345123412312112345', '123333323', 'AAAAAAAAAA')
        _out = (2, 4, 2, 8)
        _sz = (2, 1, 2, 9)
        self.subtest_samples(_in, _out, _sz)

    def test_multi(self):
        """ check multiple solutions """
        _in = ('121212312', '01300130124013', '0123231301230124012')
        _out = ([1,3,5], [2,6], [2, 10, 14])
        _sz = (2, 3, 3)
        self.subtest_samples(_in, _out, _sz)
                     
    def test_sol_various_len(self):
        """ check solutions with repeated sub pattern """
        _in = ('a'*3+'X')*3, ('ab'*3+'CD')*5, "xyxzxyxwxyxyuyx"
        _out = ([7], [31], [2, 6, 10])
        _sz = (5, 25, 2)
        self.subtest_samples(_in, _out, _sz)
            
class TestMotif(unittest.TestCase):
    """ follow the rules """
    def setUp(self):
        self.kname = "Motif"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.required = "reset_learning"

    def sub_required(self):
        _att = "backward_search"
        if _att in chk.check_module(tp, module_funs):
            raise self.skipTest("required '{}' but not found in {}"
                                    "".format(_att, tp.__name__))
        for att in self.required.split():
            self.subtest_missing(att, "'{}' is required !!!")

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
            self.skipTest(_msg.format(att)+" for {0.kname}".format(self))

    @patch('builtins.print')
    def test_compteurs_ok_mem3(self, mock_prn):
        """ good + behavior = count with max mem 3 """
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        # attribute exists, makes some evaluation
        self.o = self.K(Gentle())
        _advl = (Gentle(), Bad(),
                 Periodique("CD"), Periodique("CDDDC"))
        _expectl = [2], [3], [3,1], [3]*10
        for _adv, _expect in zip(_advl, _expectl):
            with self.subTest(adv=_adv.__class__.__name__):
                for i in range(1, 10):
                    with self.subTest(nbMatch=i):
                        _0 = evaluate(self.o, _adv, i, 4, 5)
                        _1 = self.o.good_guess + self.o.default_behavior
                        self.assertEqual(_1, self.o.count,
                                         "this is odd, got {} expect {}"
                                         "".format(_1, self.o.count))
                        _e = 0 if i > len(_expect) else _expect[i-1]
                        self.assertEqual(self.o.default_behavior, _e,
                                         "default_behavior should be {}"
                                         "found {}"
                                         "".format(_e, self.o.default_behavior))

    @patch('builtins.print')
    def test_compteurs_ok_mem50(self, mock_prn):
        """ good + behavior = count with max mem 50 """
        self.required = self.required + ' next_action update_knowledge'
        self.sub_required()
        # attribute exists, makes some evaluation
        self.o = self.K(Tit4Tat(), 50)
        _advl = (Gentle(), Bad(),
                 Periodique("DC"), Periodique("DDC"))
        _expectl = [2], [3], [5], [5,0,1,1]
        for _adv, _expect in zip(_advl, _expectl):
            with self.subTest(adv=_adv.__class__.__name__, expect=_expect):
                for i in range(5, 10):
                    with self.subTest(nbMatch=i):
                        _0 = evaluate(self.o, _adv, i, 10, 11)
                        _1 = self.o.good_guess + self.o.default_behavior
                        if len(_expect) == 1:
                            self.assertEqual(_1, self.o.count,
                                         "this is odd, got {} expect {}"
                                         "".format(_1, self.o.count))
                        else:
                            self.assertLessEqual(_1, self.o.count,
                                         "this is odd, got {} expect {}"
                                         "".format(_1, self.o.count))
                            
                        _e = 0 if i > len(_expect) else _expect[i-1]
                        self.assertEqual(self.o.default_behavior, _e,
                                         "default_behavior should be {}"
                                         "found {}"
                                         "".format(_e, self.o.default_behavior))

    def test_compteurs_get_reward(self):
        """ expect no change in guess, nor in behavior """
        self.required = self.required + ' update_knowledge'
        self.sub_required()
        # attribute exists
        self.o = self.K(Bad(), 5)
        # motif can be found *but* no decision taken
        _rewards = "RRRPRS"
        _local_memory = ''
        for i,x in enumerate(_rewards):
            self.o.get_reward(x)
            _local_memory += x
            _1 = self.o.good_guess
            _2 = self.o.default_behavior
            self.assertEqual(_2, 0,
                             "default_behavior do not appear after action"
                             " found {}".format(_2))
            self.assertEqual(_1, 0,
                             "no motif could exist found {}"
                             "".format(_1))

            _3 = tp.backward_search(_local_memory)
            if i < 1 or x in 'PS':
                self.assertEqual(len(_3[0]), 0,
                                 "no motif extracted from {}"
                                 "".format(_local_memory))
            else:
                self.assertGreater(len(_3[0]), 0,
                                   "motif(s) extracted from {}"
                                   "".format(_local_memory))
            
    @patch('builtins.print')
    def test_pattern(self, mock_prn):
        """ test the patterns """
        self.required += " rules_system update_knowledge"
        self.required += " next_action specific_reset"
        _rew = "TPRPRTTPR RSTPRSPRSTPRS RRRRRR".split()
        _pats = "TPR TPRS RRRRR".split()
        _acts = "DDC"
        self.sub_required()
        self.o = self.K(Gentle(), 17)
        for i in range(3):
            with self.subTest(rewards=_rew[i]):
                self.o.reset_learning()
                self.o.reset()
                for r in _rew[i]:
                    _ = self.o.next_action()
                    self.o.get_reward(r)
                _0 = self.o.count
                self.assertEqual(_0, len(_rew[i]),
                                 f"count expected {len(_rew[i])} found {_0}")
                _1 = self.o.next_action()
                self.assertEqual(_1, _acts[i],
                                 f"action expected {_acts[i]} found {_1}")
                _2 = self.o.rules_system
                self.assertTrue(_pats[i] in _2,
                              f"pattern expected {_pats[i]} found {_2}")
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestDefault, TestMotif, )
    
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
    
