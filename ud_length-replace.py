import sys
from tqdm import tqdm
import os

try:
    conllufile = sys.argv[1]
except:
    print("please specify file")
    exit()

#Input file
data = open(conllufile, mode="r", encoding="utf-8")
#delete file
os.remove(conllufile)
#write new file
newdata = open(conllufile, mode="w", encoding="utf-8")

file_string = data.read()
sentences = file_string.split("\n\n")


for sentence in tqdm(sentences):
    parse_lines = sentence.split("\n")
    words = []
    for line in parse_lines:
        if len(line.split("\t")) < 8:
            newdata.write(line + "\n")
        else:
            words.append(line) 
    
    punctuation_indices = []
    for word in words:
        cells = word.split("\t")
        if cells[7] == "punct":
            punctuation_indices.append(int(cells[0]))
    
    length_without_punctuation = len(words) - len(punctuation_indices)
    dependency_lengths = []
    dependency_sum = 0
    
    for word in words:
        cells = word.split("\t")
        parent = int(cells[6])
        child = int(cells[0])
        dependency_length = parent - child
        
        for p in punctuation_indices:
            if p>min(parent,child) and p<max(parent,child):
                dependency_length = dependency_length - 1
        if cells[7].lower() == "root":
            dependency_length = 0
        dependency_lengths.append(dependency_length)
        if cells[7].lower() != "punct":
            dependency_sum += abs(dependency_length)
        
    try:
        dependency_avg = dependency_sum/(len(words) - len(punctuation_indices) - 1)
    except:
        dependency_avg = 0

    for i,word in enumerate(words):
        cells = word.split("\t")
        #We rewrite conllu fields from 0 to 9, and add new fields
        newdata.write(cells[0] + "\t" + cells[1] + "\t" + cells[2] + "\t" + cells[3] + "\t" + cells[4] + "\t" + cells[5] + "\t" + cells[6] + "\t" + cells[7] + "\t" + cells[8] + "\t" + cells[9] + "\t"+ str(dependency_lengths[i]) + "\t" + str(length_without_punctuation) + "\t" + str(dependency_sum) + "\t" + str(dependency_avg) + "\n")
    newdata.write("\n")


newdata.close()
