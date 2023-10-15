############ This script prints out comma-separated spreadsheet(s) (report-language.csv) with the ratio of word order pairs, core argument and predicate morpho-syntactic features in conllu files ########
#!/usr/bin/env python3
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
import io
import conllu
from pathlib import Path
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

USAGE = './ud-clauseorder.py <source_directory> <target_directory> [-h]'

def build_parser():

    parser = argparse.ArgumentParser(description='ud-wordorder: Extract sentence/clause frequency')


    parser.add_argument('source',help='Source for conllu files, must be dir/dir/dir')
    parser.add_argument('target',help='Target destination for csv files')

    return parser


def check_args(args):
    '''Exit if required arguments not specified'''
    check_flags = {}


def getvalues(clause,sentdict): 
    sentdict[3] = {'pos': clause.token["upos"]}
    if clause.token["feats"] is not None:
        sentdict[3].update(clause.token["feats"])
    print(sentdict)
    for token in clause.children:
        #Collect information on subject and object
        if token.token["deprel"] in subj:
            sentdict[1] = token.token["feats"]
            sentdict[8] = "no"
            subj_id = token.token["id"]
        if token.token["deprel"] in obj:
            sentdict[2] = token.token["feats"]
            sentdict[9] = "no"
            obj_id = token.token["id"]
        if token.token["deprel"] in predstr and token.token["feats"] != None:
            print(sentdict[3])
            sentdict[3].update(token.token["feats"])
    if sentdict[1] != None and sentdict[2] == None:
        if subj_id > clause.token["id"]:
            sentdict[4] = "VS"
        if subj_id < clause.token["id"]:
            sentdict[4] = "SV"
    #Obj-verb order in null-subject clause
    if sentdict[2] != None and sentdict[1] == None:
        if obj_id > clause.token["id"]:
            sentdict[5] = "VO"
        if obj_id < clause.token["id"]:
            sentdict[5] = "OV"
    #Six orders
    if sentdict[1] != None and sentdict[2] != None:
            #SOV
            if subj_id < clause.token["id"] and obj_id < clause.token["id"] and subj_id < obj_id:
                sentdict[6] = "SOV"
            #SVO
            if subj_id < clause.token["id"] and obj_id > clause.token["id"] and subj_id < obj_id:
                sentdict[6] = "SVO"
            #VSO
            if subj_id > clause.token["id"] and obj_id > clause.token["id"] and subj_id < obj_id:
                sentdict[6] = "VSO"
            #OVS
            if subj_id > clause.token["id"] and obj_id < clause.token["id"] and subj_id > obj_id:
                sentdict[6] = "OVS"
            #VOS
            if subj_id > clause.token["id"] and obj_id > clause.token["id"] and subj_id > obj_id:
                sentdict[6] = "VOS"
            #OSV
            if subj_id < clause.token["id"] and obj_id > clause.token["id"] and subj_id > obj_id:
                sentdict[6] = "OSV"
    if sentdict[1] == None:
        sentdict[1] = "null"
        sentdict[8] = "yes"
    if sentdict[2] == None:
        sentdict[2] = "null"
        sentdict[9] = "yes"
    if clause.token["deprel"] == "root":
        sentdict[7] = "main"
    else:
        if clause.token["id"] > clause.token["head"]:
            sentdict[7] = "right"
        if clause.token["id"] < clause.token["head"]:
            sentdict[7] = "left"
    return sentdict


def getmood(clause):
    mood = None
    if clause[3] != None:
            if "Mood" in clause[3]:
                mood = clause[3]["Mood"]
            elif "VerbForm" in clause[3]:
                mood = clause[3]["VerbForm"]
    return mood

    


def udanalyzer(conllufile,countwriter):
    data = open(conllufile, mode="r", encoding="utf-8")
    split_func = lambda line, i: line[i].split("-")
    #sentences = conllu.parse_tree(data.read(),field_parsers={"id": split_func})
    sentences = conllu.parse_tree(data.read())
    length = sum(1 for x in sentences)
    for sentence in sentences:
        print("Analyzing sentence "+sentence.metadata["sent_id"])
        sentdict = {"sent_id": sentence.metadata, "main": ["main",None,None,None,None,None,None,None,None,None,None,None]  }
        main = getvalues(sentence,sentdict["main"])
        mood = getmood(sentdict["main"])
        countwriter.writerow([main[0],main[1],main[2],main[3],main[4],main[5],main[6],main[7],"main","0",sentence.metadata["sent_id"],os.path.basename(conllufile),mood,main[8],main[9]])
        for token in sentence.children:
            #Does the token correspond to one of the wanted clauses?
            #Sub -1
            head = sentence.token["deprel"]
            if token.token["deprel"] in clausetype:
                sentdict = {"sent_id": sentence.metadata, "subordinate": [token.token["deprel"],None,None,None,None,None,None,None,None,None,None,None]  }
                sub = getvalues(token,sentdict["subordinate"])
                mood = getmood(sentdict["subordinate"])
                #Get the clause relative position
                countwriter.writerow([sub[0],sub[1],sub[2],sub[3],sub[4],sub[5],sub[6],sub[7],head,"-1",sentence.metadata["sent_id"],os.path.basename(conllufile),mood,sub[8],sub[9]])
                #Sub -2
                head = token.token["deprel"]
                for token in token.children:
                    if token.token["deprel"] in clausetype:
                        sentdict = {"sent_id": sentence.metadata, "subordinate": [token.token["deprel"],None,None,None,None,None,None,None,None,None,None,None]  }
                        sub = getvalues(token,sentdict["subordinate"])
                        mood = getmood(sentdict["subordinate"])
                        countwriter.writerow([sub[0],sub[1],sub[2],sub[3],sub[4],sub[5],sub[6],sub[7],head,"-2",sentence.metadata["sent_id"],os.path.basename(conllufile),mood,sub[8],sub[9]])
            #Does the token is a coordination?
            #Sub 0
            if token.token["deprel"] in conj:
                sentdict = {"sent_id": sentence.metadata, "coord": [token.token["deprel"],None,None,None,None,None,None,None,None,None,None]  }
                coord = getvalues(token,sentdict["coord"])
                mood = getmood(sentdict["coord"])
                countwriter.writerow([coord[0],coord[1],coord[2],coord[3],coord[4],coord[5],coord[6],coord[7],head,"0",sentence.metadata["sent_id"],os.path.basename(conllufile),mood,coord[8],coord[9]])
                #Sub -1
                head = token.token["deprel"]
                for token in token.children:
                    if token.token["deprel"] in clausetype:
                        sentdict = {"sent_id": sentence.metadata, "subordinate": [token.token["deprel"],None,None,None,None,None,None,None,None,None,None,None]  }
                        sub = getvalues(token,sentdict["subordinate"])
                        mood = getmood(sentdict["subordinate"])
                        countwriter.writerow([sub[0],sub[1],sub[2],sub[3],sub[4],sub[5],sub[6],sub[7],head,"-1",sentence.metadata["sent_id"],os.path.basename(conllufile),mood,sub[8],sub[9]])
                        #Sub -2
                        head = token.token["deprel"]
                        for token in token.children:
                            if token.token["deprel"] in clausetype:
                                sentdict = {"sent_id": sentence.metadata, "subordinate": [token.token["deprel"],None,None,None,None,None,None,None,None,None,None,None]  }
                                sub = getvalues(token,sentdict["subordinate"])
                                mood = getmood(sentdict["subordinate"])
                                countwriter.writerow([sub[0],sub[1],sub[2],sub[3],sub[4],sub[5],sub[6],sub[7],head,"-2",sentence.metadata["sent_id"],os.path.basename(conllufile),mood,sub[8],sub[9]])

def main():
    global debug
    global args
    global seppath
    global subj
    global obj
    global conj
    global predstr
    global clausetype
    parser = build_parser()
    args = parser.parse_args()
    clausetype = ["acl", "acl:relcl", "acl:adv", "acl:attr", "acl:cleft", "acl:cmpr", "acl:inf", "acl:relat", "advcl", "advcl:abs", "advcl:cau:", "advcl:cleft", "advcl:cmpr", "advcl:cond", "advcl:coverb", "advcl:eval", "advcl:lcl", "advcl:lto", "advcl:mcl", "advcl:pred", "advcl:relcl", "advcl:svc", "advcl:tcl", "ccomp", "ccomp:cleft", "ccomp:obj", "ccomp:pmod", "ccomp:pred", "csubj", "csubj:cleft", "csubj:cop", "csubj:pass", "xcomp", "xcomp:cleft", "xcomp:ds", "xcomp:obj", "xcomp:pred", "xcomp:subj"]
    subj = ["nsubj","nsubj:advmod", "nsubj:caus", "nsubj:cleft", "nsubj:cop","nsubj:lvc","nsubj:pass"]
    obj = ["obj","obj:advmod","obj:advneg","obj:agent", "obj:lvc","obj:obl"]
    conj = ["conj","conj:expl","conj:extend","conj:svc"]
    predstr = ["aux","aux:pass","cop"]
    seppath = '/'
    '''Check arguments'''    
    if check_args(args) is False:
     sys.stderr.write("There was a problem validating the arguments supplied. Please check your input and try again. Exiting...\n")
     sys.exit(1)
    '''Unknown function, I'll check it later'''
    start_time = time.time()
    csvfile = open(args.target+"/report-"+str(os.path.basename(os.path.dirname(args.source)))+".csv", 'a+', newline='',encoding='utf-8')    
    countwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    countwriter.writerow(['type', 'subj', 'obj', 'predicate', 'SV_order', 'OV_order', 'SOV_order', 'position', 'head', 'level_embedding', 'sentence', 'source','mood','null_subj','null_obj'])
    for conllufile in sorted(glob.glob(args.source+'/*.conllu')):
        udanalyzer(conllufile,countwriter)
        print("Done with "+conllufile)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done! Happy corpus-based typological linguistics!\n")

if __name__ == "__main__":
    main()
    sys.exit(0)

