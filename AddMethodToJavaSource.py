import os
import sys
import re
import json
import argparse
from importlib import util as importutil
import javasource

installedJarFileRoot = '/awips2/edex/lib/plugins'
updatedJarFilesFile  = os.path.expanduser('~/updated_jarfiles.json')

def AddMethod(fullname, content, textToInsert):
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


def findFileDefiningClass(basepath, className):
    for dirName, _, fileList in os.walk(basepath):
        for fname in fileList:
            if os.path.splitext(fname)[0] == className:
                return os.path.join(dirName, fname)

    return None


def findFilesEndingWith(basepath, extension):
    matches = []
    for dirName, _, fileList in os.walk(basepath):
        for fname in fileList:
            if fname.endswith(extension):
                fpath = os.path.join(dirName, fname)
                matches.append(fpath)

    return matches


def modimport(mod):
    if '/' in mod or '.py' in mod:
        name = mod.split('.')[0].split('/')[-1]
        spec = importutil.spec_from_file_location(name, mod)
        foo = importutil.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo
    else:
        return __import__(mod)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform various operations on AWIPS source files.')
    parser.add_argument('-b', '--makebackups', action='store_true', help='Make a backup copy of each file before modifying')
    parser.add_argument('-t', '--testmode',    action='store_true', help='When -u is provided, output what would be done, but do not modify files')
    parser.add_argument('action',     help='Action to take - can be "requesters", "candidates", or "update"')
    parser.add_argument('configfile', type=argparse.FileType('r'), help='Path to configuration file')
    parser.add_argument('sourcepath', help='Path to base of AWIPS Java source code (e.g. - /home/awips/git/awips_19.3.1)')
    cargs = parser.parse_args()

    if cargs.action.startswith('req'):
        action = 'requesters'
    elif cargs.action.startswith('can'):
        action = 'candidates'
    elif cargs.action.startswith('upd'):
        action = 'update'
    else:
        print('Unknown action {} -- must be "requesters", "candidates", or "update"'.format(cargs.action))
        sys.exit(1)

    if not os.path.isfile(os.path.expanduser(cargs.configfile)):
        print('Specified config file {} not found'.format(cargs.configfile))
        sys.exit(1)

    if cargs.makebackups:
        import time
        timeStr  = time.strftime('.%Y%m%d_%H%M%S', time.gmtime())

    try:
        config = modimport(cargs.configfile)
    except Exception as e:
        print('Exception {} importing config file {}'.format(e, cargs.configfile))
        sys.exit(1)

    if 'interface' in config.code:
        spattern = re.compile('implements.*{}'.format(config.code['interface']))
        entityName = config.code['interface']
    elif 'classname' in config.code:
        spattern = re.compile('extends.*{}'.format(config.code['classname']))
        entityName = config.code['classname']
    else:
        print('Abstraction type (interface or classname) not found in config file')
        sys.exit(1)

    methodName = config.code['methodName']
    methodSource = config.code['methodSource']

    if hasattr(config, 'extraClasses'):
        extraClasses = config.extraClasses

    rootDir = os.path.expanduser(cargs.sourcepath)
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
    
    packages = []
    subclasses = []
    skippedFiles = []
    fileList = findFilesEndingWith(rootDir, '.java')

    for fpath in fileList:
        with open(fpath, 'r') as ifp:
            content = ifp.read()

        # Use a regular expression search to determine if the interface is a
        # candidate.  If the file contains a match, then parse the java source
        # and verify that the match wasn't a false positive.  The regular
        # expression search is used because it is significantly faster than
        # parsing the file into java elements.
        if re.search(spattern, content) is not None:
            try:
                javaSource = javasource.JavaSource(content)
            except Exception as e:
                print('Exception {} while parsing {} -- skipping'.format(e, fpath))
                skippedFiles.append(fpath)
                continue

            # Search file contents to see if it contains an implementation of IServerRequest
            className = javaSource.getClassImplementingInterface(entityName)
            if className is not None:
                if action == 'requesters':
                    print(fpath)
                    continue

                # Get the package name from the java parser
                package = javaSource.getPackageName()
                if package not in packages:
                    packages.append(package)

                # Search file contents to see if the logString method has already been implemented
                if not javaSource.classImplementsMethod(className, methodName):
                    if action == 'candidates':
                        print(fpath)
                        continue

                    if cargs.makebackups:
                        newfile = fpath + timeStr

                        # Make a backup copy
                        with open(newfile, 'w') as ofp:
                            ofp.write(content)

                    print(fpath)
                    if not cargs.testmode:
                        javaSource.addMethodToContent(methodSource)
                        javaSource.writeContent(fpath)

    for exFile in extraClasses:
        fpath = os.path.join(rootDir, exFile)
        with open(fpath, 'r') as ifp:
            content = ifp.read()

        try:
            javaSource = javasource.JavaSource(content)
        except Exception as e:
            print('Exception {} while parsing {} -- skipping'.format(e, fpath))
            skippedFiles.append(fpath)
            continue

        # Get the package name from the java parser
        package = javaSource.getPackageName()
        if package not in packages:
            packages.append(package)
    

    print()
    print('Request Packages')
    print('----------------')
    packages.sort()
    for p in packages:
        print(p)

    '''
    print()
    print('Installed Jar Files')
    print('-------------------')
    '''
    jarFiles = []
    for root, dirs, files in os.walk(installedJarFileRoot):
        for mfile in files:
            if mfile.endswith('.jar'):
                ifile = os.path.join(root, mfile)
                jarFiles.append(ifile)
                # print(ifile)

    updatedJars = []
    packageJars = {}
    unknownPackages = []
    for p in packages:
        for i in range(p.count('.')):
            splitPackage = p.rsplit('.', i)[0]
            for j in jarFiles:
                if splitPackage == os.path.splitext(os.path.basename(j))[0]:
                    if j not in packageJars:
                        packageJars[j] = []

                    packageJars[j].append(p)
                    if j not in updatedJars:
                        updatedJars.append(j)
                    break   # Found jar file matching package, break from this loop, which will break from enclosing loop (continue skipped)
            else:
                continue    # No match found, so keep going with split operation
            break
        else:
            unknownPackages.append(p)

    print()
    print('Affected Jar Files')
    print('------------------')
    updatedJars.sort()
    with open(updatedJarFilesFile, 'w') as ofp:
        ofp.write(json.dumps(updatedJars, indent=4))

    for j in updatedJars:
        print(j)

    print()
    print('Package belongs to Jar')
    print('----------------------')
    for j in sorted(packageJars.keys()):
        print(j)
        for p in packageJars[j]:
            print('\t{}'.format(p))

    print()
    print('Packages without Jar File')
    print('-------------------------')
    unknownPackages.sort()
    for p in unknownPackages:
        print(p)

    print()
    print('Wrote list of updated jar files to {}'.format(updatedJarFilesFile))
