#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "24.01.19"
__usage__ = "Test loader pour le projet 2023/2024"
__update__ = "30.01.24 18:35"

import os
import sys
import unittest
from tests.tools.checkTools import *
from tools.logger import Logger


#===== tests import, will grow ==========#
try:
    from tests import test_base_jalon01
except:
    print("failed test_base")
    pass
try:
    from tests import test_strategies_jalon01
except:
    print("failed test_strategies")
    pass
################# J02 ##################
try:
    from tests import test_periodic
except:
    print("failed test_periodic")
    pass
try:
    from tests import test_majority
except:
    print("failed test_majorite")
    pass
try:
    from tests import test_gradual
except:
    print("failed test_gradual")
    pass
try:
    from tests import test_markov
except:
    print("failed test_markov")
    pass
try:
    from tests import test_stochastic
except:
    print("failed test_stochastic")
    pass
################# J03 ##################
try:
    from tests import test_automaton
except:
    print("failed test_automaton")
    pass
try:
    from tests import test_mime
except:
    print("failed test_mime")
    pass
try:
    from tests import test_motif
except:
    print("failed test_motif")
    pass
try:
    from tests import test_shannon
except:
    print("failed test_shannon")
    pass
#========================================#

#================================ unittest area ========================#
def suite_me(fname, toTest):
    if not hasattr(toTest, '__iter__'): raise TypeError("go to Hell !")
    print("Vous avez {} série(s) à passer".format(len(toTest)))
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    suite = unittest.TestSuite()
    for test_me in toTest:
        try:
            suite.addTest(test_me.suite(fname))
        except Exception as _e:
            print(_e)
            
    return suite

if __name__ == '__main__':
    if len(sys.argv) == 1:
        param = input("quel est le fichier à traiter ? ")
        if not os.path.isfile(param): ValueError("need a python file")
    else: param = sys.argv[1]

    m = 'w' if len(sys.argv) != 3 else sys.argv[2]
    sys.stdout = sys.stderr = Logger('output.txt', m) # track screen's output

    etudiant = param.split('.')[0]

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    try:
        tp = __import__(etudiant) # revient à faire import XXX as tp
    except Exception as _e:
        print(_e)
        sys.exit(-1)

        
    _yes = "oO0Yy"
    _todo = []
    _submenu = { '1': ("Stategie tactiques_jalon01",
                       [test_base_jalon01, test_strategies_jalon01]),
                '2': ("Periodique Majorite Markov Stochastique Gradual",
                      [test_periodic, test_majority, test_markov,
                       test_stochastic, test_gradual]),
                '3' : ("Automaton Mime Motif Shannon",
                       [test_automaton, test_mime, test_motif, test_shannon])
                       }
    _all = None
    print("select wich subtests you want")
    print("Pour répondre par oui, utiliser l'un des symboles '{}'"
          "".format(_yes))
    _choices = ['all']
    _choices.extend(sorted(_submenu.keys()))
    for key in _choices:
        _msg = ("Passer tous les tests ? " if key == "all"
                else "Tests du jalon 0{} ? ".format(key))
        if key == "all":
                _ = input(_msg)
                if len(_) >=1 and _[0] in _yes:
                    for k in _submenu: _todo.extend(_submenu[k][1])
                    break # sortie
        else:
            _ = input(_msg)
            if len(_) >=1 and _[0] in _yes:
                _names, _modules = _submenu[key]
                for n,x in zip(_names.split(), _modules):
                    _ = input(">>> Jalon 0{}: Test de {} ? ".format(key, n))
                    if len(_)==1 and _ in _yes:
                        _todo.append(x) ; print("{} added".format(n))
                
    unittest.TextTestRunner(verbosity=2).run(suite_me(etudiant, _todo))
