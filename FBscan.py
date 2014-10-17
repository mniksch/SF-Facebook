#!python3
#This file scans in a Facebook messages file
from xml.etree.ElementTree import parse # for parsing XML
import csv #imports the csv module for working with those types of files
from datetime import datetime #For managing dates of the messages
import sys

def fbDate(txt):
  import re
  dump, mo, da, ye, ti, tz = re.split(', | at | ',txt)
  ho = ti[0:ti.find(':')]
  mi = ti[-4:-2]
  am = ti[-2:]
  ntxt = '%s %2d %4d %2d %2d %s' % (mo, int(da), int(ye), int(ho), int(mi), am)
  return datetime.strptime(ntxt,'%B %d %Y %I %M %p')

if len(sys.argv) != 3:
	print("Usage: %s messagesfile.html outputfile.csv" % sys.argv[0])
	exit()

#--File Initialization---
datafile = sys.argv[1] #'messages.htm'
outfile = sys.argv[2] #'testOut.csv'

f = open(datafile, 'rt',encoding='utf-8', errors='ignore')
outf = open(outfile, 'wt',encoding='utf-8')
writer = csv.writer(outf, delimiter=',', quoting=csv.QUOTE_MINIMAL, \
	 lineterminator='\n')
headers = ['Index','Contact Name','Date of Contact','Comments', \
           'Communication Status', 'Mode of Communication', \
       	   'Subject','Initiated by alum']
writer.writerow(headers)

#--Begin parsing the input file
print('Beginning to parse file')
doc=parse(f)

#The parsing here is based on the observed structure of the Facebook dump
docbody=doc.getroot()[1].getchildren()[1] #second "div" group in 'body' tag
ownerName=docbody.getchildren()[0].text #Name of person who downloaded messages
allMessages=docbody.getchildren()[1] #Another "div" group that contains all messages

#Code below here begins parsing the main messages section
#Each child of allMessages is a set of data about a single correspondent

allDetails = [] #store every detail for now in a list of lists of lists
allNames = [] #store the talkers for each convo
talkerList = {} #used to strip out dupicate names in lists
theseTalkers = [] # empty set of messages senders to build up
theseMessages = [] # empty set of all details for this singlePerson

for singlePerson in allMessages.getchildren(): # loop for all correspondents
  theseTalkers = [] # empty set of messages senders to build up
  theseMessages = [] # empty set of all details for this singlePerson
  convoBetween=singlePerson.text
  if len(convoBetween.split(sep=',')) != 2: continue #skip group convos
  convoA=convoBetween.split(sep=',')[-1].strip()
  convoB=convoBetween.split(sep=',')[0].strip()
  convoWith = (set([convoA, convoB]) - set([ownerName])).pop()

  # singlePerson contains an even number of elements, with each pair encoding
  # a message from one person to the next
  for i in range(0,len(singlePerson.getchildren()),2):
    deets = singlePerson.getchildren()[i]
    convo = singlePerson.getchildren()[i+1]
    talkWith = deets[0][0].text
    talkWhen = fbDate(deets[0][1].text)
    talkText = convo.text
    theseTalkers.append(talkWith)
    theseMessages.append([ownerName,convoWith,talkWith,talkWhen,talkText])
  for names in set(theseTalkers): #keep a record of how many times each name appears
    if names in talkerList: talkerList[names] = talkerList[names] + 1
    else: talkerList[names] = 1
  allDetails.append(theseMessages)
  allNames.append(theseTalkers)
# end of looping through each singlePerson

#Now do some cleaning up of the lists
print('Now cleaning up lists')

#First substitute names in convos with the correct facebook name
ownerAliases=[]
for names in talkerList:
  if talkerList[names] > 2: ownerAliases.append(names)
#now ownerAliases contains all the aliases for 'ownerName'

#Loop through the 'allNames' lists to force names to best name of person
for convo in range(0,len(allNames)): #allNames and allDetails have same length
  convoWith = allDetails[convo][0][1]
  for messages in range(0,len(allNames[convo])):
    if allNames[convo][messages] in ownerAliases:
      allNames[convo][messages] = ownerName
    else:
      allNames[convo][messages] = convoWith
#Now the allNames array should have the right speaker for each line

print('Beginning final output')
#Now loop through all people and messages, dumping the final output
# by combining the messages that happen on the same date
curDate=datetime.today() #just initializing prior to for loop scope
curMessage='' 
curPerson=''
for person in range(0, len(allDetails)):
  curMessage=''
  twoWay = False #indicates if two way conversation or just outreach
  alumInit = False #indicates if alum initiated the conversation
  curDate=allDetails[person][0][3].date()
  curPerson=allDetails[person][0][1]
  for message in range(0, len(allDetails[person])):
    if allDetails[person][message][3].date() == curDate:
      #add to the current message (although expect it might be the first)
      twoWay = twoWay or allNames[person][message] == curPerson
      if len(curMessage) > 0: curMessage = curMessage + '\n'
      if len(curMessage) == 0: alumInit = twoWay
      curMessage = curMessage + '(' + allNames[person][message] + \
	  ' @ ' + allDetails[person][message][3].strftime('%I:%M%p') + '): '
      curMessage = curMessage + str(allDetails[person][message][4])
      #positive if case is done
    else:
      #First write the buffered message then initialize the new message
      # headers = ['Index','Contact Name','Date of Contact','Comments', \
      #            'Communication Status', 'Mode of Communication', \
      #            'Subject','Initiated by alum']
      outBuf = []
      dateText = curDate.strftime('%m/%d/%Y')
      outBuf.append(curPerson +':'+ dateText +':'+ str(len(curMessage)))
      outBuf.extend([curPerson, curDate, curMessage])
      if twoWay: outBuf.append('Successful communication')
      else: outBuf.append('Outreach only')
      outBuf.append('Social Networking')
      if twoWay: outBuf.append('Facebook transcript')
      else: outBuf.append('Facebook outreach transcript')
      if alumInit: outBuf.append('TRUE')
      else: outBuf.append('FALSE')
      writer.writerow(outBuf)
      
      #initialize the new message
      curDate = allDetails[person][message][3].date()
      twoWay = allNames[person][message] == curPerson
      alumInit = twoWay
      curMessage = '(' + allNames[person][message] + \
	  ' @ ' + allDetails[person][message][3].strftime('%I:%M%p') + '): '
      curMessage = curMessage + str(allDetails[person][message][4])
  #write the buffered message (finished looping through this person)
  outBuf = []
  dateText = curDate.strftime('%m/%d/%Y')
  outBuf.append(curPerson +':'+ dateText +':'+ str(len(curMessage)))
  outBuf.extend([curPerson, curDate, curMessage])
  if twoWay: outBuf.append('Successful communication')
  else: outBuf.append('Outreach only')
  outBuf.append('Social Networking')
  if twoWay: outBuf.append('Facebook transcript')
  else: outBuf.append('Facebook outreach transcript')
  if alumInit: outBuf.append('TRUE')
  else: outBuf.append('FALSE')
  writer.writerow(outBuf)

  #--Done looping through this person
#--Done looping through all messages

#--File wrapups
f.close()
outf.close()
