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

import unittest
from unpack import read_int, read_str


class INXEntry(object):
    def __init__(self, result, name, content_start):
        self._result = result
        self.name = name
        self.content_start = content_start

    def get_content(self):
        return self._result.get_content(self) 


class INXParseResult(object):
    def __init__(self, buf):
        self._buf = buf
        self.entries = []
        
    def append(self, entry):
        self.entries.append(entry)

    def get_content(self, entry):
        logging.debug("extract content of %s", entry.name)
        pos = self.entries.index(entry)
        if pos == len(self.entries) - 1:
            content_end = len(self._buf)
        else:
            content_end = self.entries[pos+1].content_start - 1
        logging.debug("copying %s to %s of buffer", hex(entry.content_start), hex(content_end))
        return self._buf[entry.content_start:content_end]
    

class INXParser(object):
    """
    Address Length  Type        Memo               
    0x00    1       :entries
    0x01    8       :entry 1    :adress
    0x0A    1       :entry 1    :length of name    :A
    0x0B    [A]     :entry 1    :name
    ...
    """
    def _set_pos(self, n):
        self._pos = n
        logging.debug("position moved to %s", hex(self._pos))
        
    def _add_pos(self, n):
        self._pos += n
        logging.debug("position moved to %s", hex(self._pos))
    
    def parse(self, path):
        buf = open(path, "rb").read()
        eof = len(buf)
        logging.debug("path: %s", path)
        logging.debug("parsing INX of %s(%s) bytes", eof, hex(eof))
        self._set_pos(0)
        
        num_entries = read_int(buf, self._pos, 1)
        logging.debug("number of entries: %s", num_entries)
        self._add_pos(1)
        
        result = INXParseResult(buf)
        for i in xrange(num_entries):
            logging.debug("entry %s of %s", i+1, num_entries)
            
            content_start = read_int(buf, self._pos, 8)
            logging.debug("content_start: %s (%s)", content_start, hex(content_start))
            self._add_pos(8)
            
            name_length = read_int(buf, self._pos, 1)
            logging.debug("name_length: %s", name_length)
            self._add_pos(1)
            
            name = read_str(buf, self._pos, name_length)
            logging.debug("name: %s", name)
            self._add_pos(name_length)
            
            result.append(INXEntry(result, name, content_start))
        return result
    

class TestINXParser(unittest.TestCase):
    def test_parse_header(self):
        result = INXParser().parse("dicts\U_029\_ozh.inx")
        for entry in result.entries:
            temp = open("test/" + entry.name, "wb")
            temp.write(entry.get_content())
            temp.close()



            
            