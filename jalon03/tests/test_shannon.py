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
from tools.base import Strategy, AbstractLearner
from tools.model import Model, m1, m2, m3, m4
import random
import itertools

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
class Fool(Strategy):
    """ always D """
    def __init__(self, m:Model=m1):
        super().__init__(0, 0, m)
    def next_action(self): return random.choice('CD')

class TestDefault(unittest.TestCase):
    """ find the attributes and methods fullfilled """
    def setUp(self):
        """ init """
        self.kname = "Shannon"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.rews = m4.reward_names
        
    def test_check(self):
        """ collect datas """
        _latt = "shannon_memories last_index rules_system"
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

def build_key(mem:str) -> str:
    """ requires len(mem) > 1 & x in 'RTPS' for x in mem 
        victory is '1', loss is '0'
        keep is '1', change is '0'
    """
    def victory(rew):
        return '1' if rew in 'RS' else '0'
    def behavior():
        """ build RR RT TR TT PP SP SS PS then looks if mem is present """
        # he had cooperated twice built from my point of view
        g = set(''.join(x) for x in itertools.product("RT", repeat=2))
        # he had defected twice built from my point of view
        g.update(''.join(x) for x in itertools.product("PS", repeat=2))
        return '1' if mem[-2:] in g else '0'
    return ''.join([victory(mem[-2]), behavior(), victory(mem[-1])])
        
                 
class TestShannon(unittest.TestCase):
    """ follow the rules """
    def setUp(self):
        self.kname = "Shannon"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.required = "reset_learning"
        self.st = [Gentle(), Bad()]
        self.keys = [''.join(x) for x in itertools.product('01', repeat=3)]

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

    
    def test_ro(self):
        """ verify ro attributes """
        self.sub_required()
        _latt = "last_index shannon_memories".split()
        _types = (str, tuple)
        _values = ('', 'NA')
        for att in _latt:
            self.subtest_missing(att)
        self.o = self.K(self.st[0])
        self.o.reset_learning()
        for i in range(2):
            chk.guard_ro(self, _latt[i])
            _1 = getattr(self.o, _latt[i])
            self.assertIsInstance(_1, _types[i],
                                  "'{}' expecting {} found {}"
                                  "".format(_latt[i], _types[i], type(_1)))
            if i == 0:
                self.assertEqual(_1, _values[i],
                                 "'{}' should {}, found {}"
                                 "".format(_latt[i], _values[i], _1))
            else:
                self.assertEqual(len(_1), 8,
                                 "'{}' wrong size found {}"
                                 "".format(_latt[i], len(_1)))
                for j,x in enumerate(_1):
                    self.assertEqual(x, _values[i],
                                     "'{}[{}]' should be '{}'"
                                     "".format(_latt[i], j, _values[i]))


    def find_rule(self, mem:str) -> str:
        """ get the rule from the mem """
        return '' if len(mem) < 2 else build_key(mem)

    def sub_check_equal(self, _latt:str, _val:list, msg:str='>'):
        """ check evaluation """
        _v = [getattr(self.o, att) for att in _latt]
        for name,found,expect in zip(_latt, _v, _val):
            with self.subTest(att=name):
                self.assertEqual(found, expect,
                                 "{}: '{}' should be {}, found {}"
                                "".format(msg, name, expect, found))
            
    def subtest_first_steps(self, event=''):
        """ requires all the attributes exist """
        self.o.reset_learning() # start from fresh
        _cpt = "good_guess default_behavior last_index".split()
        self.sub_check_equal(_cpt, (0,0,''))
        _count = 0
        for e in event:
            _mem = event[:_count]
            _last = self.find_rule(_mem)
            _ = self.o.next_action()
            _count += 1
            self.sub_check_equal(_cpt, (0,_count,_last),
                                 ">> after next_action with mem {}\n"
                                 "".format(_mem))
            self.o.get_reward(e)
            self.sub_check_equal(_cpt, (0,_count,_last),
                                 ">> after get_reward with old mem {}\n"
                                 "".format(_mem))
            
    @patch('builtins.print')
    def test_first_steps(self, mock_prn):
        """ tests the 4 first steps """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        for default in self.st:
            with self.subTest(default=default.__class__.__name__):
                self.o = self.K(default)
                self.subtest_first_steps("RTR")

    def subtest_meme(self, adv, reset=20):
        """ whatever happens we are in PP or RR 
            requires reset > 4
        """
        self.assertGreater(reset, 4, "cant process subtest_meme")
        _rew = 'P' if 'Bad' in adv.__class__.__name__ else 'R'
        _win = '0' if _rew == 'P' else '1'
        _key = ''.join([_win, '1', _win])
        _idx = self.keys.index(_key)
        _val = "NA gn gr".split()
        _cpt = "good_guess default_behavior last_index".split()
        for _count in range(2):
            self.sub_check_equal(_cpt, (0,_count,''))
            self.o.next_action()
            self.sub_check_equal(_cpt, (0,_count+1,''))
            self.o.get_reward(_rew)
            self.sub_check_equal(_cpt, (0,_count+1,''))
        _right = 0
        for _count in range(2, 4):
            self.o.next_action()
            self.sub_check_equal(_cpt, (0,_count+1,_key))
            _1 = self.o.shannon_memories[_idx]
            self.assertEqual(_1, _val[_right],
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _val[_right], _1))
            self.o.get_reward(_rew)
            _right += 1
            _2 = self.o.shannon_memories[_idx]
            self.sub_check_equal(_cpt, (0,_count+1,_key))
            self.assertEqual(_2, _val[_right],
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _val[_right], _2))
            
        for _count in range(4, reset):
            self.o.next_action()
            self.sub_check_equal(_cpt, (_count-4, 4, _key))
            _1 = self.o.shannon_memories[_idx]
            self.assertEqual(_1, _val[_right],
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _val[_right], _1))
            self.o.get_reward(_rew)
            _2 = self.o.shannon_memories[_idx]
            self.sub_check_equal(_cpt, (_count-3, 4, _key))
            self.assertEqual(_2, _val[_right],
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _val[_right], _2))
        if reset==20: return
        self.o.reset()
        self.sub_check_equal(_cpt, (0, 0, ''))
        for _count in range(reset, reset+10):
            self.o.next_action()
            self.sub_check_equal(_cpt, (_count-reset, 0, _key))
            _1 = self.o.shannon_memories[_idx]
            self.assertEqual(_1, _val[_right],
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _val[_right], _1))
            self.o.get_reward(_rew)
            _2 = self.o.shannon_memories[_idx]
            self.sub_check_equal(_cpt, (_count-reset+1, 0, _key))
            self.assertEqual(_2, _val[_right],
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _val[_right], _2))

    @patch('builtins.print')        
    def test_me_me(self, mock_prn):
        """ test me against me """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        for default in self.st:
            with self.subTest(default=default.__class__.__name__):
                self.o = self.K(default)
                self.subtest_meme(default)

    @patch('builtins.print')        
    def test_me_me_reset(self, mock_prn):
        """ test me against me with reset involved """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        for default in self.st:
            with self.subTest(default=default.__class__.__name__):
                self.o = self.K(default)
                self.subtest_meme(default, 15)

    def subtest_diff(self, adv, reset=20):
        """ learner != target 
            Good vs Bad : SP ; Bad vs Good TR
            build_key -> str '000' => '111'

            requires reset > 2
        """
        self.assertGreater(reset, 2, "cant process subtest_diff")
        def reward(idem:bool, adv_act:str) -> str:
            """ get the reward """
            return (('P' if idem else 'S') if adv_act == 'D'
                    else ('R' if idem else 'T'))
            
        _val = "NA gn gr".split()
        _cpt = "good_guess default_behavior last_index".split()
        _adv_act = adv.next_action()

        _db, _gg = 0, 0
        for _count in range(2):
            self.sub_check_equal(_cpt, (_gg, _db, ''))
            _a = self.o.next_action() == _adv_act
            _db += 0 if _a else 1
            self.sub_check_equal(_cpt, (_gg, _db, ''))
            self.o.get_reward(reward(_a, _adv_act))
            self.sub_check_equal(_cpt, (_gg, _db, ''))
        _rules = {}
        for _count in range(2, reset):
            _a = self.o.next_action() == _adv_act
            _db += 0 if _a else 1
            _idx = self.keys.index(build_key(self.o.memory))
            _key = self.keys[_idx]
            _rules[_idx] = min(2, _rules.get(_idx, -1)+1)
            self.sub_check_equal(_cpt, (_gg, _db, _key))
            _1 = self.o.shannon_memories[_idx]
            _2 = _val[_rules[_idx]]
            self.assertEqual(_1, _2,
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _2, _1))
            self.o.get_reward(reward(_a, _adv_act))
            _gg += 1 if _a else 0
            self.sub_check_equal(_cpt, (_gg, _db, _key))
            _1 = self.o.shannon_memories[_idx]
            _2 = _val[min(2, 1+_rules[_idx])]
            self.assertEqual(_1, _2,
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _2, _1))
        if reset==20: return
        _old = self.o.memory
        self.o.reset()
        self.sub_check_equal(_cpt, (0, 0, ''))
        _db, _gg = 0, 0
        for _count in range(reset, reset+10):
            _a = self.o.next_action() == _adv_act
            _db += 0 if _a else 1
            _idx = self.keys.index(build_key(_old+self.o.memory))
            _key = self.keys[_idx]
            _rules[_idx] = min(2, _rules.get(_idx, -1)+1)
            self.sub_check_equal(_cpt, (_gg, _db, _key))
            _1 = self.o.shannon_memories[_idx]
            _2 = _val[_rules[_idx]]
            self.assertEqual(_1, _2,
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _2, _1))
            self.o.get_reward(reward(_a, _adv_act))
            _gg += 1 if _a else 0
            self.sub_check_equal(_cpt, (_gg, _db, _key))
            _1 = self.o.shannon_memories[_idx]
            _2 = _val[min(2, 1+_rules[_idx])]
            self.assertEqual(_1, _2,
                             "rule expect {} -> {}, found -> {}"
                             "".format(_key, _2, _1))
    @patch('builtins.print')
    def test_bad_gentle(self, mock_prn):
        """ test Bad_learner against Gentle """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        self.o = self.K(self.st[1])
        self.subtest_diff(self.st[0])

    @patch('builtins.print')
    def test_bad_gentle_reset(self, mock_prn):
        """ test Bad_learner against Gentle, reset involved """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        self.o = self.K(self.st[1])
        self.subtest_diff(self.st[0], 15)

    @patch('builtins.print')
    def test_gentle_bad(self, mock_prn):
        """ test Gentle_learner against Bad """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        self.o = self.K(self.st[0])
        self.subtest_diff(self.st[1])

    @patch('builtins.print')
    def test_gentle_bad_reset(self, mock_prn):
        """ test Gentle_learner against Bad, reset involved """
        self.required += " next_action update_knowledge"
        self.required += " last_index shannon_memories"
        self.sub_required()
        self.o = self.K(self.st[0])
        self.subtest_diff(self.st[1], 10)

def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestDefault, TestShannon, )
    
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
    
