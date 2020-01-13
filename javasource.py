import javalang

class JavaSource:
    def __init__(self, content):
        self.content  = content
        self.codetree = javalang.parse.parse(self.content)


    def extendsBaseclass(self, baseclass):
        pass


    def addMethodToContent(self, textToInsert):
        content = ''
        lines = self.content.split('\n')
        for i in range(len(lines)-1, -1, -1):
            if lines[i].strip() == '}':    # This is the closing brace on the class
                for line in range(i):
                    content += lines[line]+'\n'

                content += textToInsert
                for line in range(line+1, len(lines)):
                    content += lines[line]+'\n'
                break

        self.content = content
        self.codetree = javalang.parse.parse(self.content)


    def getClassImplementingInterface(self, interface):
        for item in self.codetree.types:
            if type(item) is javalang.tree.ClassDeclaration:
                if item.implements is None:
                    return None

                for imped in item.implements:
                    if imped.name == interface:
                        return item.name
        else:
            return None


    def classImplementsMethod(self, iclass, method):
        for item in self.codetree.types:
            if type(item) is javalang.tree.ClassDeclaration:
                if item.name == iclass:
                    for element in item.body:
                        if type(element) is javalang.tree.MethodDeclaration \
                            and element.name == method:
                            return True
        else:
            return False


    def getPackageName(self):
        return self.codetree.package.name


    def writeContent(self, fullname):
        with open(fullname, 'w') as outp:
            outp.write(self.content)
