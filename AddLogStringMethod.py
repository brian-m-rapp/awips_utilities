#!/home/awips/nwspy/anaconda/bin/python

import os
import sys
import re
import time
import argparse
import javalang

parser = argparse.ArgumentParser(description='Perform various operations on AWIPS source files.')
parser.add_argument('-r', '--requesters', action='store_true', help='List all request classes in source tree')
parser.add_argument('-c', '--candidates', action='store_true', help='List all request classes that would be updated')
parser.add_argument('-b', '--makebackups', action='store_true', help='Make a backup copy of each file before modifying')
parser.add_argument('sourcepath', help='Path to AWIPS Java source code')
cargs = parser.parse_args()

class JavaSource:
    def __init__(self, filename):
        self.filename = filename
        with open(fpath, 'r') as ifp:
            self.content = ifp.read()

        self.codetree = None


    def containsPattern(self, pattern):
        return re.search(spattern, self.content) is not None


    def classExtendingBaseclass(self, subclass, baseclass):
        pass


    def classImplementingInterface(self, interface):
        if self.codetree is None:
            self.codetree = javalang.parse.parse(self.content)

        for item in self.codetree.types:
            if type(item) is javalang.tree.ClassDeclaration:
                for imped in item.implements:
                    if imped.name == interface:
                        return item.name
        else:
            return None


    def classImplementingMethod(self, iclass, method):
        if self.codetree is None:
            self.codetree = javalang.parse.parse(self.content)

        for item in self.codetree.types:
            if type(item) is javalang.tree.ClassDeclaration:
                for imped in item.implements:
                    if imped.name == iclass:
                        for element in item.body:
                            if type(element) is javalang.tree.MethodDeclaration \
                                and element.name == method:
                                return True
        else:
            return False


if cargs.candidates:
    action = 'candidates'
elif cargs.requesters:
    action = 'requesters'
else:
    action = 'update'

logStringText = '''
    public String logString() {
        // logString stub
        return String.format("{\\\"reqClass\\\":\\\"%s\\\"}", this.getClass().getName());
    }
'''

def addLogString(fullname, content, textToInsert):
    lines = content.split('\n')
    for i in range(len(lines)-1, -1, -1):
        if lines[i].strip() == '}':    # This is the closing brace on the class
            with open(fullname, 'w') as outp:
                for line in range(i):
                    outp.write(lines[line]+'\n')

                outp.write(textToInsert)
                for line in range(line+1, len(lines)):
                    outp.write(lines[line]+'\n')
            break


def findFilesEndingWith(basepath, extension):
    matches = []
    for dirName, subdirList, fileList in os.walk(basepath):
        for fname in fileList:
            if fname.endswith(extension):
                fpath = os.path.join(dirName, fname)
                matches.append(fpath)

    return matches



timeStr  = time.strftime('.%Y%m%d_%H%M%S', time.gmtime())
spattern = re.compile('implements.*IServerRequest')
fpattern = re.compile('public.*String.*logString\(\)')
ppattern = re.compile('^package ')

rootDir = cargs.sourcepath
fcount = 0
if action == 'requesters':
    print('Requester Classes')
    print('-----------------')
elif action == 'candidates':
    print('Candidate Requester Classes')
    print('---------------------------')
else:
    print('Classes Updated')
    print('---------------')

jarfiles = []
subclasses = []
fileList = findFilesEndingWith(rootDir, '.java')
for fpath in fileList:
    javaSource = JavaSource(fpath)

    # Search file contents to see if it contains an implementation of IServerRequest
    if javaSource.containsPattern(spattern):
        if action == 'requesters':
            print(fpath)
            continue

        # Get the package name from the java parser
        package = javaSource.codetree.package.name
        jarfile = package+'.jar'
        if jarfile not in jarfiles:
            jarfiles.append(jarfile)

        # Search file contents to see if the logString method has already been implemented
        if re.search(fpattern, content) is None:
            if action == 'candidates':
                print(fpath)
                continue

            if cargs.makebackups:
                newfile = fpath + timeStr

                # Make a backup copy
                with open(newfile, 'w') as ofp:
                    ofp.write(content)

            print(fpath)
            addLogString(fpath, content, logStringText)

print()
print('Request Jars')
print('------------')
for jfile in jarfiles:
    print(jfile)

print()
print('Installed Jar Files')
print('-------------------')
installedfiles = []
for root, dirs, files in os.walk('/awips2/edex/lib'):
    for mfile in files:
        if mfile.endswith('.jar'):
            ifile = os.path.join(root, mfile)
            installedfiles.append(ifile)
            print(ifile)
print()
print('Affected Jar Files')
print('------------------')

for ifile in installedfiles:
    if os.path.basename(ifile) in jarfiles:
        print(ifile)
