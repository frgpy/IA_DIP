#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.02.20"
__usage__ = "Project 2024: tests jalon 03"
__update__ = "14.02.24 21h15"


import os
import unittest
from unittest.mock import patch
from tests.tools import checkTools as chk
from tools.model import m1, m2, m3, m4
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

def mock_prn(*args, **kwargs):
    """ no output allowed during tests """
    pass

class TestAutomaton(unittest.TestCase):
    """ follow the rules """
    def setUp(self):
        self.kname = "Automaton"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)
        random.seed(42) # replication purpose

    def test_klass(self):
        """ test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))

    def subtest_init(self, arg:int):
        """ verify the length of rules and size + content of rules """
        if arg < 4: memory_size = 0 ; val = 0
        elif arg < 20: memory_size = 1; val = 4
        elif arg < 84: memory_size = 2 ; val = 20
        else: memory_size = 3 ; val = 84
        _str = 'x'*arg

        _att = 'rules'
        self.o = self.K(1, _str)
        chk.check_attr(self.o, _att)
        try:
            self.rules = "C"*val
            self.skipTest("'{}' is not read_only".format(_att))
        except:
            self.assertEqual(self.o.rules, _str[:val],
                         "'rules' got {}, expecting {}"
                         "".format(len(self.o.rules), val))
        self.assertEqual(self.o.memory_limit, memory_size,
                         f"'memory_limit' got {self.o.memory_limit}, "
                         f"expecting {memory_size}")
        self.assertTrue(self.o.style == 'C',
                        f"not the correct style found {self.o.style}"
                        f" expect 'C'")

    @patch('builtins.print')    
    def test_init(self, mock_prn):
        """ check the __init__ """
        for i in range(90):
            with self.subTest(taille=i):
                self.subtest_init(i)
                
    @patch('builtins.print')    
    def test_auto_test_failure(self, mock_prn):
        """ should find a bad system of rules """
        self.o = self.K(0, '')
        chk.check_attr(self.o, "rules")
        chk.guard_meth(self, "auto_test")

        _1 = [random.choice(m2.actions) for _ in range(23)]
        if _1.count('R') == 0: _1[random.randrange(5,20)] = 'R'
 
        for m in (m1, m3):
            with self.subTest(model=m):
                self.o = self.K(1, _1, m)
                self.assertFalse(self.o.auto_test(),
                                 "index {} is 'R' not in {}"
                                 "".format(_1.index('R'), m.actions))

    @patch('builtins.print')    
    def test_auto_test_success(self, mock_prn):
        """ should find a good system of rules """
        self.o = self.K(1, '')
        chk.check_attr(self.o, "rules")
        chk.guard_meth(self, "auto_test")
        for m in (m1, m2, m3, m4):
            for i in (1, 7, 17, 29, 87):
                _1 = [random.choice(m.actions) for _ in range(i)]
                if _1[0] == 'R': _1[0] = random.choice("CD")
                _1 = ''.join(_1)
                with self.subTest(model=m, rules=_1):
                    self.o = self.K(0, _1, m)
                    self.assertTrue(self.o.auto_test(),
                                    "expect True for actions = '{}'\n"
                                    "rules {}".format(m.actions, _1))

    @patch('builtins.print')    
    def test_rule_event(self, mock_prn):
        """ verify that after some event, things happen """
        _att = 'next_action'
        _rew = "TPRS"
        _sz = 0, 4, 20, 84, 340 # size 0, 1, 2, 3
        _rules = ''.join([random.choice('CD') for _ in range(340)])
        _m = random.choice([m1, m2, m3, m4])
        for x in _sz:
            with self.subTest(size=x, rules=_rules[:x], model=_m):
                self.o = self.K(-1, _rules[:x], _m)
                chk.guard_meth(self, 'auto_test')
                chk.guard_meth(self, 'next_action')
                for _e in itertools.combinations_with_replacement(_rew, 5):
                    for x in _e:
                        self.o.get_reward(x)
                        _i = _m.encoding(self.o.memory)-1
                        _0 = self.o.next_action()
                        # style = -1 when memory_limit = 0
                        _1 = 'D' if self.o.memory_size==0 else _rules[_i]
                        self.assertEqual(_0, _1,
                                         "'next_action' found {} expect {}"
                                         " when memory is '{}'"
                                         "".format(_0, _1, self.o.memory))
        
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestAutomaton, )
    
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
    
