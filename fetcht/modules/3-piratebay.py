from urllib.request import Request, urlopen
import re
import ssl
import random
from fetcht.utils import *

def __main__(core):
	INFO("Checking piratebay source...")
	urls = ['https://thepiratebay.org', 'https://pirateproxy.cc', 'https://pirateproxy.gdn', 'https://tpbproxy.online', 'https://thepiratebay.vip' ]
	random.shuffle(urls)
	current = 0
	context = ssl._create_unverified_context()
	regexp = re.compile("<a href=\"(magnet.+?)\"")
	for row in core.search("pirate"):
		for i in range(0, core.npages):
			failed = 0
			while failed <= (len(urls) * 5):
				try:
					if len(row) != 3:
						break
					s_id , s_item, s_enabled = row
					url = "{0}/search/{1}/{2}/3/0".format(urls[current], s_item, i)
					INFO("url {0}".format(url))

					req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'})
					data = urlopen(req, None, core.request_timeout, context=context).read()
					magnets = regexp.findall(str(data))

					for magnet in magnets:
						magnet = magnet.strip()
						core.process_item(row, magnet, magnet)
				except Exception as e:
					ERROR("process_command_pirate -> error: " + str(e) + "\n")
					current = (current + 1) % len(urls)
					failed += 1
					pass

				break
