#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.02.20"
__usage__ = "Project 2024: tests Jalon 02"
__update__ = "30.01.24 17h50"


import os
import unittest
from tests.tools import checkTools as chk
from tools.model import m1, m2, m3, m4
from tests import test_strategies_jalon01 as j01
import itertools
import random

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

def frequency(obj, repeat:int, error:int, kargs, verbose=False):
    """ check the frequency of some events
        require obj.next_action()
    """
    if chk.check_flush(): print('.', end='', flush=True)
    else: print('.', end='')
        
    _ = [obj.next_action() for _ in range(repeat) ]
    _1 = [
        (len(_)*kargs[key] ==_.count(key) if kargs[key] in (0,1)
        else
         _.count(key) -error <= repeat*kargs[key] <= _.count(key) + error)
                for key in kargs]
    if verbose and not all(_1):
        print(repeat, error, kargs, [_.count(key) for key in kargs])
    return _1

class TestMarkov(unittest.TestCase):
    """ memory length 1 """
    def setUp(self):
        self.kname = "Markov"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        self.samples = [0, 1/4, 1/3, 1/2, 2/3, 1, -1, -.5, 2]
        self.models = m3, m4
        random.seed(42) # replication purpose

    def test_klass(self):
        """ test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))


    def subtest_size(self, sz):
        _0 = itertools.product([0,1], repeat=sz)
        for m in range(2):
            for p in _0:
                _s = random.choice([-1,0,1])
                self.o = self.K(_s, p, self.models[m])
                chk.check_attr(self.o, 'actions')
                self.assertTrue(self.models[m].actions == self.o.actions,
                                "'actions' is wrong")
                _latt = "probabilities style".split()
                for att in _latt:
                    chk.guard_ro(self, att)
                
                _1 = self.o.probabilities
                self.assertTrue(len(_1) == 4,
                                "found {}, need 4 values".format(_1))
                _2 = self.o.style
                _3 = "aCD"
                self.assertEqual(_3[_s], _2,
                                 "'style' is wrong found {}, param was {}"
                                 "".format(_2, _s))
    def test_init_short(self):
        """ check that we can work with incomplete data """
        self.subtest_size(2)

    def test_init_long(self):
        """ check that we can work with long data """
        self.subtest_size(5)

    def subtest_autotest(self, expect:bool):
        _0 = itertools.product(self.samples, repeat=4)
        for p in _0:
            if (any([self.samples[_] in p for _ in (-1, -2)])
                and expect): continue
            if (any([self.samples[_] not in p for _ in (-1, -2)])
                and not expect): continue
            self.o = self.K(1, p, self.models[0])
            chk.guard_meth(self, 'auto_test')
            self.assertEqual(self.o.auto_test(), expect,
                             "'auto_test' is wrong for {}".format(p))
                
    def test_auto_test_success(self):
        """ auto_test() should succeed """
        self.subtest_autotest(True)
    def test_auto_test_failure(self):
        """ auto_test() should fail """
        self.subtest_autotest(False)

    def test_next_action_validity(self):
        """ 1st move control """
        self.o = self.K(-1, (1,1,1,1), self.models[0])
        j01.next_action(self, self.models[0], first='D')
        self.o = self.K(1, (0,0,0,0), self.models[0])
        j01.next_action(self, self.models[0], first='C')

    def test_rule_event(self):
        """ verify that, after some event, things happen """
        _att = 'next_action'
        _rew = "TRPS"
        _probas = []
        # only valid prob are examined
        _probas.extend([ (0,(x,0,1,0)) for x in self.samples[:-2] ])
        _probas.extend([ (1,(1,x,0,0)) for x in self.samples[:-2] ])
        _probas.extend([ (2,(0,1,x,1)) for x in self.samples[:-2] ])
        _probas.extend([ (3,(1,1,1,x)) for x in self.samples[:-2] ])
        for i,x in enumerate(_rew):
            for r,v in _probas:
                self.o = self.K(0, v, self.models[0])
                chk.guard_meth(self, _att)
                self.o.get_reward(x)
                # exactitudiness might happen
                if v[i] in (0,1): repeat, error=1000,0
                else: repeat, error = 10000, 200
                if v[i] >= 0:
                    _1 = frequency(self.o, repeat, error,
                                   {"C": v[i], 'D': 1-v[i]})
                else:
                    _1 = frequency(self.o, repeat, error,
                                   {"C": 1/2, 'D': 1/2})
                    
                self.assertTrue(all(_1),
                                "act = '{}' rew = '{}' p = {} freq = {}"
                                "".format(self.models[0].actions, x,v,_1))
                self.o = self.K(0, v, self.models[1])
                self.o.get_reward(x)
                if v[i] >= 0: _expected = {"C": v[i],
                                           'D': .5*(1-v[i]),
                                           'R': .5*(1-v[i]),
                                           }
                else: _expected = {_: 1/3 for _ in "RDC"}
                # never exact
                _1 = frequency(self.o, 10000, 200, _expected)
                self.assertTrue(all(_1),
                                "act = '{}' rew = '{}' p = {} freq = {}"
                                "".format(self.models[1].actions, x,v,_1))

                
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestMarkov, )
    
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
    
