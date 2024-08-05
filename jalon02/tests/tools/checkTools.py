#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "27.01.20"
__usage__ = "some check_XXX Tools"
__update__ = "27.01.20 06:04"


#-------------- import ----------------------#
import sys
import os
import copy
import unittest
#============================================#

class Data:
    """ simple storage """
    __slots__ = tuple("yes no report subtests".split())
    def __init__(self):
        self.yes = 0
        self.no = 0
        self.report = {}
        self.subtests = set()

    @property
    def total(self) -> int: return self.yes + self.no
    @property
    def ratio(self) -> float:
        return round(self.yes / self.total, 3)
    def __str__(self) -> str:
        _str = "\n{}\n".format("_"*17)
        for (k, v) in self.report.items():
            _str += ">>> '{}' : {}\n".format(k, v)
        _str += "{0.yes} success / {0.total} tests\n".format(self)
        return _str
        
def check_property(prop:bool, msg:str='property is False',
                   letter:str='E') -> str:
    """ 
        check if some property is True

        :param bolean prop: property to verify
        :param str msg: message if failure
        :param char letter: the char if failure
        :return: letter or '.'
        :rtype: char

    """
    try:
        assert( prop ), '>>> failure: {}'.format(msg)
        _ = '.'
    except Exception as _e:
        if sys.version_info[:2] >= (3, 3): print(_e, flush=True)
        else: print(_e)
        _ = letter
        
    return _

def has_failure(string:str, sz:int=1) -> bool:
    """ check if there are failures in the  last sz tests """
    sz = min(len(string), sz)
    return string[-sz:] != '.'*sz
    

def check_attr(obj, att:str):
    """ check if att is missing for a given obj """
    if not hasattr(obj, att):
        raise unittest.SkipTest("{} missing for {}"
                                "".format(att, obj.__class__.__name__))

def check_ro(obj, latt, verbose=False) -> tuple:
    """ 
        check if any of the iterable :latt: of attributes 
        are read-only
    """
    _missing = []
    _rw = []
    latt = latt.split() if isinstance(latt, str) else latt
    for att in latt:
        if verbose: print(att, 'processing ...', flush=True)
        if not hasattr(obj, att):
            _missing.append(att) ; continue
        else:
            _old = copy.deepcopy(getattr(obj, att))

        if hasattr(_old, '__iter__'):
            _x = 'mmc' if 'mmc' not in _old else 'capharnaumadlib'
        else: _x = 'mmc' if _old != 'mmc' else 42
        try:
            setattr(obj, att, _x)
            if getattr(obj, att) == _x:
                _rw.append(att) ; setattr(obj, att, _old) ; continue
        except:
            pass
        
        if hasattr(_old, '__len__'):
            _szold = len(_old)
            if isinstance(_old, list):
                try:
                    _old.append(_x)
                    if len(getattr(obj, att)) > _szold:
                        _rw.append(att) ; setattr(obj, att, _old[:-1])
                except: pass
            elif isinstance(_old, str):
                _old+str(_x)
                if len(getattr(obj, att)) > _szold:
                    _rw.append(att) ; setattr(obj, att, _old[:-len(str(_x))])
            elif isinstance(_old, set):
                try:
                    _old.add(_x)
                    if len(getattr(obj, att)) > _szold:
                        _rw.append(att) ; _old.discard(_x)
                except: pass
            elif isinstance(_old, dict):
                _old[_x] = _x
                if verbose: print('>>> ', _old.get(_x))
                _y = getattr(obj, att).get(_x, None)
                if (len(getattr(obj, att)) > _szold or
                     _y == _x) :
                    _rw.append(att)
                    del getattr(obj, att)[_x]

    return _missing, _rw

def check_flush():
    """ check python print flush """
    _ = sys.version_info
    return False if _[0] == 2 else (False if _[0] == 3 and _[1] < 4 else True)

def check_class(module, klass:str):
    """ check if a specific class is missing in a given module """
    if not hasattr(module, klass):
        raise unittest.SkipTest("{} not found in module {}"
                                "".format(klass, module.__name__))
def check_module(module, things):
    """ check if any specific things is missing in a given module """

    return [thing for thing in things.split()
            if not hasattr(module, thing)]

#============= on the fly methods ====================#
def guard_meth(self, att, args=None):
    """
        require hasattr(self, 'o')

        ensure we could keep on safely or skip it
    """
    try:
        if not hasattr(self.o, att):
            self.skipTest("'{}' is missing".format(att))
        _0 = (getattr(self.o,att)() if args is None
              else getattr(self.o, att)(*args))
        return True
    except Exception as _e:
        
        self.skipTest(f"{_e}: {att}{() if args is None else args} failed")
        return False

def guard_att(self, att):
    """
        require hasattr(self, 'o')

        ensure we could keep on safely or skip it
    """
    try:
        if not hasattr(self.o, att):
            self.skipTest("'{}' is missing".format(att))
        _0 = getattr(self.o,att)
        return True
    except:
        self.skipTest("'{}' failure".format(att))
        return False

def guard_ro(self, att):
    """
        require hasattr(self, 'o')

        ensure we could keep on safely or skip it
    """
    if guard_att(self, att):
        if sys.version_info.minor <11:
            with self.assertRaisesRegex(AttributeError, "can't set att.*"):
                setattr(self.o, att, 'mmc')
        else:
            with self.assertRaisesRegex(AttributeError,
                                        "property .* has no setter"):
                setattr(self.o, att, 'mmc')
                
        with self.assertRaisesRegex(TypeError, ".*not support item assignment"):
            getattr(self.o, att)[0] = 42
    
def sub_default(self):
    """ 
        require hasattr(self, "defaults")
        require isinstance(self.default, dict)
        require hasattr(self, 'K') # class
        require hasattr(self, 'o') # instance of K
    
        verify that each attribute has default values
    """
    if check_flush():
        print('\n>>>', self.K.__name__, 'default', end='> ', flush=True)
    else:
        print('\n>>>', self.K.__name__, 'default', end='> ')
        
    for k,v in self.defaults.items():
        if not guard_att(self, k): continue
        _0 = getattr(self.o, k)
        self.assertTrue(_0 == v,
                        "'{}' found {} expecting {}".format(k,_0,v))

def sub_signature(self):
    """ 
        require hasattr(self, methods)
        require isinstance(self.methods, dict)
        require hasattr(self, 'K') # class
        require hasattr(self, 'o') # instance of K
       
        verify signature for each method
    """
    if check_flush():
        print('\n>>>', self.K.__name__, 'signature', end='> ', flush=True)
    else:
        print('\n>>>', self.K.__name__, 'signature', end='> ')
        
    for x in self.methods:
        with self.subTest(meth=x):
            _args, _typ = self.methods[x]
            if not guard_meth(self, x, _args): continue
            if _args is None:
                _0 = getattr(self.o, x)()
            else:
                _0 = getattr(self.o, x)(*_args)
            self.assertTrue(isinstance(_0, _typ),
                            "{} expected {}".format(x, _typ))

#========== class Bidon pour contrôler les outils ============#            
class Bidon:
    __slots__ = ('x', 'y', 'z', 't')
    def __init__(self, x=42):
        self.x = x
        self.y = [3]
        self.z = set([5])
        self.t = {'mmc': 42}

    @property
    def u(self): return frozenset(self.z)
    @property
    def v(self): return self.y[:]
    @property
    def w(self): return tuple(self.y)
    @property
    def a(self): return self.t.copy()
        
        
if __name__ == "__main__":
    print(check_property(Bidon().x == 42,
                         "pb with default parameter of Bidon", "X"))
    print(check_property(hasattr(Bidon(), 'b'),
                         "'Bidon' objects have no 'b' attribute,"
                         " result was expected"))
    print(check_ro(Bidon(), "x y z t u v w a".split(), True))
