from urllib.request import Request, urlopen
import re

from fetcht.utils import *

def __main__(core):
	INFO("Checking eztv source...")
	urls = [ 'https://eztv.ag/', 'http://eztv-proxy.net/']
	current = 0
	for i in range(0, core.npages):	
		while True:
			url = urls[current]
			INFO("page #{0} -> {1}\n".format(i, url))
			if i > 0:
				url = "{0}page_{1}".format(urls[current], i)
			try:
				req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
				data = urlopen(req, None, core.request_timeout).read()
				regexp = re.compile("<a href=\"(magnet.+?)\"")
				magnets = regexp.findall(str(data))

				for magnet in magnets:
					magnet = magnet.strip()
					for row in core.search("eztv"):
						core.process_item(row, magnet, magnet)
				break
			except Exception as e:
				ERROR("process_command_eztv -> error : ", str(e))
				current = (current + 1) % len(urls)
