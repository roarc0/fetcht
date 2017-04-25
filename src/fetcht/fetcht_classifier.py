import re

def parse_tv(name):
	tv = re.findall(r"""(.*)[ .][Ss](\d{1,2})[Ee](\d{1,2})[ .a-zA-Z]*(\d{3,4}p)?""", name, re.VERBOSE)

	new_name= "{1}-S{2}E{3}".format(name, str(tv[0][0]).replace(".", " "), str(tv[0][1]), str(tv[0][2]));
	return new_name, tv[0]

def parse_movie(name):
	movie = re.findall(r"""(.*?[ .]\d{4})[ .a-zA-Z]*(\d{3,4}p)?""", name, re.VERBOSE)
	return movie[0]
