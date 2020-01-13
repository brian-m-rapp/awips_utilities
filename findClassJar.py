import os
import argparse
import javasource

class FindClassJar:
    def __init__(self, sourcePath):
        self.installedJarFileRoot = '/awips2/edex/lib/plugins'
        self.rootDir = sourcePath
        self.findAllJarFiles()


    def findAllJarFiles(self):
        self.jarFiles = []
        for root, _, files in os.walk(self.installedJarFileRoot):
            for mfile in files:
                if mfile.endswith('.jar'):
                    ifile = os.path.join(root, mfile)
                    self.jarFiles.append(ifile)


    def getJarContainingPackage(self, package):
        for i in range(package.count('.')):
            splitPackage = package.rsplit('.', i)[0]
            for j in self.jarFiles:
                if splitPackage == os.path.splitext(os.path.basename(j))[0]:
                    return j

        return None


    def getFileDefiningClass(self, className):
        for dirName, _, fileList in os.walk(self.rootDir):
            for fname in fileList:
                splitFile = os.path.splitext(fname)
                if splitFile[0] == className and splitFile[1] == '.java':
                    return os.path.join(dirName, fname)

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find the source file where the class is defined, the package it belongs to, and the deployed jar file name')
    parser.add_argument('sourcepath', help='Path to base of AWIPS Java source code (e.g. - /home/awips/git/awips_19.3.1)')
    parser.add_argument('className', nargs='+', help='Java class name')
    cargs = parser.parse_args()

    myObj = FindClassJar(os.path.expanduser(cargs.sourcepath))

    for className in cargs.className:
        sourceFile = myObj.getFileDefiningClass(className)

        if sourceFile is None:
            print('Could not find source file defining class {}'.format(className))
            continue

        with open(sourceFile, 'r') as ifp:
            content = ifp.read()

        try:
            jfile = myObj.getJarContainingPackage(javasource.JavaSource(content).getPackageName())
        except Exception as e:
            print('Exception {} while parsing {}'.format(e, sourceFile))
            continue

        if jfile is None:
            print('Could not find jar file containing class {}'.format(className))
        else:
            print('Jar file containing {} class: {}'.format(className, jfile))
