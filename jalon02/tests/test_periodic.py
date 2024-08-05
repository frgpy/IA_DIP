#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "17.02.20"
__usage__ = "Project 2024: tests Jalon 02 Periodic"
__update__ = "30.01.24 17h50"


import os
import unittest
from tests.tools import checkTools as chk
from tests import test_strategies_jalon01 as j01
from tools.model import m1, m2, m3, m4

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

class TestPeriodique(unittest.TestCase):
    """ no memory works on a cycle of actions """
    def setUp(self):
        self.args = [('',), ('C',), ('D',), ('CD',), ('DCD',) ]
        self.m = m3
        self.context = ({"style": 'D', "memory_size": 0,
                         "actions": self.m.actions},
                        {"style": 'C', "memory_size": 0,
                         "actions": self.m.actions},
                        {"style": 'D', "memory_size": 0,
                         "actions": self.m.actions},
                        {"style": 'C', "memory_size": 0,
                         "actions": self.m.actions},
                        {"style": 'D', "memory_size": 0,
                         "actions": self.m.actions},)
        
        self.defaults = {"idnum": 42,
                        "memory_limit": 0,
                        "memory": '',
                        "count": 0,
                        "color": 42,
                        "name" : "Strat_042",
                        "surname": "Strat_042",}

        self.kname = "Periodic"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))

    def test_word(self):
        """ check the word value """
        _att = "word"
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            chk.guard_ro(self, _att)
            _ = 'D' if args[0] == '' else args[0]
            self.assertEqual(self.o.word, _, "wrong value")
            # no changes after reset
            chk.guard_meth(self, "reset")
            self.o.reset()
            chk.guard_ro(self, _att)
            self.assertEqual(self.o.word, _, "wrong value")




    def subtest_def(self, idx:int):
        """ basic default values """
        for k,v in self.context[idx].items():
            if k == "actions": continue
            self.defaults[k] = v
        chk.sub_default(self)

    def test_default(self):
        """ default values subcases """
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

    def test_first_action_validity(self):
        """ verify we are good at 1st """
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                j01.next_action(self, self.m, first=self.context[i]['style'])

    def test_any_action_validity(self):
        """ verify that we are good at any step """
        import random
        _att = "next_action"
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
        
                chk.guard_meth(self, "get_reward", ('T',))
                chk.guard_meth(self, "reset")
                chk.guard_meth(self, _att)
                chk.guard_att(self, "actions")
                chk.guard_att(self, "word")
                self.o.reset()
                try:
                    _rew = random.choices(self.m.reward_names, k=20)
                except:
                    _rew = [random.choice(self.m.reward_names)
                            for _ in range(20)]
                _word = self.o.word*20
                for _1 in range(20):
                    self.assertEqual(self.o.count, _1,
                                     "count is buggy at step {}".format(_1))
                    _2 = self.o.next_action()
                    if len(self.o.word) == 0:
                        self.assertEqual(_2, "D",
                                         "found {}, expecting {}"
                                         "".format(_2, "D"))
                    else:
                        self.assertEqual(_2, _word[_1],
                                         "found {}, expecting {}"
                                         "".format(_2, _word[_1]))
                        
                    self.o.get_reward(_rew[_1])
        
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestPeriodique, )
    
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
