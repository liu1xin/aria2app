#!/usr/bin/env python

# -*- coding: utf8 -*-


import base64
import logging
import httplib
import json
import subprocess
import sys
import time
import urllib2


SERVER_URI_FORMAT = '{}://{}:{:d}/jsonrpc'


class Aria2JsonRpcError(Exception):

    def __init__(self, msg):
        super(self.__class__, self).__init__(self, msg)
    
class Aria2JsonRpcServer(object):
    
    ''' Manage starting and stopping Aria2 RPC server. '''
    def __init__(self, token, timeout=30,
                 scheme='http', host='localhost', port=6800, quiet=True):        
        
        self.cmd = ['aria2c']
        self.token = token
        self.timeout = timeout
        self.scheme = scheme
        self.host = host
        self.port = port
        self.quiet = quiet
        self.process = None
        self.client = None
    
    def setextendcmd(self, cmdpara):
        self.cmd.extend(cmdpara)
        
    def getallcmd(self):
        return self.cmd
    
    def start(self, restart=False):
        # logging info
        
        if self.process and self.client:
            launched = True
            try:
                self.client.getVersion()
            except Aria2JsonRpcError as e:
                launched = False
        else:
            launched = False
        
        # need restart
        if launched and restart:
            self.stop()
        elif launched:
            return True

        if self.quiet:
            self.process = subprocess.Popen(self.cmd, stdout=file('/dev/null'))
        else:
            self.process = subprocess.Popen(self.cmd, stdout=sys.stderr)
        print(self.process)
        
        uri = SERVER_URI_FORMAT.format(self.scheme, self.host, self.port)
        self.client = Aria2JsonRpcClient('server', uri, token=self.token)
        timeout = time.time() + self.timeout
      
        # Wait for the server to start listening.
        while True:
            try:
                self.client.getVersion()
            except Aria2JsonRpcError as e:                
                time.sleep(1)
                if time.time() > timeout:
                    return False
            else:
                return True
    
    def stop(self, force=False):
        # logging info
        
        if self.process is None:
            return True
        
        self.client.shutdown()
        time.sleep(5)
        if force:
            self.client.forceShutdown()
        
        try:
            self.process.terminate()
            self.process.kill()
            exit_code = self.process.wait()
        except:
            # logging error
            pass
        
        # logging info
        self.process = None

        return True

class Aria2JsonRpcClient():
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
        except urllib2.URLError as e:
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
