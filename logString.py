'''
abstractionType - interface or class (maps to implements or extends)
methodName - name of method to add
methodSource - source code of method
'''

code = {}
code['interface']    = 'IServerRequest'
code['methodName']   = 'logString'
code['methodSource'] = '''
    public String logString() {
        // logString stub
        return String.format("{\\\"reqClass\\\":\\\"%s\\\"}", this.getClass().getName());
    }
'''

'''
Class hierarchy
---------------
IServerRequest
    RegistryQuery
        BaseQuery
            AdhocRegistryQuery
            AssociationQuery
'''

extraClasses = []
extraClasses.append('AWIPS2_Core/common/com.raytheon.uf.common.dataquery/src/com/raytheon/uf/common/dataquery/requests/DbQueryRequest.java')
extraClasses.append('AWIPS2_Core/common/com.raytheon.uf.common.serialization.comm/src/com/raytheon/uf/common/serialization/comm/IServerRequest.java')
extraClasses.append('AWIPS2_Core/edex/com.raytheon.uf.edex.requestsrv/src/com/raytheon/uf/edex/requestsrv/RequestServiceExecutor.java')

# These next 3 files must be updated manually
extraClasses.append('AWIPS2_Dev_Baseline/edexOsgi/com.raytheon.uf.common.registry.ebxml/src/com/raytheon/uf/common/registry/ebxml/AssociationQuery.java')
extraClasses.append('AWIPS2_Dev_Baseline/edexOsgi/com.raytheon.uf.common.registry.ebxml/src/com/raytheon/uf/common/registry/ebxml/IdQuery.java')

# ServerPrivilegedRequestHandler.java has a subclass that implements IServerRequest
extraClasses.append('AWIPS2_Core/edex/com.raytheon.uf.edex.requestsrv/src/com/raytheon/uf/edex/requestsrv/request/ServerPrivilegedRequestHandler.java')
