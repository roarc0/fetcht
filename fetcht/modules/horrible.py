import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from fetcht.utils import *

def __main__(core):
	INFO("Checking horrible source...")
	url = "http://horriblesubs.info/rss.php?res=720"

	try:
		req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		data = urlopen(req, None, core.request_timeout).read()
		soup = BeautifulSoup(data, "xml")

		for elem in soup.find_all("item"):
			name = elem.find("title").get_text()
			magnet = elem.find("link").get_text()

			for row in core.search("horrible"):
				core.process_item(row, name, magnet)

			for row in core.search("nyaa"):
				core.process_item(row, name, magnet)
	except Exception as e:
		ERROR("process_command_horrible -> error: ", str(e))
		pass
