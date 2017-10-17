verbose = True

class PrettyPrint:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

def DEBUG(header, message=""):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.OKGREEN + header + PrettyPrint.ENDC + message)

def INFO(header, message=""):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.OKBLUE + header + PrettyPrint.ENDC + message)

def WARN(header, message=""):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.WARNING + header + PrettyPrint.ENDC + message)

def ERROR(header, message="" ):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.FAIL + header + PrettyPrint.ENDC + message)

def ask(what):
	res = input("{0} (y/N) ".format(what))
	if res == "yes" or res == "y":
	  return True
	else:
	  return False

def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
