#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__usage__ = '''
Logger provides an alternative to standard output
>>> import sys
>>> sys.stdout = Logger(filename:str) # replace
>>> sys.stdout = Logger(filename:str, mode='a') # append
To redirect errors
>>> sys.sterr = Logger(filename:str, mode:char) 
To redirect both
>>> sys.stdout = sys.sterr = Logger(filename:str, mode:char) 
'''
import sys
 
class Logger:
    ''' duplicate std[out|err] to some file '''
    def __init__(self, filename:str='track.txt', mode:str='w'):
        """ error prone for mode """
        _mode = 'w' if mode not in ('w', 'a') else mode
        self.__console = sys.stdout
        self.__fd = open(filename, _mode)
 
    def write(self, message):
        self.__console.write(message)
        self.__fd.write(message)
 
    def flush(self):
        self.__console.flush()
        self.__fd.flush()
 
if __name__ == '__main__': print(__usage__)
