#!/usr/bin/env python3
############ This script prints out comma-separated spreadsheet(s) (report-language.csv) with the ratio of word order pairs in conllu files ########
import sys
import subprocess
import re
import pprint
import glob
import os
import random
import unicodedata
import collections
import csv
import string
import pyconll
import pyconll.util

try:
    import argparse
except ImportError:
    checkpkg.check(['python-argparse'])

import time
import socket

"""

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

USAGE = './ud-wordorder.py <source_directory> <target_directory> [-h] \n [--analyze UD_SYN_REL]'

def build_parser():

    parser = argparse.ArgumentParser(description='ud-wordorder: Extract word-order pairs frequency')


    parser.add_argument('source',help='Source for conllu files, must be dir/dir/dir')
    parser.add_argument('target',help='Target destination for csv files')
    parser.add_argument('-a', '--analyze', nargs='*', help=' Extract word-order pairs frequency: specify UD syntactic relation')

    return parser


def check_args(args):
    '''Exit if required arguments not specified'''
    check_flags = {}

def udanalyzer(conllufile,countwriter):
    conllu = pyconll.load_from_file(conllufile)
    for sentence in conllu:
        left = {}
        right = {}
        for token in sentence:
            #Most of the time, in the token itself...
            if token.deprel in args.analyze:
                if token.deprel not in left:
                    left[token.deprel] = {}
                if token.deprel not in right:
                    right[token.deprel] = {}
                #Head is on the left
                if int(token.id) > int(token.head):
                    #collect token
                    left[token.deprel][token.id]= token
                #Head is on the right
                if int(token.id) < int(token.head):
                    #collect token
                    right[token.deprel][token.id]= token
        for syntacticrel in args.analyze:
            if syntacticrel in left:
                for ident,token in left[syntacticrel].items():
                    for x in sentence:
                        if token.head == x.id:
                            head = x
                        hmLength = abs(int(token.id)-int(token.head))
                    countwriter.writerow(['X-'+syntacticrel,head.deprel,token.deprel,head.form,token.form,head.lemma,token.lemma,head.upos,token.upos,hmLength,sentence.id,os.path.splitext(os.path.basename(conllufile))[0],conllu.__len__()])
            if syntacticrel in right:
                for ident,token in right[syntacticrel].items():
                    for x in sentence:
                        if token.head == x.id:
                            head = x
                        hmLength = abs(int(token.id)-int(token.head))
                    countwriter.writerow([syntacticrel+'-X',token.deprel,head.deprel,token.form,head.form,token.lemma,head.lemma,token.upos,head.upos,hmLength,sentence.id,os.path.splitext(os.path.basename(conllufile))[0],conllu.__len__()])
    return 


def main():
    global debug
    global args
    global seppath
    parser = build_parser()
    args = parser.parse_args()
    seppath = '/'
    '''Check arguments'''    
    if check_args(args) is False:
     sys.stderr.write("There was a problem validating the arguments supplied. Please check your input and try again. Exiting...\n")
     sys.exit(1)
    '''Unknown function, I'll check it later''' 
    start_time = time.time()
    csvfile = open(args.target+"/report-"+args.source.split(seppath)[2]+".csv", 'a+', newline='',encoding='utf-8')    
    countwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    countwriter.writerow(['order', 'relfirst', 'relsecond', 'tokenfirst', 'tokensecond', 'lemmafirst', 'lemmasecond', 'uposfirst', 'upossecond', 'hmLength', 'sentence', 'source', 'size'])
    for conllufile in sorted(glob.glob(args.source+'/*.conllu')):
        conllu = pyconll.load_from_file(conllufile)
        udanalyzer(conllufile,countwriter)
        print("Done with "+conllufile)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done! Happy corpus-based typological linguistics!\n")

if __name__ == "__main__":
    main()
    sys.exit(0)

