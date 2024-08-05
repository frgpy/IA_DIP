#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class A:
     """ classe parente """
     def __init__(self, x:int):
         """ __local variable privée, valeur variable publique """
         self.__local = x-1
         self.valeur = x
         print(f"** je suis dans A et j'ai reçu {x=}")
     def __repr__(self) -> str:
         return ("** je suis défini dans A mais:"
                 f" je suis {self.__class__.__name__}"
                 f" avec {self.valeur=} & {self.__local=}")
     def methodA(self):
         print(f"** je suis défini dans A {self.__local=}")
     def methodB(self):
         print(f"** je suis défini aussi dans A {self.valeur=}")

class B(A):
    """ classe fille, redéfinit methodB ajoute methodC """
    def methodB(self):
        print(f"** je suis défini dans B {self.valeur=}")
    def methodC(self):
        ''' __local privée de A n'est pas accessible en B '''
        try: print(f"** je suis défini dans B {self.valeur=} & {self.__local=}")
        except Exception as _e: print(f"** dans B, on a un ennui : {_e}")
        print(f"** le vrai nom de __local est {self._A__local=}")

class C(A):
    """ classe fille, redéfinit methodB ajoute methodC """
    def __init__(self, a:int, b:int):
        ''' redéfinit constructeur en ajoutant une __local propre à elle '''
        super().__init__(a)
        self.__local = b
        print(f"** je suis dans C et j'ai reçu {a=} {b=}")
    def methodB(self):
        print(f"** je suis défini dans C {self.__local=}")
    def methodC(self):
        print(f"** je suis défini dans C {self.valeur=} & {self.__local=}")
        print(f"** le vrai nom de __local est {self._C__local=}"
              f" mais aussi {self._A__local=}")

if __name__ == '__main__':
     from tools.ezCLI import testcode
     code = '''
a = A(22)
a # utilise __repr__
a.methodA()
a.methodB()

b = B(13)
b # utilise __repr__
b.methodA() # methodA de la classe A
b.methodB() # methodB de la classe B
b.methodC() # methodC de la classe B voulant utiliser __local de A

c = C(17, 25)
c # utilise __repr__
c.methodA()
c.methodB()
c.methodC()
'''
     testcode(code)
