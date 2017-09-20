import os, json, logging

class jconfig(object):
    __instance = None
    cfg = None
    fname = None
    def __new__(cls, val):
        if jconfig.__instance is None:
            jconfig.__instance = object.__new__(cls)
        jconfig.__instance.val = val
        return jconfig.__instance

    def __init__(self, fname):
        self.log = logging.getLogger('jconfig')
        self.fname = fname
        self.load()

    def get(self, key):
        return self.cfg[key]

    def set(self, key, val):
        self.cfg[key] = val

    def load(self):
        self.log.info('loading config %s' % self.fname)
        try:
            with open(self.fname) as config_file:
                self.cfg = json.load(config_file)
        except Exception as e:
            self.log.warn("{} ".format(self.fname) + str(e))
            return False
        return True

    def save(self):
        self.log.info('saving config %s' % self.fname)
        try:
            with open(self.fname, 'w') as config_file:
                json.dump(self.cfg, config_file, sort_keys=True, indent=2, separators=(',', ': '))
        except Exception as e:
            self.log.warn("error writing {} : ".format(self.fname) + str(e))
            return False
        return True

