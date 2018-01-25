from urllib.request import Request, urlopen
import re

from fetcht.utils import *

def __main__(core):
	INFO("Checking piratebay source...")
	urls = ['https://thepiratebay.org', 'https://1-thepiratebay.bypassed.st', 'https://2-thepiratebay.bypassed.st', 'https://3-thepiratebay.bypassed.st', 'https://pirateproxy.cc' ]
	current = 0
	for row in core.search("pirate"):
		failed = 0
		for i in range(0, core.npages):	
			while failed <= (len(urls) * 2):
				try:
					if len(row) != 3:
						continue
					s_id , s_item, s_enabled = row
					url = "{0}/search/{1}/{2}/3/0".format(urls[current], s_item, i)
					INFO("url {0}".format(url))

					req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'})
					data = urlopen(req, None, core.request_timeout).read()

					regexp = re.compile("<a href=\"(magnet.+?)\"")
					magnets = regexp.findall(str(data))

					for magnet in magnets:
						magnet = magnet.strip()
						core.process_item(row, magnet, magnet)
					
					failed = 0
					break

				except Exception as e:
					ERROR("process_command_pirate -> error: " + str(e) + "\n")
					current = (current + 1) % len(urls)
					failed += 1
					pass
