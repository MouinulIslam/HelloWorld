#!/usr/bin/env python






fout = open('corpa.txt','w')

fout.write('[\n')



for k in range(1,5):
    print k
    banFile = 'ban' + str(k) + '.txt'
    engFile = 'eng' + str(k) + '.txt'
    fb = open(banFile,'r').read().split('\n')
    fe = open(engFile,'r').read().split('\n')
    k = k + 1
    i = 0
    for bLine in fb:
        eLine = fe[i]
        i = i + 1
        fout.write('  {\n')
        eLine = eLine.replace('"','')
        eLine = eLine.replace('\\','')
        bLine = bLine.replace('"','')
        bLine = bLine.replace('\\','')
        fout.write('    \"Eng\": \"' + eLine + '\",' + '\n')
        fout.write('    \"Ban\": \"' + bLine + '\"' + '\n')
        fout.write('  },\n')
fout.write(']')
print 'line number = ', i
#.replace('"',r'')









