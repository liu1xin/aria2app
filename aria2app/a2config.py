#!/usr/bin/env python

# -*- coding: utf8 -*-


import ConfigParser
import os.path as op


DEFAULT_CFG = "/etc/a2app/config.conf"


class Aria2Config(object):
    
    def __init__(self, cfgfile=DEFAULT_CFG):
        a2conf = ConfigParser.ConfigParser(allow_no_value=True)
        if op.exists(cfgfile) and op.isfile(cfgfile):
            rf = a2conf.read(cfgfile)
            if not rf:
                return None
        else:
            return None
        
        self.a2conf = a2conf
        self.cfgfile = cfgfile
        
    def getcfgbysection(self, section='DEFAULT'):
        return dict(self.a2conf.items(section))

    def getcfgbyname(self, section, keyname):
        return self.a2conf.get(section, keyname)

    def seta2config():
        pass

    def savea2config():
        pass


################################### Main for Test###################################

def main(args=None):
    cfgfile = "/home/liuyx/aapp/app/a2config.cnf"
    
    config = Aria2Config(cfgfile)

    dft = config.getcfgbysection()
    print("get len %d" % len(dft))
    for f in dft:
      print(f)
      
    address= config.getcfgbyname('RPC', 'address')
    print(address)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass