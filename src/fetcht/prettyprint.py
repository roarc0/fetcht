verbose = True

class PrettyPrint:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

def print_debug(header, message=""):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.OKGREEN + header + PrettyPrint.ENDC + message);

def print_info(header, message=""):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.OKBLUE + header + PrettyPrint.ENDC + message);

def print_warn(header, message=""):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.WARNING + header + PrettyPrint.ENDC + message);

def print_err(header, message="" ):
	if verbose:
		print(PrettyPrint.HEADER + "*** " + PrettyPrint.FAIL + header + PrettyPrint.ENDC + message);

