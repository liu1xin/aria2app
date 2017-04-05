#!/usr/bin/env python

# -*- coding: utf8 -*-

import aria2app.a2jsonrpc as a2jsonrpc

######################## Convenience Methods for Client#############################


################################### Main for Test###################################

def main(args=None):
    uri = "http://localhost:6800/jsonrpc"
    token = '11111111'
  
    ajclient = a2jsonrpc.Aria2JsonRpcClient('test', uri, token)

    version = ajclient.getVersion()
    print('version: {}'.format(version['version']))
    print('enabled features:')
    for f in version['enabledFeatures']:
      print(' ', f)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass