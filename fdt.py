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
from unpack import read_int, read_str, find

def read_utf8(f, p, n):
    length = 0
    eof = len(f)
    buf = ""
    while True:
        if p == eof:
            raise EOFError()
        buf += read_str(f, p, 1)
        p += 1
        length += 1
        if n <= length:
            try:
                text = unicode(buf, "utf-8")
                if len(text) == n:
                    return UTF8String(length, text) 
            except UnicodeDecodeError:
                pass

def read_vint(f, p):
    """
    Decodes variable-length format for position integers.
    http://lucene.apache.org/core/old_versioned_docs/versions/3_0_0/fileformats.html#VInt
    """
    eof = len(f)
    length = 0
    total = 0
    while True:
        if p == eof:
            raise EOFError()
        i = read_int(f, p, 1)
        has_remain = False
        if 0b10000000 <= i: #high-order bit is 1
            has_remain = True
            i = i ^ 0b10000000 #high-order bit to 0
        else:
            has_remain = False
        total = total | i << 7 * length #append low-order 7 bits to the result
        length += 1
        p += 1
        if not has_remain:
            break
    return VInt(length, total)


class LuceneFDTDataType(object):
    pass


class VInt(LuceneFDTDataType):
    def __init__(self, length, value):
        self.length = length
        self.value = value
        
    def __str__(self):
        return "VInt: length=%s, value=%s" % (self.length, self.value)
    
    def __int__(self):
        return self.value
        
    
class UTF8String(LuceneFDTDataType): 
    def __init__(self, length, value):
        self.length = length
        self.value = value
               
    def __str__(self):
        return "UTF8String: length=%s, value=%s" % (self.length, self.value)
    
    def __int__(self):
        return self.value


class FDTParser(object):
        
    def _set_pos(self, n):
        self._pos = n
        logging.debug("position moved to %s", hex(self._pos))
        
    def _add_pos(self, n):
        self._pos += n
        logging.debug("position moved to %s", hex(self._pos))
    
    def _read_vstr(self, buf):
        vint = read_vint(buf, self._pos)
        logging.debug(vint)
        self._add_pos(vint.length)
        
        vstr = read_utf8(buf, self._pos, vint.value)
        logging.debug(vstr)
        self._add_pos(vstr.length)
        return vstr
    
    def accept(self, buf, visitor):
        """
        [0x0B 0x09 0x00] ... 2 bytes ... 
            [main id: 11 byte] ... 3 bytes ... 
            [sub id: 3byte] ... ? ...
            [0x00 0x00 0x02 0x01]
                [VInt A] [VStr(heading): A.length] ... ? ... 
                [0x0B 0x00]
                [VInt B] [VSTr(body): B.length]
                ... 
            OR
            [0x00 0x00 0x03 0x01]
                [Vint C] [VStr(heading): A.length]
                ...
        """
        logging.debug("parsing FDT of %s(%s) bytes", len(buf), hex(len(buf)))
        self._set_pos(0)
        try:
            while True:
                i = find(buf, self._pos, 0x0B, 0x09, 0x00)
                logging.debug("[0x0B 0x09 0x00] found at %s", hex(i))
                self._set_pos(i)
                
                main_id = read_str(buf, self._pos+4, 11)
                sub_id = read_str(buf, self._pos+18, 3)
                logging.debug("main id: %s", main_id)
                logging.debug("sub id: %s", sub_id)
                
                if int(sub_id) == 0:
                    i = find(buf, self._pos, 0x00, 0x00, 0x02, 0x01)
                    logging.debug("[0x00 0x00 0x02 0x01] found at %s", hex(i))
                else:
                    i = find(buf, self._pos, 0x00, 0x00, 0x03, 0x01)
                    logging.debug("[0x00 0x00 0x03 0x01] found at %s", hex(i))
                self._set_pos(i+4)
                
                heading = self._read_vstr(buf)
                
                if int(sub_id) > 0:
                    visitor.example(FDTParserExample(main_id, sub_id, heading.value))
                    continue
                    
                i = find(buf, self._pos, 0x0B, 0x00)
                logging.debug("[0x0B 0x00 found] at %s", hex(i))
                 
                if i - self._pos > 5:
                    logging.warn("[0x0B 0x00](%s) found long after [0x00 0x00 0x02 0x01](%s)", 
                                 hex(i), hex(self._pos))
                
                self._set_pos(i+2)
                
                body = self._read_vstr(buf)
                
                visitor.document(FDTParserDocument(main_id, sub_id, heading.value, body.value))

        except EOFError:
            logging.debug("rearch EOF")
        logging.debug("parse finishied")


class TestFDTParser(unittest.TestCase):
    def test_parse_header(self):
        parser = FDTParser()
        visitor = FDTParserVisitorExample()
        parser.accept(open("test/_ozh.fdt", "rb").read(), visitor)
        visitor.show()
        
        
class FDTParserFragment(object):
    pass


class FDTParserExample(FDTParserFragment):
    def __init__(self, main_id, sub_id, heading):
        self.main_id = main_id
        self.sub_id = sub_id
        self.heading = heading

    def __str__(self):
        return "%s" % self.heading


class FDTParserDocument(FDTParserFragment):
    def __init__(self, main_id, sub_id, heading, body):
        self.main_id = main_id
        self.sub_id = sub_id
        self.heading = heading
        self.body = body

    def __str__(self):
        return u"%s %s" % (self.heading, self.body)
    

class FDTParserVisitor(object):
    def example(self, example):
        pass
    
    def document(self, document):
        pass


class FDTParserVisitorExample(FDTParserVisitor):
    def __init__(self):
        self.examples = 0
        self.documents = 0
        
    def example(self, example):
        logging.info(example)
        self.examples += 1
    
    def document(self, document):
        logging.info(document)
        self.documents += 1
        
    def show(self):
        logging.info("documents: %s, examples: %s, total: %s", 
                     self.documents, self.examples, self.documents+self.examples)
        

