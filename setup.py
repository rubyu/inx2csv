
# -*- coding: utf-8 -*-
#
# setup.py

'''
Created on 2013/02/28

@author: user
'''

from distutils.core import setup
import py2exe

setup(data_files=["readme.txt",
                  ("sources", ["unpack.py", 
                               "fdt.py", 
                               "inx.py", 
                               "inx2csv.py", 
                               "setup.py"])],
      console=['inx2csv.py'])