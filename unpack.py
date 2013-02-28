# -*- coding: utf-8 -*-

'''
Created on 2013/02/27

@author: user
'''

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
)

import struct

def int_to_hex(i):
    return ("0" + hex(i)[2:].upper())[-2:]

def str_to_int(c):
    b = struct.unpack("B", c)
    if 1 != len(b):
        raise ValueError()
    return b[0]

def big_endian_bytes_to_int(t):
    arr = [int_to_hex(str_to_int(c)) for c in t]
    return int("".join(arr), 16)

def read_int(f, p, n):
    return big_endian_bytes_to_int(f[p:p+n])

def read_str(f, p, n):
    return f[p:p+n]

def find(f, p, *args):
    eof = len(f)
    length = len(args)
    logging.debug("query: %s", [hex(n) for n in args])
    if 0 == length:
        raise Exception()
    
    def match(l, t):
        for i in xrange(length):
            if l[i] != t[i]:
                return False
        return True
    
    buf = []
    while True:
        if p == eof:
            raise EOFError()
        if len(buf) == length:
            buf.pop(0)
        buf.append(read_int(f, p, 1))
        p = p + 1
        #logging.debug("buf: %s", [hex(n) for n in buf])
        if len(buf) == length and match(buf, args):
            return p - length
    