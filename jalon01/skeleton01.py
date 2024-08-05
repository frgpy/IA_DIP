#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from tools.base import Strategy
from tools.model import Model, m1, m2

#============= Quelques classes de stratégies classiques =============#
# Les classes héritent toutes de la classe Strategy
# exple d'héritage: sample.py
#=====================================================================#
    
# mettez ici les codes de vos classes après avoir changer le nom de ce
# fichier sinon il sera écrasé lors de la prochaine mise à jour

if __name__ == "__main__":
    from tools.evaluations import evaluation, multi_eval, tournament
    from tools.ezCLI import testcode
    code = """    
a = Strategy(1, 2, m1)
a.memory
a.memory_limit == 2
a.memory_size == 0
a.actions == m1.actions
a.style

a = Strategy(-1, 1, m2)
a.memory
a.memory_limit == 1
a.memory_size == 0
a.actions 
a.style

a = Strategy(0, -13) # ne pas mettre de modele revient à utiliser m1
a.memory
a.memory_limit == -1
a.memory_size == 0
a.actions == m1.actions
a.style

x = Strategy(0) # la mémoire est de taille 0, le modèle est m1
x.memory
x.memory_limit
x.memory_size
x.actions
x.style

y = Strategy(-1) # le style est méchant
y.memory
y.memory_limit
y.memory_size
y.actions
y.style

z = Strategy() # le style est gentil, 
z.memory
z.memory_limit
z.memory_size
z.actions
z.style

x.surname = 'Lunatique'
y.surname = 'Méchant'
z.surname = 'Gentil'
x.surname == 'Lunatique'
y.surname == 'Méchant'
z.surname == 'Gentil'
# this should fail as no next_action is defined
evaluation(y,z) == (m1.values['T'], m1.values['S'])

g = Gentle()
b = Bad()
f = Fool()
f.surname = 'Lunatique'
b.surname = 'Méchant'
g.surname = 'Gentil'
f.surname == 'Lunatique'
b.surname == 'Méchant'
g.surname == 'Gentil'
evaluation(b,g) == (m1.values['T'], m1.values['S'])

print(f"{g.idnum=}, {b.idnum=}, {f.idnum=}")
multi_eval(g, [b, f])

print(f"{g.idnum=}, {b.idnum=}, {f.idnum=}")
tournament([g,b,f])
""" ; testcode(code)
