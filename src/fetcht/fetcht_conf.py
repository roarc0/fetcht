import os, configparser

def load_config(self):
	try:
		if not os.path.exists(self.cfg_path):
			os.makedirs(self.cfg_path)
		
		self.cfg = configparser.ConfigParser()
		if not os.path.exists(self.cfg_file):
			self.cfg['fetcht'] = { 'torrentcmd':'deluge' };
			with open(self.cfg_file, 'w') as configfile:
				self.cfg.write(configfile)
		else:
			self.cfg.read_file(open(self.cfg_file))
	except Exception as e:
		print_err("config error: ", str(e))
		sys.exit(1)

def get_conf(self, param):
	return self.cfg.get('fetcht', str(param))
