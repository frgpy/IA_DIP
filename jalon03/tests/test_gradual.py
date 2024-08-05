#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "30.01.24"
__usage__ = "Project 2024: tests Jalon02 Gradual"
__update__ = "30.01.24 23:40"

import os
import unittest
from tests.tools import checkTools as chk
from tools.model import m1, m4

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
   self.defaults dictionnary "att" default_value
   self.methods dictionnary "method" (args, type)
"""

class TestGradual(unittest.TestCase):
    def setUp(self):
        self.kname = "Gradual"
        chk.check_class(tp, self.kname)
        self.K = getattr(tp, self.kname)

        self.defaults = {"idnum": 42,
                        "memory_size": 0,
                        "memory": '',
                        "count": 0,
                        "color": 42,
                        "name" : "Strat_042",
                        "surname": "Strat_042",
                        "state": 0,
                         "duplicity": 0,
                         "time_left": 0,}
        
        # required mode:bool, cool:int, rate:int
        # optional abort:int=0, model:Model=m1
        self.args = ( (False, -1, -1),
                      (True, -1, -1),
                      (False, 2, 3),
                      (True, 3, 2),
                      (False, 2, 2, 2),
                      (False, 2, 2, 3, m4), )
        self.context = ({'additive': False,
                         'cooling': 1,
                         'rate': 1,
                         'abort': 0,
                         'actions': m1.actions},
                        {'additive': True,
                         'cooling': 1,
                         'rate': 1,
                         'abort': 0,
                         'actions': m1.actions},
                        {'additive': False,
                         'cooling': 2,
                         'rate': 3,
                         'abort': 0,
                         'actions': m1.actions},
                        {'additive': True,
                         'cooling': 3,
                         'rate': 2,
                         'abort': 0,
                         'actions': m1.actions},
                        {'additive': False,
                         'cooling': 2,
                         'rate': 2,
                         'abort': 2,
                         'actions': m1.actions},
                        {'additive': False,
                         'cooling': 2,
                         'rate': 2,
                         'abort': 3,
                         'actions': m4.actions})
        for c in self.context:
            c.update({'style': 'C', 'memory_limit': 1, })
        self.ro_att = "state abort duplicity additive rate cooling time_left"
        self.ro_att = self.ro_att.split()
        self.required_meth = "make_prediction reset next_action".split()
        
    def test_klass(self):
        """ test if subclass of Strategy """
        self.assertTrue(issubclass(self.K, getattr(tp,"Strategy")),
                        "{0.kname} is not a subclass of Strategy"
                        "".format(self))
    def subtest_def(self, idx:int, do_test:bool=True):
        """ basic default values """
        for k,v in self.context[idx].items():
            if k == "actions": continue
            self.defaults[k] = v
        if do_test: chk.sub_default(self)

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

    def test_prediction_memory(self):
        """ what is in memory has nothing to do with prediction """
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                self.subtest_def(i, False)
                for r in "TSRP":
                    self.o.get_reward(r)
                    self.assertEqual(self.o.memory, r,
                                     "wrong memory")
                    _0 = self.o.make_prediction()
                    self.assertEqual(_0, 'C', "prediction should be 'C'")
                # same but this time action is performed
                for r in "TSRP":
                    self.o.get_reward(r)
                    self.assertEqual(self.o.memory, r,
                                     "wrong memory")
                    _0 = self.o.next_action()
                    _1 = self.o.time_left
                    _2 = self.o.make_prediction()
                    if _1 == 0:
                        self.assertTrue(_2=='C',
                                        f"expected prediction 'C' found {_2}")
                    else:
                        self.assertTrue(len(_2) == _1,
                                        f"expecting a prediction of size {_1}"
                                        f" got {_2}")
    def test_forbidden(self):
        """ parse the internal dictionnary for forbidden values """
        _keys = self.K.__dict__.keys()
        _authorized = self.ro_att[:]
        _authorized.append('ID')
        _authorized.extend(self.required_meth)

        for key in _keys:
            if key.startswith('__'): continue
            if key.startswith('_Strategy__'): continue
            if key.startswith('_Gradual__'): continue
            with self.subTest(att=key):
                self.assertTrue(key in _authorized,
                                f"{key} is not authorized")

    def test_ro_att(self):
        """ test ro of each required attribute """
        self.K.ID = 42
        self.o = self.K(* self.args[-1])
        for att in self.ro_att:
            chk.guard_ro(self, att)

    def test_first_action_validity(self):
        """ check that 1st action is always C """
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                self.subtest_def(i)
                _0 = self.o.next_action()
                self.assertTrue(_0 == 'C',
                                f"unexpected {_0}")
    def test_CDD(self):
        """ rewards are preset to RSP """
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                self.subtest_def(i)
                self.o.get_reward('R') # all play 'C'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.time_left, self.o.state
                self.assertTrue(_0 == "C",
                                f"unexpected {_0} 1st action")
                self.assertTrue(all([x==0 for x in _bag]),
                                    f"unexpected {_bag}")
                self.o.get_reward('S') # adv plays 'D'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.state
                self.assertTrue(_0 == "D",
                                f"unexpected {_0} 2nd action")
                self.assertTrue((1, -1) == _bag,
                                    f"unexpected {_bag} state should be -1")
                if self.o.additive:
                    _1 = 1+self.o.rate + self.o.cooling
                else:
                    _1 = self.o.rate + self.o.cooling
                self.assertEqual(self.o.time_left, _1 -1,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {_1 -1}")
                chk.guard_meth(self, 'make_prediction')
                _act = self.o.make_prediction()
                self.assertEqual(len(_act), _1 -1,
                                 f"bad prediction len found {len(_act)}"
                                 f" expecting {_1 -1}")
                self.assertTrue(_act.endswith('C'*self.o.cooling),
                                f"bad todo {_act}")
                self.o.get_reward('P') # adv plays 'D'
                # times to check blind mode due to mode
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.state
                if self.o.rate == 1 and not self.o.additive:
                    self.assertTrue(_0 == "C",
                                    f"unexpected {_0} 3rd action")
                    self.assertTrue((1, 1) == _bag,
                                    f"unexpected {_bag} state should be 1")
                    self.assertEqual(self.o.time_left, self.o.cooling -1,
                                         f"Bad clock found {self.o.time_left}"
                                         f" expecting {self.o.cooling -1}")

                else:
                    
                    self.assertTrue(_0 == "D",
                                    f"unexpected {_0} 3rd action")
                    self.assertTrue((2, -1) == _bag,
                                    f"unexpected {_bag} state should be -1")
                    if self.o.additive:
                        _1 = 2+self.o.rate + self.o.cooling
                    else:
                        _1 = 2*self.o.rate + self.o.cooling
                        self.assertEqual(self.o.time_left, _1 -1,
                                         f"Bad clock found {self.o.time_left}"
                                         f" expecting {_1 -1}")
                
    def test_DCD(self):
        ''' rewards are preset to ST? '''
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                self.subtest_def(i)
                self.o.get_reward('S') # adv plays 'D'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.state
                self.assertTrue(_0 == "D",
                                f"unexpected {_0} 1st action")
                self.assertEqual((1, -1), _bag,
                                    f"unexpected {_bag}")
                if self.o.additive:
                    _D = self.o.duplicity + self.o.rate
                else:
                    _D = self.o.duplicity * self.o.rate

                _1 = _D + self.o.cooling

                self.assertEqual(self.o.time_left, _1 -1,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {_1 -1}")
                chk.guard_meth(self, 'make_prediction')
                _act = self.o.make_prediction()
                self.assertEqual(len(_act), _1 -1,
                                 f"bad prediction len found {len(_act)}"
                                 f" expecting {_1 -1}")
                self.assertTrue(_act.endswith('C'*self.o.cooling),
                                f"bad todo {_act}")
                self.o.get_reward('T') # adv played 'C'
                # times to check blind mode due to mode
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.state
                if self.o.rate == 1 and not self.o.additive:
                    self.assertTrue(_0 == "C",
                                    f"unexpected {_0} 2nd action")
                    self.assertTrue((1, 1) == _bag,
                                f"unexpected {_bag} state should be 1")
                    self.assertEqual(self.o.time_left, self.o.cooling -1,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {self.o.cooling -1}")
                    _last = 'C'
                else:
                    self.assertTrue(_0 == "D",
                                    f"unexpected {_0} 2nd action")
                    self.assertTrue((1, -1) == _bag,
                                f"unexpected {_bag} state should be -1")

                    self.assertEqual(self.o.time_left, _1 -2,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {_1 -2}")
                    _last = 'D'

                #3rd step he betrays
                _rew = 'S' if _last == 'C' else 'P'
                self.o.get_reward(_rew)
                # are we in blind mode or not ... check _D wrt 2 defects
                _seen = (self.o.time_left == 0) or (_D > 2)
                _0 = self.o.next_action()
                if _seen:
                    self.assertEqual(_0, 'D',
                                     f"expecting 'D' found '{_0}' "
                                     f"as 3rd action")
                    _1 = self.o.duplicity
                    self.assertEqual(_1, 2,
                                     f"Adversary action seen")
                    if self.o.additive:
                        _1 = _1+self.o.rate + self.o.cooling
                    else:
                        _1 = _1*self.o.rate + self.o.cooling
                    self.assertEqual(self.o.time_left, _1 -1,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {_1 -1}")
                    chk.guard_meth(self, 'make_prediction')
                    _act = self.o.make_prediction()
                    self.assertEqual(len(_act), _1 -1,
                                 f"bad prediction len found {len(_act)}"
                                 f" expecting {_1 -1}")
                    self.assertTrue(_act.endswith('C'*self.o.cooling),
                                    f"bad todo {_act}")

                else:
                    self.assertEqual(_0, 'C',
                                     f"expecting 'C' found '{_0}' "
                                     f"as 3rd action")
                    #'coz we were blind
                    _1 = self.o.duplicity
                    self.assertEqual(_1, 1,
                                     f"Adversary action not seen")

    def test_CD_reset_CD(self):
        """ rewards are preset to RS reset RS """
        for i,args in enumerate(self.args):
            self.K.ID = 42
            self.o = self.K(*args)
            with self.subTest(arg=args):
                self.subtest_def(i)
                self.o.get_reward('R') # all play 'C'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.time_left, self.o.state
                self.assertTrue(_0 == "C",
                                f"unexpected {_0} 1st action")
                self.assertTrue(all([x==0 for x in _bag]),
                                    f"unexpected {_bag}")
                self.o.get_reward('S') # adv plays 'D'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.state
                self.assertTrue(_0 == "D",
                                f"unexpected {_0} 2nd action")
                self.assertTrue((1, -1) == _bag,
                                    f"unexpected {_bag} state should be -1")
                if self.o.additive:
                    _1 = 1+self.o.rate + self.o.cooling
                else:
                    _1 = self.o.rate + self.o.cooling
                self.assertEqual(self.o.time_left, _1 -1,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {_1 -1}")
                chk.guard_meth(self, 'make_prediction')
                _act = self.o.make_prediction()
                self.assertEqual(len(_act), _1 -1,
                                 f"bad prediction len found {len(_act)}"
                                 f" expecting {_1 -1}")
                self.assertTrue(_act.endswith('C'*self.o.cooling),
                                f"bad todo {_act}")
                self.o.get_reward('P') # adv plays 'D'
                # reset
                self.assertTrue(self.o.time_left > 0,
                                "expect clock not at zero")
                self.o.reset()
                self.subtest_def(i) # verify default values
                # CD
                self.o.get_reward('R') # all play 'C'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.time_left, self.o.state
                self.assertTrue(_0 == "C",
                                f"unexpected {_0} 1st action")
                self.assertTrue(all([x==0 for x in _bag]),
                                    f"unexpected {_bag}")
                self.o.get_reward('S') # adv plays 'D'
                _0 = self.o.next_action()
                _bag = self.o.duplicity, self.o.state
                self.assertTrue(_0 == "D",
                                f"unexpected {_0} 2nd action")
                self.assertTrue((1, -1) == _bag,
                                    f"unexpected {_bag} state should be -1")
                if self.o.additive:
                    _1 = 1+self.o.rate + self.o.cooling
                else:
                    _1 = self.o.rate + self.o.cooling
                self.assertEqual(self.o.time_left, _1 -1,
                                 f"Bad clock found {self.o.time_left}"
                                 f" expecting {_1 -1}")
                chk.guard_meth(self, 'make_prediction')
                _act = self.o.make_prediction()
                self.assertEqual(len(_act), _1 -1,
                                 f"bad prediction len found {len(_act)}"
                                 f" expecting {_1 -1}")
                self.assertTrue(_act.endswith('C'*self.o.cooling),
                                f"bad todo {_act}")

    def test_abort_possible(self):
        """ duplicity is strong enough to abort=3 """
        self.K.ID = 42
        self.o = self.K(*self.args[-1])
        self.subtest_def(-1, False)
        self.o.get_reward('S') # 1st Defection
        _1 = self.o.next_action()
        _2 = self.o.duplicity
        self.assertEqual(_1, 'D', f"wrong reaction {_1}")
        self.assertEqual(_2, 1, f"wrong duplicity {_2}")
        self.o.get_reward('P') # 2nd Defection
        _1 = self.o.next_action()
        _2 = self.o.duplicity
        self.assertEqual(_1, 'D', f"wrong reaction {_1}")
        self.assertEqual(_2, 2, f"wrong duplicity {_2}")
        self.o.get_reward('P') # 3rd Defection
        _1 = self.o.next_action()
        _2 = self.o.duplicity
        self.assertEqual(_1, 'R', f"wrong reaction {_1}")
        self.assertEqual(_2, 3, f"wrong duplicity {_2}")

    def test_abort_impossible(self):
        """ duplicity is strong enough to abort but actions do not allow it """
        self.K.ID = 42
        self.o = self.K(*self.args[-2])
        self.subtest_def(-2, False)
        self.o.get_reward('S') # 1st Defection
        _1 = self.o.next_action()
        _2 = self.o.duplicity
        self.assertEqual(_1, 'D', f"wrong reaction {_1}")
        self.assertEqual(_2, 1, f"wrong duplicity {_2}")
        self.o.get_reward('P') # 2nd Defection
        _1 = self.o.next_action()
        _2 = self.o.duplicity
        self.assertEqual(_1, 'D', f"wrong reaction {_1}")
        self.assertEqual(_2, 2, f"wrong duplicity {_2}")
        self.o.get_reward('P') # 3rd Defection
        _1 = self.o.next_action()
        _2 = self.o.duplicity
        self.assertEqual(_1, 'D', f"wrong reaction {_1}")
        self.assertEqual(_2, 3, f"wrong duplicity {_2}")


    def test_prediction_no_abort(self):
        """ if model denies it then dont predict an 'R' """
        self.K.ID = 42
        self.o = self.K(*self.args[-2])
        chk.guard_meth(self, 'make_prediction')
        self.subtest_def(-2, False)
        self.o.get_reward('S') # 1st Defection
        _1 = self.o.next_action()
        self.o.get_reward('P') # 2nd Defection
        _2 = self.o.next_action()
        self.assertEqual(_1, _2, "should be 'D'")
        self.o.get_reward('P') # 3rd Defection
        _3 = self.o.next_action()
        _4 = self.o.make_prediction()
        self.assertEqual(_3, "D", "should be 'D'")
        if self.o.additive: _D = self.o.duplicity + self.o.rate -1
        else: _D = self.o.duplicity * self.o.rate -1
        self.assertTrue(_4.startswith('D'*_D), "wrong prediction")

    def test_prediction_aborting(self):
        """ if model allows it then predict an 'R' """
        self.K.ID = 42
        self.o = self.K(*self.args[-1])
        chk.guard_meth(self, 'make_prediction')
        self.subtest_def(-2, False)
        self.o.get_reward('S') # 1st Defection
        _1 = self.o.next_action()
        self.o.get_reward('P') # 2nd Defection
        _2 = self.o.next_action()
        self.assertEqual(_1, _2, "should be 'D'")
        self.o.get_reward('P') # 3rd Defection
        _3 = self.o.next_action()
        _4 = self.o.make_prediction()
        self.assertEqual(_3, _4, "should be 'R'")
        
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestGradual,)
    
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
