#!python3
#This file scans an input that exhibits errors in the utf-8 encoding
import sys

if len(sys.argv) != 3:
	print("Usage: %s inputtextfile outputfile" % sys.argv[0])
	exit()

#--File Initialization---
datafile = sys.argv[1] #'messages.htm'
outfile = sys.argv[2]

f = open(datafile, 'rt',encoding='utf-8',errors='ignore')
outF = open(outfile, 'wt', encoding='utf-8')

#--Begin parsing the input file
row = 1
try:
    for line in f:
        for ch in line:
            try:
                print(ch, end='',file=outF)
            except:
                try:
                    print(ch.encode('utf-8'),file=outF)
                except:
                    print('\n\nFailure in row %d' % row)
                    print(int(ch.encode('utf-8'),base=16))
                exit()
        row += 1
        print(row)
except:
    print('\n\nFailure in row %d at position %d' % (row,f.tell()))
