import os, re, sqlite3
import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from fetcht.prettyprint import *
from fetcht.fetcht_utils import *
from fetcht.fetcht_io import *

class fetcht_core:

	def __init__(self):
		self.db_path = os.getenv("HOME") + '/.local/hexfiles/db/fetcht.db'
		self.check_pages_num = 5
		self.request_timeout = 30
		self.manual_add = False

		try:
			base_path = os.path.dirname(self.db_path)
			if not os.path.exists(base_path):
				os.mkdir(base_path)

			self.con = sqlite3.connect(self.db_path);
			self.cur = self.con.cursor();
			if not self.table_exists("keyword"):
				print_info("Initializing new database")
				self.init();
		except Exception as e:
			print_err("init -> error opening db: ", str(e));
			self.status = False;
		self.status = True;

	def find_name_by_id(self, id):
		try:
			self.cur.execute("SELECT name FROM keyword WHERE id={0}".format(str(id)));
			res = self.cur.fetchone();
			return res[0]
		except sqlite3.Error as e:
			print_err("find_name_by_id -> sqlite error: ", str(e));
			pass
		except Exception as e:
			print_err("find_name_by_id -> error: ", str(e))
			pass
		return ""

	def table_exists(self, name):
		try:
			self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(name));
			return bool(len(self.cur.fetchall()));
		except sqlite3.Error as e:
			print_err("find_name_by_id -> sqlite error: ", str(e));
			return False

	def find_id_by_name(self, name):
		try:
			self.cur.execute("SELECT id FROM keyword WHERE name LIKE '%{0}%'".format(name));
			res = self.cur.fetchone();
			return res[0]
		except sqlite3.Error as e:
			print_err("find_name_by_id -> sqlite error: ", str(e));
			pass
		except Exception as e:
			print_err("find_name_by_id -> error: ", str(e))
			pass
		return -1

	def get_item(self, value):
		item_id = -1
		item_name = ""
		try:
			if not value.isdigit():
				item_id = self.find_id_by_name(value);
				item_name = self.find_name_by_id(item_id);
				if int(item_id) >=0:
					print_warn("Recognized item \"{0}\" with id={1}".format(item_name, str(item_id)));
			else:
				item_id = value;
				item_name = self.find_name_by_id(item_id);
		except sqlite3.Error as e:
			print_err("get_item -> sqlite error: ", str(e));
			pass
		except Exception as e:
			print_err("get_item -> error: ", str(e))
			pass
		return item_id, item_name

	def check_filter(self, id, item):
		name = magnet_name(item);
		try:
			for row_include in self.cur.execute("SELECT value FROM filter WHERE id={0} AND exclude=0".format(str(id))):
				if row_include[0] not in item:
					print_warn("Filtering out, include reason \"{0}\" not found :\n".format(row_include[0]), str(name) + "\n");
					return False

			for row_exclude in self.cur.execute("SELECT value FROM filter WHERE id={0} AND exclude=1".format(str(id))):
				if row_exclude[0] in item:
					print_warn("Filtering out, exclude reason \"{0}\" found :\n".format(row_exclude[0]), str(name) + "\n");
					return False
		except sqlite3.Error as e:
			print_err("check_filter -> sqlite error: ", str(e))
			print_err(item);
		except Exception as e:
			print_err("check_filter -> error: ", str(e))
			print_err(item);

		return True # Download file

	def check_memory(self, item):
		count=0;
		name = magnet_name(item);
		try:
			for row_memory in self.cur.execute("SELECT * FROM memory WHERE value = '{0}'".format(str(item))):
				count+=1;
			if count == 0:
				print_info("New torrent found:\n", "{0}\n".format(name));
				return True
			else:
				print_warn("Torrent already downloaded:\n", "{0}\n".format(name));
				return False
		except sqlite3.Error as e:
			print_err("check_memory -> sqlite error: ", str(e))
			print_err(item);

	def add_to_memory(self, item):
		try:
			self.cur.execute("INSERT INTO memory VALUES (NULL, '{0}', strftime('%s','now'))".format(str(item)));
			self.con.commit();
		except sqlite3.Error as e:
			print_err("add_to_memory -> sqlite error: ", str(e))
			print_err(item);

	def clean_memory(self, all=False):
		if all:
			self.cur.execute("DELETE FROM memory");
		else:
			self.cur.execute("DELETE FROM memory WHERE (strftime('%s','now') - date) > 15552000");
		self.con.commit();

	def close(self):
		self.clean_memory();
		self.con.close();
		print_info("bye bye!");

	def init(self):
		try:
			self.cur.executescript('''PRAGMA writable_schema = 1;
			delete from sqlite_master where type in ('table', 'index', 'trigger');
			PRAGMA writable_schema = 0;
			VACUUM;
			PRAGMA INTEGRITY_CHECK;
			CREATE TABLE keyword(id INTEGER, name TEXT, date TEXT, source TEXT,
								 enabled BOOLEAN, PRIMARY KEY (id), UNIQUE (name));
			CREATE TABLE memory(id INTEGER, value TEXT, date  INTEGER,
								PRIMARY KEY (id,value));
			CREATE TABLE filter(id INTEGER, value TEXT, exclude BOOLEAN,
								PRIMARY KEY (id,value,exclude));''');
			self.con.commit();
		except sqlite3.Error as e:
			print_err("init -> sqlite error: ", str(e))
			pass

	def query(self, qstring):
		self.cur.execute(str(qstring));
		self.con.commit();

	def insert(self, name, source):
		self.cur.execute("INSERT INTO keyword VALUES (NULL, '{0}', datetime('now'), '{1}', 1)".format(str(name), str(source)));
		self.con.commit();

	def update(self, item_id, key, val):
		self.cur.execute("UPDATE keyword SET {1}='{2}' WHERE id={0}".format(str(item_id), str(key), str(val)));
		self.con.commit();

	def delete(self, item_id):
		self.cur.execute("DELETE FROM keyword WHERE id={0}".format(item_id));
		self.cur.execute("DELETE FROM memory WHERE id={0}".format(item_id));
		self.cur.execute("DELETE FROM filter WHERE id={0}".format(item_id));
		self.con.commit();

	def enable(self, item_id, action):
		self.cur.execute("UPDATE keyword SET enabled='{0}' WHERE id={1}".format(int(bool(action)), str(item_id)));
		self.con.commit();

	def filter(self, item_id, val, exclude):
		self.cur.execute("INSERT INTO filter VALUES ('{0}', '{1}' , {2})".format(str(item_id), str(val), str(int(exclude))));
		self.con.commit();

	def set_source(self, item_id, val):
		self.cur.execute("UPDATE keyword SET source='{1}' WHERE id={0}".format(str(item_id), str(val)));
		self.con.commit();

	def delete_filter(self, item_id, val):
		self.cur.execute("DELETE FROM filter WHERE id={0} AND value=\"{1}\"".format(str(item_id), str(val)));
		self.con.commit();

	def get_filters(self, item_id):
		return self.cur.execute("SELECT value,exclude FROM filter WHERE id={0}".format(str(item_id)))

	def search(self, source):
		return self.cur.execute("SELECT id,name,enabled FROM keyword WHERE source=\"{0}\" ORDER BY name".format(str(source)))

	def list(self, sstring=""):
		return self.cur.execute("SELECT id,name,source,enabled FROM keyword WHERE name LIKE '%{0}%' ORDER BY name".format(sstring))

	def get_cursor(self):
		return self.cur

	def process_item(self, row, current_item, link):
		if len(row) < 3 :
			#print_err("Malformed row: ", str(row))
			return
		check_id , check_item, enabled = row

		if str(check_item).lower().replace("."," ") in str(current_item).lower().replace("."," "):
			if not enabled:
				print_warn("Downloadable but disabled:\n", magnet_name(current_item) + "\n")
			elif self.check_filter(check_id, current_item):
				if self.check_memory(current_item):
					if self.manual_add and (not ask("Do you want to load this torrent?")):
						return
					ret = False;
					if link.startswith("magnet"):
						ret = load_magnet(link);
					else:
						ret = download_file(link, current_item + ".torrent")
					if ret:
						self.add_to_memory(current_item);

	def process_command(self, cmd):
		if type(cmd) is str:
			cmd = cmd.split(" ")
		c = cmd[0]
		try:
			if c in ["exit","quit","e","q"]:
				self.status=False

			elif c in ["help","h","?"]:
				col_names=["Command", "Parameters", "Description"];
				x = PrettyTable(col_names);
				x.align[col_names[1]] = "l"
				x.align[col_names[2]] = "l"
				x.padding_width = 1

				x.add_row(["init","","Inits or resets the database"]);
				x.add_row(["dump","","[TODO] Dumps database to a file."]);
				x.add_row(["schema","","Display database schema"]);
				x.add_row(["query","<query>","[WIP] Execute raw query! warning!"]);
				x.add_row(["clear","","Clear downloaded memory"]);
				x.add_row(["insert","<name> <source>","Insert a new item"]);
				x.add_row(["delete","<id/name>","Delete item by id"]);
				x.add_row(["enable","<id/name>","Enable item"]);
				x.add_row(["disable","<id/name>","Disable item"]);
				x.add_row(["update","<id/name> <property> <value>","Update item's property: {name,date,source,enabled}"]);
				x.add_row(["filter show","<id/name>","Show filters for item"]);
				x.add_row(["filter del","<id/name>","Delete a filter for item"]);
				x.add_row(["exclude","<id/name> <filter_val>","Filters out item containing filter_val."]);
				x.add_row(["include","<id/name> <filter_val>","Requires out item containing filter_val."]);
				x.add_row(["source","<id/name> <source>","Changes source for item"]);
				x.add_row(["prompt","<id/name> <filter_val>","[TODO] Asks to continue if contains filter_val."]);
				x.add_row(["fetch","<pages>","Fetch torrents"]);
				x.add_row(["list","","List currently watched items"]);
				print(x);

			elif c == "init":
				if ask("This will reset the entire database, are you sure?"):
					self.init();

			elif c == "dump":
				print_warn("not yet implemented...")

			elif c in ["insert", "ins", "i"]: #TODO check valid source
				if len(cmd) == 3:
					self.insert(cmd[1], cmd[2]);
					print_info("Inserting \"{0}\" source: {1}. id: {2}".format(cmd[1],cmd[2], self.find_id_by_name(cmd[1])));
				else:
					print("Wrong synthax. use \"insert <name> <source>\"\nname: name of the series. be careful to match the exact name in magnet or link name.\nsource: one of {eztv,horrible,nyaa,pirate}");

			elif c in ["update", "up", "u"]:
				if len(cmd) == 4:
					[item_id, item_name] = self.get_item(cmd[1]);
					self.update(item_id, cmd[2], cmd[3]);
					print_info("Updating \"{0}\" id:{1} -> {2} = {3}".format(item_name, item_id, cmd[2], cmd[3]));
				else:
					print_err("Wrong synthax. use \"update <id/name> <opt> <val>\"");
					print_warn("<opt>: name, enabled, source\"");

			elif c in ["exclude","include"]:
				if len(cmd) == 3:
					action = True if c=="exclude" else False;
					[item_id, item_name] = self.get_item(cmd[1]);
					if int(item_id) >= 0:
						self.filter(item_id, cmd[2], action);
						print_info("New filter for \"{0}\" id:{1} keyword: \"{2}\"".format(item_name, item_id, cmd[2]));
					else:
						print_err("Can't find \"{0}\" in database.".format(cmd[1]));
				else:
					print_err("Wrong synthax. use \"filter <id/name> <val> <0/1>\"");

			elif c in ["source"]:
				if len(cmd) == 3:
					[item_id, item_name] = self.get_item(cmd[1]);
					if int(item_id) >= 0:
						self.set_source(item_id, cmd[2]);
						print_info("New source for \"{0}\" id:{1} source: \"{2}\"".format(item_name, item_id, cmd[2]));
					else:
						print_err("Can't find \"{0}\" in database.".format(cmd[1]));
				else:
					print_err("Wrong synthax. use \"source <id/name> <source>\"");

			elif c == "filter": #TODO table
				if len(cmd) >= 3:
					[item_id, item_name] = self.get_item(cmd[2]);
					if int(item_id) >= 0:
						if cmd[1]=="show":
							print_info("Filters for {0} id:{1} :".format(item_name, item_id));
							col_names=["Value", "Filter Type"];
							x = PrettyTable(col_names);
							x.padding_width = 1

							for row in self.get_filters(item_id):
								if row[1] == 1:
									x.add_row([row[0], "EXCLUDE"]);
								else:
									x.add_row([row[0], "INCLUDE"]);
							print(x)
						elif cmd[1]=="del":
							if len(cmd) == 4:
								self.delete_filter(item_id, cmd[3]);
								print_info("Deleting \"{0}\" filter for \"{1}\" id:{2}".format(cmd[3], item_name, item_id));
							else:
								print_err("Missing extra argument for this action: value to delete.");
						else:
							print_err("Unrecognized \"{0}\" action".format(cmd[1]));
					else:
						print_err("Can't find \"{0}\" in database.".format(cmd[2]));
				else:
					print_err("Wrong synthax. use \"filters (show|del) <id/name> <val>\".\nuse include/exclude command to add new filters.");

			elif c in ["enable", "disable"]:
				if len(cmd) == 2:
					[item_id, item_name] = self.get_item(cmd[1]);
					if int(item_id) >= 0:
						action = True if c=="enable" else False;
						self.enable(item_id, action);
						if action:
							print_info("Enabling \"{0}\" id:{1}".format(item_name, item_id));
						else:
							print_info("Disabling \"{0}\" id:{1}".format(item_name, item_id));
					else:
						print_err("Can't find \"{0}\" id or name in database.".format(cmd[1]));
				else:
					print_err("Wrong synthax. use \"(enable|disable) <id/name>\"")

			elif c in ["delete", "del"]:
				if len(cmd) == 2:
					[item_id, item_name] = self.get_item(cmd[1]);
					self.delete(item_id);
					print_info("Deleting \"{0}\" id:{1} done".format(item_name, item_id));
				else:
					print_err("Wrong synthax. use \"delete <id/name>\"")

			elif c in ["list", "ls", "l"]: #TODO show EXCLUDE{...}, INCLUDE{...}
				if len(cmd) == 2:
					print_info("searching for elements containing \"{0}\"\n".format(cmd[1]));
					search_str = cmd[1];
				else:
					search_str = "";

				for row in self.list(search_str):
					col_names = [cn[0] for cn in self.get_cursor().description]
					rows_ls = self.get_cursor().fetchall()
					x = PrettyTable(col_names)
					x.align[col_names[1]] = "l"
					x.align[col_names[2]] = "r"
					x.padding_width = 1

					count = 0
					for row in rows_ls:
						count+=1
						x.add_row(row)

					if count > 0:
						print (x)
					else:
						print_info("No results!");

			elif c == "schema":
				x = PrettyTable(["Table Name", "Primary Key", "Unique", "Fields"])
				x.padding_width = 1
				x.add_row(["keyword", "id", "name", "id, name, date, source, enabled"]);
				x.add_row(["memory", "id,value", "", "id,value,date"]);
				x.add_row(["filter", "id,value,exclude", "", "id, value,exclude"]);
				print(x);

			elif c == "query": # TODO handle output
				if len(cmd) == 2:
					self.query(cmd[1]);
					print_info("Query executed!");

			elif c in ["clear", "clr"]: #TODO clear last x
				self.clean_memory(True);
				print_info("Memory table cleared");

			elif c in ["fetch", "f"]:
				check_process(torrent_client);
				if len(cmd) > 1 and cmd[1] == "manual":
					self.manual_add = True;
				if len(cmd) > 1 and cmd[1].isdigit():
					print_info("Setting check pages number to {0}".format(cmd[1]))
					self.check_pages_num = int(cmd[1])

				print_info("Checking eztv source...");
				for i in range(0, self.check_pages_num):
					print_info("page #{0}\n".format(i));

					url = "http://eztv-proxy.net/"; #'https://eztv.ag/'
					if i > 0:
						url = "{0}page_{1}".format(url,i);

					try:
						req = Request(url, headers={'User-Agent': 'Mozilla/5.0'});
						data = urlopen(req, None, self.request_timeout).read();
						regexp = re.compile("<a href=\"(magnet.+?)\"");
						magnets = regexp.findall(str(data));

						for magnet in magnets:
							magnet = magnet.strip()
							for row in self.search("eztv"):
								self.process_item(row, magnet, magnet);
					except Exception as e:
						print_err("process_command_eztv -> error : ", str(e))

				print_info("Checking horrible source...");
				url = "http://horriblesubs.info/rss.php?res=720"

				try:
					req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
					data = urlopen(req, None, self.request_timeout).read()
					soup = BeautifulSoup(data, "xml")

					for elem in soup.find_all("item"):
						name = elem.find("title").get_text();
						magnet = elem.find("link").get_text();

						for row in self.search("horrible"):
							self.process_item(row, name, magnet);

						for row in self.search("nyaa"):
							self.process_item(row, name, magnet);
				except Exception as e:
					print_err("process_command_horrible -> error: ", str(e));
					pass

				print_info("Checking piratebay source...");
				for row in self.search("pirate"):
					s_id , s_item, s_enabled = row
					url = "https://pirateproxy.cc/search/{0}/0/3/0".format(s_item);
					try:
						req = Request(url, headers={'User-Agent': 'Mozilla/5.0'});
						data = urlopen(req, None, self.request_timeout).read();

						regexp = re.compile("<a href=\"(magnet.+?)\"");
						magnets = regexp.findall(str(data));

						for magnet in magnets:
							magnet = magnet.strip()
							self.process_item(row, magnet, magnet);
					except Exception as e:
						print_err("process_command_pirate -> error: ", str(e));
						pass

			elif cmd != ['']:
				print_err("process_command -> command not found!\n", "Please, type \"help\" for command list");

		except sqlite3.Error as e:
			print_err("process_command -> sqlite error: ",str(e));
			pass
		except Exception as e:
			print_err("process_command -> error: ", str(e));
