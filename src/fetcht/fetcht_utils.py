def ask(what):
	res = input("{0} (y/N) ".format(what))
	if res == "yes" or res == "y":
	  return True
	else:
	  return False
