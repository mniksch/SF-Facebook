#!python3
'''
This file takes a "names_for_matching.csv" output from the Facebook parser
and tries to match it to another file with Salesforce IDs
'''
import csv
from datetime import datetime
import sys

if len(sys.argv) != 3:
    print('Usage: %s names_for_matching.csv roster_file.csv' % sys.argv[0])
    exit()

#File initialization
matchNames = []
with open(sys.argv[1]) as f_names:
    reader = csv.reader(f_names)
    for row in reader:
        row.append(False) #initially, there is no match
        matchNames.append(row)

print('Read in %d lines of names to match.' % len(matchNames))
matchNames.pop(0)

''' For the roster, we're expecting 4 columns:
-Salesforce ID
-Last Name
-First Name
-HS Class'''
roster = []
with open(sys.argv[2]) as f_roster:
    reader = csv.reader(f_roster)
    for row in reader:
        row.append(False) #initially, there is no match
        roster.append(row)
print('Read in %d lines of roster to match.' % len(roster))
roster.pop(0)

#Now insert a last name and first name field into the Facebook table
for row in matchNames:
    names=row[0].split(sep=' ')
    lastName = names[-1]
    if lastName.find('jr') > -1: lastName = names[-2]
    if lastName.find('JR') > -1: lastName = names[-2]
    if lastName.find('Jr') > -1: lastName = names[-2]
    if lastName.find('III') > -1: lastName = names[-2]
    firstName =names[0]
    conYear = row[1][0:4]
    row.insert(1,lastName)
    row.insert(2,firstName)
    row.insert(3,conYear)


def compareWFun(matchNames, roster, func):
    '''This function will take a passed comparison function and map
    the resultant matches back to their indices'''
    matches=0
    for un in matchNames:
        if un[5]: continue #skip this Facebook name if we've found it
        for alum in roster:
            if alum[4]: continue #skip this if roster already matched
            if func(un, alum):
                matches+=1
                un[5] = alum[0] #matches to Salesforce Id
                alum[4] = un[0] #matches to Facebook Id
                break
    return matches

#Now do a first pass/perfect comparison of first/last/year
def perfectCompare(un, alum):
    #       LN     FN     Year       LN       FN       Year
    return (un[1], un[2], un[3]) == (alum[1], alum[2], alum[3])
def perfectCompareY1(un, alum):
    return (un[1], un[2], int(un[3])) == (alum[1], alum[2], int(alum[3])+1)
def perfectCompareY2(un, alum):
    return (un[1], un[2], int(un[3])) == (alum[1], alum[2], int(alum[3])+2)
def perfectCompareFN5(un, alum):
    return (un[1], un[2][:5], un[3]) == (alum[1], alum[2][:5], alum[3])
def perfectCompareFN5Y1(un, alum):
    return (un[1], un[2][:5], int(un[3])) == (alum[1], alum[2][:5], int(alum[3])+1)
def perfectCompareFN5LN5(un, alum):
    return (un[1][:5], un[2][:5], un[3]) == (alum[1][:5], alum[2][:5], alum[3])

print('%d perfect matches' % compareWFun(matchNames, roster, perfectCompare))
print('%d year-1 matches'  % compareWFun(matchNames, roster, perfectCompareY1))
print('%d year-2 matches'  % compareWFun(matchNames, roster, perfectCompareY2))
print('%d perfect FN5 matches' %
        compareWFun(matchNames, roster, perfectCompareFN5))
print('%d FN5 year-1 matches' %
        compareWFun(matchNames, roster, perfectCompareFN5Y1))
print('%d FN5 LN5 matches' %
        compareWFun(matchNames, roster, perfectCompareFN5LN5))

print('Facebook names still looking for a match: %d' %
        len([w for w in matchNames if not w[5]]))
'''Some potential further match criteria
-Perfect match on first name (if only one)
-Strip Jr and III from names
'''

#Now dump to an Excel file
import xlsxwriter

workbook = xlsxwriter.Workbook('MatchWorksheet.xlsx')
fb=workbook.add_worksheet('Facebook_names')
rs=workbook.add_worksheet('Class_roster')
fb.write_row('A1', ['FB Name', 'LastName', 'FirstName', 'FC Year', 'FC', 'Match ID'])
fb.set_column('A:A',34)
fb.set_column('B:C',15)
fb.set_column('D:E',10)
fb.set_column('F:F',20)
rowIndex=1
for w in matchNames:
    fb.write_row(rowIndex,0,w)
    rowIndex+=1
fb.autofilter(0,0,rowIndex-1,5)

rs.write_row('A1', ['SF ID', 'LastName', 'FirstName', 'HS Class', 'FB Match'])
rs.set_column('A:A',20)
rs.set_column('B:C',15)
rs.set_column('D:D',10)
rs.set_column('E:E',35)
rowIndex=1
for w in roster:
    rs.write_row(rowIndex,0,w)
    rowIndex+=1
rs.autofilter(0,0,rowIndex-1,4)

workbook.close()
