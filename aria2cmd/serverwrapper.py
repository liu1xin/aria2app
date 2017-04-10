#!/usr/bin/env python

# -*- coding: utf8 -*-


import aria2app.a2jsonrpc as a2jsonrpc
import aria2app.a2config as a2config

######################## Convenience Methods for Server#############################

class Aria2ServerWrapper(object):

    def __init__(self, cfgfile, token=None):
        self.token = token
        self.server = a2jsonrpc.Aria2JsonRpcServer(token)
        self.config = a2config.Aria2Config(cfgfile)
        
    def startA2Server(self, restart=False):
        cmd = []
        
        # set default config
        defaults = self.config.getcfgbysection('DEFAULT')
        dir = defaults.get('storedir', '')
        cmd.append('--dir=%s' % dir)
        logfile = defaults.get('logfile', None)
        loglevel = defaults.get('loglevel', 'info')
        if logfile:
            cmd.append('--log=%s' % logfile)
            cmd.append('--log-level=%s' % loglevel)
        maxdownloads = defaults.get('maxconcurrentdownloads', 10)
        maxdownlimit = defaults.get('maxoveralldownloadlimit', '10M')
        maxuploadlimit = defaults.get('maxoveralluploadlimit', '10M')
        cmd.append('--max-concurrent-downloads=%d' % int(maxdownloads))
        cmd.append('--max-overall-download-limit=%s' % maxdownlimit)
        cmd.append('--max-overall-upload-limit=%s' % maxuploadlimit)
        cache = defaults.get('cache', '32M')
        fileallocation = defaults.get('fileallocation', 'falloc')
        cmd.append('--disk-cache=%s' % cache)
        cmd.append('--file-allocation=%s' % fileallocation)

        # set rpc config
        rpcs = self.config.getcfgbysection('RPC')
        cmd.append('--enable-rpc=true')
        cmd.append('--rpc-listen-all=true')
        cmd.append('-D')
        if self.token:
            cmd.append('--rpc-secret=%s' % self.token)
        else:
            token = rpcs.get('token', 'abcdef098')
            cmd.append('--rpc-secret=%s' % token)
            self.token = token
        port = rpcs.get('port', '6800')
        cmd.append('--rpc-listen-port=%s' % port)
                
        self.server.setextendcmd(cmd)
        ret = self.server.start(restart)

def stopA2():
    pass
    
    
################################### Main for Test###################################

def main(args=None):
    token = '11111111'
  
    ajserver = a2jsonrpc.Aria2JsonRpcServer(token)
    ret = ajserver.start(restart=True)
    print('start ajserver %d' % ret)
    
    ajserver.stop()
    
def main1(args=None):
    a2server = Aria2ServerWrapper("/home/liuyx/aapp/app/a2config.cnf")
    a2server.startA2Server()

if __name__ == '__main__':
  try:
    main1()
  except KeyboardInterrupt:
    pass