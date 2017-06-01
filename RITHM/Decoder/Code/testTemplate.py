# Test Program to decypher the template

import time, os, re, sys
from decode import decoder
from combine import csvcombine

directory = "C:\\Users\\crlar\\Desktop\\MagicBird\\"

lineCount = 0
with open(directory + "template.txt", 'r') as template:
    for line in template:
        line = re.sub('\r', '', line)
        line = re.sub('\n', '', line)
        if lineCount == 0:
            dirIn = str(line)[str(line).find(":")+2:]
            dirIn.strip()
        if lineCount == 1:
            dirOut = str(line)[str(line).find(":")+2:]
        if lineCount == 2:
            dirTemp = str(line)[str(line).find(":")+2:]
        #this doesn't work yet
        #if lineCount == 3:
        #    test = str(line)[str(line).find(":")+2:]
        #    if test is "None":
        #        test = None
        #    else:
        #        test = True
        if lineCount == 4:
            start = int(str(line)[str(line).find(":")+1:])
        if lineCount == 5:
            end = int(str(line)[str(line).find(":")+1:])
        if lineCount == 6:
            geo = str(line)[str(line).find(":")+2:]
            if geo == "1":
                geo = 1
            else:
                geo = 0
        if lineCount == 7:
            emoji_file = str(line)[str(line).find(":")+2:]
            emojify = 0
            if emoji_file != '':
                emojify = 1
        if lineCount == 8:
            combine = str(line)[str(line).find(":")+2:]
        if lineCount == 9:
            clear = str(line)[str(line).find(":")+2:]       #Clear will remove all files in the tempDir when finished
            if clear == '1':
                clear = 1
            else:
                clear = 0
        if lineCount == 10:
            keywords = {}
        if lineCount >= 11:
            if line.rstrip() not in keywords.keys():
                if line.rstrip() != '' and line.rstrip() != ' ':
                    keywords.update({line.rstrip():0})
        lineCount += 1

if clear == 1:
    files = sorted(os.listdir(dirTemp))
    for f in files:
        os.remove(dirTemp+f)

files = sorted(os.listdir(dirIn))
print("\nREADING TWEETS FROM " + str(start) + ' to ' + str(end) +'\n')
#read all the files in the directory
t = str(time.time())
for f in files:
    if f[-5:] =='.json':
        #try:
        if int(f[:8]) >= start:
            if int(f[:8]) <= end:
                d = decoder(keywords, dirOut, directory, dirTemp, emojify, emoji_file)
                record = d.fixjson(dirIn, f)
                d.jsontocsv(record,f,geo,emojify)
        #except:
        #    print("ERROR!!!!!!!!!!!")

c = csvcombine(dirOut, directory, dirTemp)
c.combinecsv(combine, clear)
