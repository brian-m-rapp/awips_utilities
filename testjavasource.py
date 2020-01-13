import os
import javasource as js

basepath = '/home/awips/source/awips19.3.1/'
sourceFile = basepath + '/AWIPS2_Core/common/com.raytheon.uf.common.dataquery/src/com/raytheon/uf/common/dataquery/requests/DbQueryRequest.java'
interface = 'IServerRequest'

with open(sourceFile, 'r') as ifp:
    content = ifp.read()

jsrc = js.JavaSource(content)

iclass = jsrc.classImplementingInterface(interface)
if iclass is not None:
    print('{} implements IServerRequest'.format(os.path.basename(sourceFile)))
    print('{} belongs to package {}'.format(os.path.basename(sourceFile), jsrc.package))
    print('Class implementing {} is {}'.format(interface, iclass))
