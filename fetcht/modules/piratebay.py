from urllib.request import Request, urlopen
import re

from fetcht.utils import *

def __main__(core):
	INFO("Checking piratebay source...")
	for row in core.search("pirate"):
		try:
			if len(row) != 3:
				continue
			s_id , s_item, s_enabled = row
			url = "https://pirateproxy.cc/search/{0}/0/3/0".format(s_item)

			req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
			data = urlopen(req, None, core.request_timeout).read()

			regexp = re.compile("<a href=\"(magnet.+?)\"")
			magnets = regexp.findall(str(data))

			for magnet in magnets:
				magnet = magnet.strip()
				core.process_item(row, magnet, magnet)
		except Exception as e:
			ERROR("process_command_pirate -> error: ", str(e))
			pass
