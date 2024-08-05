#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.02.20"
__usage__ = "Project 2024: tests Jalon 02 Stochastic"
__update__ = "30.01.24 17h50"


import os
import unittest
from tests.tools import checkTools as chk
from tools.model import m1, m2, m3, m4
import random
import itertools
from tests import test_strategies_jalon01 as j01
from tests.test_markov import frequency

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

class TestStochastique(unittest.TestCase):
    """ memory length 1 """
    def setUp(self):
        self.kname = "Stochastic"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose
        self.models = (m1, m2, m3, m4)

    def test_klass(self):
        """ test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategie"
                        "".format(self))

    def subtest_init(self, probas, m):
        """ helper for test_init_** """
        self.o = self.K(probas, m)
        chk.check_attr(self.o, 'actions')
        self.assertTrue(m.actions == self.o.actions,
                        "'actions' is wrong")
        _latt = "probabilities style memory_limit".split()
        for att in _latt:
            chk.guard_ro(self, att)

        # probabilities
        _1 = self.o.probabilities
        self.assertTrue(len(_1) == 1+2**len(m.actions),
                    "found {}, need {} values"
                    "".format(_1, len(probas)))
        # style
        _2 = self.o.style
        _3 = "DCa"
        self.assertEqual(_3[probas[0]], _2,
                     "'style' is wrong found {}, param was {}"
                     " & 1st action should be {}"
                    "".format(_2, probas[0], _3[probas[0]]))
        # size
        self.assertEqual(self.o.memory_limit, 1,
                         "bad memory size, expecting 1, found {}"
                         "".format(self.o.memory_limit))
        
    def test_init_perfect(self):
        """ the simple case """
        for m in self.models:
            _ =  itertools.combinations_with_replacement([0,1,-1],
                                                         1+2**len(m.actions))
            for probas in _:
                with self.subTest(model=m, probas=probas):
                    self.subtest_init(probas, m)
                    

    def test_init_short(self):
        """ missing values """
        for m in self.models:
            _ =  itertools.combinations_with_replacement([0,1,-1],2)
            for probas in _:
                with self.subTest(model=m, probas=probas):
                    self.subtest_init(probas, m)
                    _4 = self.o.probabilities[2:]
                    self.assertTrue(all([x==-1 for x in _4]),
                                    "bad values in {}".format(_4))

    def test_init_exceeding(self):
        """ too much values """
        for m in self.models:
            _ =  itertools.combinations_with_replacement([0,1,-1],10)
            for probas in _:
                with self.subTest(model=m, probas=probas):
                    self.subtest_init(probas, m)

    def subtest_autotest(self, expect:bool):
        """ helper """
        _att = 'auto_test'
        if expect:
            for m in self.models:
                p = [.45 for i in range(4)]
                p.extend([-1 for _ in range(2**len(m.actions) -3)])
                random.shuffle(p)
                self.o = self.K(p, m)
                chk.guard_meth(self, _att)
                self.assertTrue(self.o.auto_test(), "p = {}".format(p))
                if len(m.actions) == 3: continue
                p = [.7 for i in range(4)]
                p.extend([.5 for _ in range(2**len(m.actions) -3)])
                random.shuffle(p)
                self.o = self.K(p, m)
                self.assertTrue(self.o.auto_test(), "p = {}".format(p))
        else:
            for m in self.models:
                if len(m.actions) == 2: continue
                p = [.7 for i in range(4)]
                p.extend([.5 for _ in range(2**len(m.actions) -3)])
                random.shuffle(p)
                self.o = self.K(p, m)
                self.assertFalse(self.o.auto_test(), "p = {}".format(p))
            
        
    def test_auto_test_success(self):
        """ auto_test() should succeed """
        self.subtest_autotest(True)
    def test_auto_test_failure(self):
        """ auto_test() should fail """
        self.subtest_autotest(False)

    def test_get_probas_signature(self):
        """ check that type is correct """
        _att = "get_probabilities"
        self.o = self.K([1], m1)
        chk.guard_meth(self, _att, ('T',))
        _0 = getattr(self.o, _att)('')
        self.assertIsInstance(_0, tuple,
                              "'{}' type found '{}' expecting tuple"
                              .format(_att, type(_0)))

    def test_get_probas_return(self):
        """ check that type is correct """
        _att = "get_probabilities"
        self.o = self.K([1], m1)
        chk.guard_meth(self, _att, ('T',))
        # not a reward
        _0 = getattr(self.o, _att)('')
        self.assertEqual(len(_0), 0,
                         "wrong size found {}".format(len(_0)))
        # a reward
        _0 = getattr(self.o, _att)('T')
        self.assertEqual(len(_0), 3,
                         "wrong size found {}".format(len(_0)))
        # a 3 actions model
        self.o = self.K([1], m2)
        _0 = getattr(self.o, _att)('T')
        self.assertEqual(len(_0), 3,
                         "wrong size found {}".format(len(_0)))

    def test_get_probas_values(self):
        """ a model with 2 actions provides (x, y, 0) """
        _att = "get_probabilities"
        for m in m1, m3:
            _ =  itertools.combinations_with_replacement([0,1,-1],2)
            for probas in _:
                with self.subTest(model=m, probas=probas):
                    self.o = self.K(probas, m)
                    chk.guard_meth(self, _att, ('T',))
                    for rew in m.reward_names:
                        _1 = getattr(self.o, _att)(rew)
                        self.assertEqual(_1[-1], 0,
                                         "expecting last to be 0, found {}"
                                         "".format(_1))

    def test_get_probas_sum(self):
        """ probabilities should be 1 """
        _att = "get_probabilities"
        _dom = [0, 1, -1, .25, .5, .75, 1/3, 2/3]
        for m in self.models:
            _ =  itertools.combinations_with_replacement(_dom, 3)
            for probas in _:
                self.o = self.K(list(probas)*3, m)
                chk.guard_meth(self, _att, ('T',))
                chk.guard_meth(self, 'auto_test')
                if not self.o.auto_test(): continue
                for r in m.reward_names:
                    if r == "A": continue
                    with self.subTest(model=self.models.index(m),
                                      probas=probas, rew=r):
                        _1 = getattr(self.o, _att)(r)
                        self.assertAlmostEqual(sum(_1), 1,
                                         msg="expecting total 1, found {}"
                                         "".format(_1))

    def subtest_proba_sample(self, act:str, rew:str):
        """ helper to find values """
        _att = 'probabilities'
        idx = { 'T': (2,3), 'R': (1,3), 'P': (2,4), 'S': (1,4) }
        chk.check_attr(self.o, _att)
        _1 = getattr(self.o, _att)
        _2, _3 = [_1[x] for x in idx[rew]]

        if _2 == -1 and _3 == -1:
            _c = 1/2 ; _msg = "all unknown"
        elif _2 == -1:
            _c = _3 ; _msg = "one unknown"
        elif _3 == -1:
            _c = _2 ; _msg = "one unknown"
        else:
            _c = _2 + _3 - _2 * _3 ; _msg = "both known"

        _v = None
        if len(act) == 2: _r = 0
        else:
            _4, _5 = [_1[x+4] for x in idx[rew]]
            if _4 == -1 and _5 == -1:
                if "all" in _msg:
                    _v = (1/3, 1/3, 1/3) ; _msg = "equiproba"
                else:
                    _v = (_c, (1-_c)/2, (1-_c)/2) ; _msg = "equi-résidu C"
            else:
                if _5 == -1: _r = _4
                elif _4 == -1: _r = _5
                else: _r = _4 + _5 - _4*_5
                    
        if 'all' in _msg:
            _v = ((1 - _r)/2, (1 - _r)/2, _r)
            _msg = "equi-résidu R"
        elif _v is None:
            _R = (1 - _c)*_r
            _D = 1 - _c - _R
            _v = (_c, _D, _R)
            _msg = "all found"

        _P = self.o.get_probabilities(rew)
        for x,y in zip(_P, _v):
            self.assertAlmostEqual(x, y,
                                   msg=_msg+" found {} expected {}".format(x,y))

                    
    def test_get_probas_sample(self):
        """ check values for a given set """
        _att = "get_probabilities"
        _sample = [(-1, 1/2),
                   (1, -1, -1, -1, -1, -1, 1, -1, 2/3),
                   (0, 1/2, 1/3), (-1, 1/2, 1/3, 1/2),
                   (1, 1/2, 1/3, -1, -1, -1, -1, -1, 1),
                   (0, 1/4, 1/3, -1, 1/10, -1, -1, -1, 1),
                   (0, 0, 1/2, 1/2, 0) ]
        for m in (m1, m4):
            for p in _sample:
                self.o = self.K(p, m)
                chk.guard_meth(self, _att, ('R',))
                for r in m1.reward_names:
                    with self.subTest(m=m.actions, vect=p, rew=r):
                        self.subtest_proba_sample(m.actions, r)

    def test_next_action_validity(self):
        """ 1st move control """
        self.o = self.K((-1, 1), m1) # rand
        j01.next_action(self, m1, valid=m1.actions)
        self.o = self.K((1, 1), m1) # C
        j01.next_action(self, m1, first='C')
        self.o = self.K((0, 1), m1) # not C
        j01.next_action(self, m1, first='D')

    def subtest_rule(self, rew):
        _att = 'probabilities'
        idx = { 'T': (2,3), 'R': (1,3), 'P': (2,4), 'S': (1,4) }
        chk.check_attr(self.o, _att)
        _1 = getattr(self.o, _att)
        _2, _3 = [_1[x] for x in idx[rew]]

        if _2 == -1 and _3 == -1:
            _c = 1/2 ; _msg = "all unknown"
        elif _2 == -1:
            _c = _3 ; _msg = "one unknown"
        elif _3 == -1:
            _c = _2 ; _msg = "one unknown"
        else:
            _c = _2 + _3 - _2 * _3 ; _msg = "both known"

        _v = {'C':_c, 'D': 1 -_c}
        if _c in (0, 1): repeat, error = 1000, 0
        else: repeat, error = 5000, 100
        _1 = frequency(self.o, repeat, error, _v, True)
        self.assertTrue(all(_1),
                        "act = '{}' rew = '{}' p = {} freq = {}"
                        "".format(self.o.actions, rew, _v,
                                  self.o.get_probabilities(rew)))

    def test_rule_event(self):
        """ verify that, after some event, things happen """
        _att = 'next_action'
        _rew = "TRPS"
        _ = [0, 1, -1, 1/2]
        _0 = itertools.product(_, repeat=4)
        for p in _0:
            _1 = [random.choice(_)]
            _1.extend(p)
            r = random.choice(_rew)
            with self.subTest(proba=_1, reward=r):
                self.o = self.K(_1)
                self.o.get_reward(r)
                self.subtest_rule(r)
                
        
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestStochastique, )
    
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
    
