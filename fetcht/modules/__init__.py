from os.path import dirname, basename, isfile
import glob

def load(self):
    for name in __all__:
      try:
        obj = __import__(name, globals=globals(), locals={}, fromlist=[], level=1)
        getattr(obj, '__main__', lambda: None)(self)
      except ImportError:
        sys.stderr.write("error importing module: " + name + "\n")
        pass

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py') ]
