#!/usr/bin/env python

# -*- coding: utf8 -*-


import base64
import logging


class Aria2JsonRpcError(Exception):

    def __init__(self, msg):
        super(self.__class__, self).__init__(self, msg)
    
class Aria2RpcServer(object):
    
    ''' Manage starting and stopping Aria2 RPC server. '''
    def __init__(self, cmd, token, port, ID, a2jr_kwargs=None,
                 timeout=10, scheme='http', host='localhost', nice=True, lock=None,
                 quiet=True):        
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    

class Aria2JsonRcpClient():
    '''
      Client class for interacting with Aria2 RPC server.
    '''
    
    def __init__(self, ID, uri, token=None):
        self.id = ID
        self.uri = uri
        self.token = token
        
    def _init_params(self, value=None, secret=True):
        
        params = []
        
        if secret and self.token is not None:
            token_str = 'token:{}'.format(self.token)
            params.append(token_str)
            
        if value is not None:
            params.append(value)
        
        return params
    
    def _add_more_options(self, params, options=None):
        if options is not None:
            return params.append(options)
    
    def _send_request(self, req_obj):
        request = json.dumps(req_obj).encode('UTF-8')
        client = urllib2.urlopen(self.uri, request)
        response = json.loads(client.read().decode())
        return response
    
    def _add_postion(self, params, position=None):
        if isinstance(position, int) and position >= 0:
            return params.append(position)
      
    def jsonrpccall(self, method, params=None, prefix='aria2.'):

        if not params and prefix == 'system.':
            params = self._init_params(secret=False)
        elif not params:
            params = self._init_params()

        reqjson = {'jsonrpc' : '2.0',
                   'id' : self.id,
                   'method' : prefix + method,
                   'params' : params}
        
        # logging.debug input
        
        try:
            repjson = self._send_request(reqjson)
        except httplib.BadStatusLine as e:
            raise Aria2JsonRpcError(str(e))      
        
        # logging debug output
        if repjson is not None:
            try:
                return repjson['result']
            except KeyError:
                raise Aria2JsonRpcError('unexpected result: {}'.format(repjson))      
      
    ######## Methods in RPC INTERFACE ########
    
    def addUri(self, uris, options=None, position=None):
        
        params = self._init_params(uris)
        params = self._add_more_options(params, options)
        params = self._add_postion(params, position)
        
        return self.jsonrpccall('addUri', params)
    
    def addTorrent(self, torrnet, uris=None, options=None, position=None):
        
        with open(torrnet, 'r') as ftor:
            tor = base64.b64encode(ftor.read())
            
        params = self._init_params(tor)
        if uris:
            params.append(uris)
        params = add_more_options(params, options)
        params = self._add_postion(params, position)

        return self.jsonrpccall('addTorrent', params)
    
    def addMetalink(self, metalink, options=None, position=None):
    
        with open(metalink, 'r') as fmet:
            met = base64.b64encode(fmet.read())
            
        params = self._init_params(met)
        params = self._add_more_options(params, options)
        params = self._add_postion(params, position)

        return self.jsonrpccall('addTorrent', params)
    
    def remove(self, gid):
        
        return self.jsonrpccall('remove', self._init_params(gid))
    
    def forceRemove(self, gid):
        
        return self.jsonrpccall('forceRemove', self._init_params(gid))
    
    def pause(self, gid):

        return self.jsonrpccall('pause', self._init_params(gid))
    
    def pauseAll(self):
        
        return self.jsonrpccall('pauseAll')
    
    def forcePause(self, gid):
        
        return self.jsonrpccall('forcePause', self._init_params(gid))
    
    def forcePauseAll(self):
        
        return self.jsonrpccall('forcePauseAll')
        
    def unpause(self, gid):
        
        return self.jsonrpccall('unpause', self._init_params(gid))
    
    def unpauseAll(self):
        
        return self.jsonrpccall('unpauseAll')
    
    def tellStatus(self, gid, key=None):
        
        params = self._init_params(gid)
        if keys:
            params = self._add_more_options(params, key)
    
        return self.jsonrpccall('tellStatus', params)
    
    def getUris(self, gid):
        
        return self.jsonrpccall('getUris', self._init_params(gid))
    
    def getFiles(self, gid):
        
        return self.jsonrpccall('getFiles', self._init_params(gid))
        
    def getPeers(self, gid):
        
        return self.jsonrpccall('getPeers', self._init_params(gid))
    
    def getServers(self, gid):
        
        return self.jsonrpccall('getServers', self._init_params(gid))
    
    def tellActive(self, keys=None):
        pass
    
    def tellWaiting(self, offset, num, keys=None):
        pass
    
    def tellStopped(self, offset, num, keys=None):
        pass
    
    def changePosition(self, gid, pos, how):        
        pass
    
    def changeUri(self, gid, fileIndex, delUris, addUris, position=None):
        pass
    
    def getOption(self, gid):
        
        return self.jsonrpccall('getOption', self._init_params(gid))
    
    def changeOption(self, gid, options):

        params = self._init_params(gid)
        params = self._add_more_options(params, options)
        
        return self.jsonrpccall('changeOption', params)
    
    def getGlobalOption(self):
        
        return self.jsonrpccall('getGlobalOption')
    
    def changeGlobalOption(self, options):
        
        return self.jsonrpccall('changeGlobalOption', self._init_params(options))
    
    def getGlobalStat(self):
        
        return self.jsonrpccall('getGlobalStat')
    
    def purgeDownloadResult(self):
        
        return self.jsonrpccall('purgeDownloadResult')
    
    def removeDownloadResult(self, gid):
        
        return self.jsonrpccall('removeDownloadResult', self._init_params(gid))
    
    def getVersion(self):
        
        return self.jsonrpccall('getVersion')
    
    def getSessionInfo(self):
        
        return self.jsonrpccall('getSessionInfo')
    
    def shutdown(self):
        
        return self.jsonrpccall('shutdown')
    
    def forceShutdown(self):
        
        return self.jsonrpccall('forceShutdown')
    
    def saveSession(self):
        
        return self.jsonrpccall('saveSession')
    
    def multicall(self, methods):
        
        return self.jsonrpccall('multicall', [methods], prefix='system.')
    
    def listMethods(self):
        
        return self.jsonrpccall('listMethods', prefix='system.')
    
    def listNotifications(self):
        
        return self.jsonrpccall('listNotifications', prefix='system.')
