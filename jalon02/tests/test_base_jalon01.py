#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "27.01.20"
__usage__ = "Project 2024: tests Strategy"
__update__ = "16.01.24 10h40"


import os
import unittest
import random
from  tests.tools import checkTools as chk


"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

data = chk.Data()

class TestDefault(unittest.TestCase):
    """ find the attributes and methods fullfilled """
    def setUp(self):
        self.K = getattr(tp, "Strategy")
        
    def test_check(self):
        """ find what has been done, if any ... """
        self.o = self.K()
        _latt = "idnum color surname name style actions count"
        _latt += " memory_size memory memory_limit has_memory"
        _lmeth0 = "__repr__ __str__  history reset next_action"
        _lmeth1 = "get_reward my_action adv_action"
        _rewlst = tp.m2.reward_names
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
                getattr(self.o, att)
                data.yes += 1
                data.subtests.add(att)
                if chk.check_flush(): print('.', flush=True, end='')
            except Exception as _e:
                data.no += 1
                data.report[att] = str(_e)

        for att in _lmeth1.split():
            
            _rew = random.choice(_rewlst)
            try:
                getattr(self.o, att)(_rew)
                data.yes += 1
                data.subtests.add(att)
                if chk.check_flush(): print('.', flush=True, end='')
            except Exception as _e:
                data.no += 1
                data.report[att] = str(_e)

        print(data)

class TestAttributes(unittest.TestCase):
    """ some data are verified unless they haven't been set properly """

    def setUp(self):
        self.K = getattr(tp, "Strategy")
        self.K.ID = 42
        self.o = self.K()

    def test_idnum(self):
        """ check idnum default """
        _att = "idnum"
        _val = 42
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_color(self):
        """ check color default """
        _att = "color"
        _val = self.o.idnum
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_color_success(self):
        """ set color within range value """
        _att = "color"
        _val = random.randrange(0, 256)
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, self.o.idnum,
                         "expecting {} found {}".format(self.o.idnum, _0))
        setattr(self.o, _att, _val)
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_color_failure(self):
        """ set color with out of range value """
        _att = "color"
        _val = self.o.idnum
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        setattr(self.o, _att, random.randrange(-256,0))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        setattr(self.o, _att, random.randrange(666,6666))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        setattr(self.o, _att, "blue")
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        
    def test_name(self):
        """ check name default """
        _att = "name"
        _val = "Strat_{:03d}".format(self.o.idnum)
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_surname(self):
        """ check surname default """
        _att = "surname"
        _val = self.o.name
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_set_surname_success(self):
        """ check surname behavior """
        _att = "surname"
        _val = self.o.name
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        _val = "mmc_test"
        setattr(self.o, _att, _val)
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_set_surname_failure(self):
        """ check surname behavior in case of non str """
        _att = "surname"
        _val = self.o.name
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        for _val in (42, [], 37.2):
            with self.subTest(value=_val):
                setattr(self.o, _att, _val)
                _0 = getattr(self.o, _att)
                self.assertTrue(isinstance(_0, str),
                            "expecting {} found {}".format(str, type(_0)))
        
    def test_size(self):
        """ check memory_limit default """
        _att = "memory_limit"
        _val = 0
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_hasmem(self):
        """ check has_memory default """
        _att = "has_memory"
        _val = False
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        
    def test_memsz(self):
        """ check memory_size default """
        _att = "memory_size"
        _val = 0
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_memory(self):
        """ check memory default """
        _att = "memory"
        _val = ''
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        
    def test_count(self):
        """ check count default """
        _att = "count"
        _val = 0
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))

    def test_style(self):
        """ check style default """
        _att = "style"
        _val = "C"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        self.assertEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))


    def test_actions(self):
        """ check actions default """
        _att = "actions"
        _val = tp.m1.actions
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)
        # for 3.2 otherwise need sorted + assertEqual
        self.assertCountEqual(_0, _val,
                         "expecting {} found {}".format(_val, _0))
        


class TestMethods0(unittest.TestCase):
    """ methods without parameter """
    def setUp(self):
        self.K = getattr(tp, "Strategy")
        self.o = self.K()

    def test_repr(self):
        """ check that repr is as expected Strategy(p1, p2, Model(a1, a2)) """
        _att = "__repr__"
        _val = str
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)()
        self.assertEqual(type(_0), _val,
                         "expecting {} found {}".format(_val, type(_0)))
        _1 = "Strategy" in _0
        _2 = 'C' in _0
        _3 = '0' in _0
        _4 = 'Model' in _0
        _5 = _0.count('(') == 2 and _0.count(')') == 2
        _a = [_1, _2, _3, _4, _5]
        self.assertTrue(all(_a),
                        "missing information {}".format(_0))

    
    def test_str(self):
        """ check that __str__ is a string """
        _att = "__str__"
        _val = str
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)()
        self.assertEqual(type(_0), _val,
                         "expecting {} found {}".format(_val, type(_0)))


    def test_history(self):
        """ check that history is iterable and is empty """
        _att = "history"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _0 = getattr(self.o, _att)()
        # iterable
        self.assertTrue(hasattr(_0, '__len__'),
                        "'{}' is not iterable".format(_att))
        # no val in it
        _1 = 0
        for k,v in _0: _1 += v
        self.assertEqual(_1, 0,
                         "'{}' is not of length 0 or "
                         "has values different from 0".format(_att))
        
    def test_reset(self):
        """ check that reset clear count, memory_size, memory, history """
        _att = "reset"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        _latt = "count memory_size memory history"
        _required = all([att in data.subtests for att in _latt.split()])
        if not _required:
            self.skipTest("'{}' requires {}".format(_att, _latt))
            
        _0 = getattr(self.o, _att)()
        # reset() has no return
        self.assertEqual(type(_0), type(None),
                         "return of '{}()' is {} expecting {}"
                         "".format(_att, type(_0), type(None)))
        # count = 0, memory_size = 0, memory = '', history() is clean
        for att in _latt.split():
            if att == "history": self.test_history()
            elif att == "memory":
                self.assertEqual(getattr(self.o, att), "",
                                 "'{}' is '{}' expecting '{}'"
                                 "".format(att, getattr(self.o, att), ""))
            else: self.assertEqual(getattr(self.o, att), 0,
                                   "'{}' is {} expecting {}"
                                   "".format(att, getattr(self.o, att), 0))
    @unittest.expectedFailure
    def test_next_action(self):
        """ check that next_action exist and is not available """
        _att = 'next_action'
        if _att not in data.subtests:
            self.skipTest(f"'{_att}' not properly set\n{data.subtests}")
        self.o = self.K()
        chk.check_attr(self.o, _att)
        self.o.next_action()
    
class TestMethods1(unittest.TestCase):
    """ methods with one parameter """
    def setUp(self):
        self.K = getattr(tp, "Strategy")
        self.o = self.K()

    def subtest_action(self, att:str, rewards:str, expect:str):
        """ test actions for different rewards """
        for r in rewards:
            with self.subTest(reward=r):
                _0 = getattr(self.o, att)(r)
                self.assertTrue(_0 in expect,
                                "{}({}) is {} not in '{}'"
                                "".format(att, r, _0, expect))
    def test_success_my(self):
        """ test success for my_action(reward) """
        _att = "my_action"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        self.subtest_action(_att, "TRPS", "CD")

    def test_failure_my(self):
        """ test failure for my_action(reward) """
        _att = "my_action"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        self.subtest_action(_att, "pAX", "")
        

    def test_success_adv(self):
        """ test success for adv_action(reward) """
        _att = "adv_action"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        self.subtest_action(_att, "TRPS", "CD")
        
    def test_failure_adv(self):
        """ test failure for adv_action(reward) """
        _att = "my_action"
        if _att not in data.subtests:
            self.skipTest("'{}' not properly set".format(_att))
        self.subtest_action(_att, "tAX", "")

def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestDefault, TestAttributes, TestMethods0, TestMethods1)
    
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

