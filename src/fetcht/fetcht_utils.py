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
