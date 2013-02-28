# -*- coding: utf-8 -*-

'''
Created on 2013/02/27

@author: user
'''

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
)

import unittest
import sys
import re
import argparse
from datetime import datetime

from inx import INXParser
from fdt import FDTParser, FDTParserVisitor


class FDTParserVisitorDetailFormatter(FDTParserVisitor):
    def __init__(self, path):
        import csv
        self._writer = csv.writer(open(path, "wb"), quoting=csv.QUOTE_ALL)
        self._total = 0
        self._row = 0
        self._last_time = datetime.now() 
    
    def print_detail(self):
        now = datetime.now()
        if 1 < (now - self._last_time).total_seconds():
            print "%s / %s" % (self._total, self._total - self._row)
            self._last_time = now
    
    def _write(self, row):
        self._row += 1
        self.print_detail()
        self._writer.writerow([text.encode("utf-8") for text in row])
        
    def example(self, example):
        self._total += 1
        self._write([example.main_id, example.sub_id, example.heading, ""])
        
    def document(self, document):
        self._total += 1
        self._write([document.main_id, document.sub_id, document.heading, document.body])


class FDTParserVisitorAnkiFormatter(FDTParserVisitorDetailFormatter):
    def __init__(self, path):
        super(FDTParserVisitorAnkiFormatter, self).__init__(path)
    
    def example(self, example):
        pass
        
    def document(self, document):
        self._total += 1
        
        #エイリアス的な見出しはスキップする
        body = re.sub(ur"▲▲(.+)?/(\d{11})△△", "", document.body)
        if len(body) < 10:
            logging.debug("skipped: %s", document)
            return
        
        #▲▲{text}/{main_id}△△  -> {text} 
        body = re.sub(ur"▲▲(.+)?/(\d{11})△△", ur"\1", document.body)
        #<CR> -> <BR /><BR />
        body = re.sub(ur"<CR>", "<BR /><BR />", body)
        
        #"{text} | " -> {text} 
        heading = re.sub(ur" \| $", "", document.heading)
        
        self._write([heading, body])
        

def get_arg():
    parser = argparse.ArgumentParser(prog="inx2csv.exe",
                                     description="inx to csv converter")
    parser.add_argument("--mode", default="all", choices=["all", "anki"])
    parser.add_argument("input")
    parser.add_argument("output")
    return parser.parse_args()

def main():
    arg = get_arg()
        
    print ""
    print "input path: %s" % arg.input
    print "output path: %s" % arg.output
    print "mode: %s" % arg.mode
    print ""

    result = INXParser().parse(arg.input)
    for entry in result.entries:
        if entry.name.endswith(".fdt"):
            print "found %s in %s" % (entry.name, arg.input)
            print "converting fdt to csv ..."
            print "total / skipped"
            if arg.mode == "all":
                visitor = FDTParserVisitorDetailFormatter(arg.output)
            elif arg.mode == "anki":
                visitor = FDTParserVisitorAnkiFormatter(arg.output)
            parser = FDTParser()
            parser.accept(entry.get_content(), visitor)
            visitor.print_detail()
            print "done."
            return
    print "ERROR: fdt file was not found"
    

class TestMain(unittest.TestCase):
    def test_main(self):
        sys.argv = ["", "--mode", "anki", "dicts/U_029/_ozh.inx", "test/_ozh.csv"]
        main()
        
        sys.argv = ["", "dicts/U_029/_ozh.inx", "test/_ozh.csv"]
        main()
        

if __name__ == "__main__":
    main()