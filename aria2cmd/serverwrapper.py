#!/usr/bin/env python

# -*- coding: utf8 -*-


import aria2app.a2jsonrpc as a2jsonrpc


######################## Convenience Methods for Client#############################


################################### Main for Test###################################

def main(args=None):
    token = '11111111'
  
    ajserver = a2jsonrpc.Aria2JsonRpcServer(token)
    ret = ajserver.start(restart=True)
    print('start ajserver %d' % ret)
    
    ajserver.stop()
    

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass