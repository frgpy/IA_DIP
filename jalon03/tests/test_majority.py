#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "18.02.20"
__usage__ = "Project 2024: tests Jalon 02"
__update__ = "30.01.24 17h45"


import os
import unittest
from tests.tools import checkTools as chk
from tools.model import m1, m2, m3, m4

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

class TestMajorite(unittest.TestCase):
    """ memory compute C/D majority """
    def setUp(self):
        self.args = ((), (0,), (-1,), (1,),
                     (0, -42,), (1, 3,), (-1, 5, m4))
        # style, size, actions have context
        self.context = ({"style": 'C', "memory_limit": 0,
                         "actions": m1.actions},
                        {"style": 'a', "memory_limit": 0,
                         "actions": m1.actions},
                        {"style": 'D', "memory_limit": 0,
                         "actions": m1.actions},
                        {"style": 'C', "memory_limit": 0,
                         "actions": m1.actions},
                        {"style": 'a', "memory_limit": -1,
                         "actions": m1.actions},
                        {"style": 'C', "memory_limit": 3,
                         "actions": m1.actions},
                        {"style": 'D', "memory_limit": 5,
                         "actions": m4.actions})
        
        self.defaults = {"idnum": 42,
                        "memory_size": 0,
                        "memory": '',
                        "count": 0,
                        "color": 42,
                        "name" : "Strat_042",
                        "surname": "Strat_042",
                        "majority": 0,}

        self.kname = "Majority"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

    def test_klass(self):
        """ test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))

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


    def test_majority_init(self):
        """ check the majority value """
        _att = "majority"
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            chk.guard_ro(self, _att)
            self.assertEqual(self.o.majority, 0,
                                "'{}' found {}, expecting 0"
                                "".format(_att, self.o.majority))

    def subtest_majority(self, sz:int):
        """ feeding with bananas """
        chk.check_attr(self.o, 'memory')
        _bananas = "PATATRASalcatrazPS"
        # "D.C.CC.D........DD"
        # values are computed by hands
        _expected = {0: [ 0, 0,0,0,0,0,0,0, 0, 0, 0, 0,0,0,0,0, 0, 0],
                     -1:[-1,-1,0,0,1,1,1,1, 1, 1, 1, 1,1,1,1,1, 0,-1],
                     3: [-1,-1,0,1,1,1,1,0,-1,-1, 0, 0,0,0,0,0,-1,-1],
                     5: [-1,-1,0,0,1,1,1,1, 1, 0,-1,-1,0,0,0,0,-1,-1]}
        cpt = 0
        for b in _bananas:
            self.o.get_reward(b)
            self.assertEqual(self.o.majority, _expected[sz][cpt],
                             "found {}, expecting {}"
                             "".format(self.o.majority,
                                       _expected[sz][cpt]))
            cpt += 1
            
    def test_majority_evolution(self):
        """ perform update and check that all is as expected """
        _att = "majority"
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            chk.check_attr(self.o, _att)
            with self.subTest(arg=args):
                self.subtest_majority(self.context[i]['memory_limit'])
                # reset is done
                chk.guard_meth(self, "reset")
                self.o.reset()
                self.assertEqual(self.o.majority, 0,
                                "'{}' found {}, expecting 0"
                                "".format(_att, self.o.majority))
            
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestMajorite, )
    
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
