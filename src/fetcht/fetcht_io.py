import sys, os, subprocess
import urllib
from urllib.request import Request, urlopen
from time import sleep

from fetcht.fetcht_utils import *
from fetcht.fetcht_conf import *
from fetcht.prettyprint import *

dl_path = os.getenv("HOME")

def daemonize(name):
	"""UNIX double fork mechanism."""
	try:
		pid = os.fork()
		if pid > 0:
			return # exit first parent
	except OSError as err:
		sys.stderr.write('fork #1 failed: {0}\n'.format(err))
		sys.exit(1)

	os.chdir('/') # decouple from parent environment
	os.setsid()
	os.umask(0)

	try:
		pid = os.fork() # do second fork
		if pid > 0:
			sys.exit(0) # exit from second parent
	except OSError as err:
		sys.stderr.write('fork #2 failed: {0}\n'.format(err))
		sys.exit(1)

	sys.stdout.flush() # redirect standard file descriptors
	sys.stderr.flush()
	si = open(os.devnull, 'r')
	so = open(os.devnull, 'a+')
	se = open(os.devnull, 'a+')

	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())
	os.spawnlp(os.P_NOWAIT, name, name)

def check_process(name):
	ps= subprocess.Popen("ps -A | awk '/" + name + "/{print \"1\";exit}'",
						  shell=True, stdout=subprocess.PIPE)
	output = ps.stdout.read()
	ps.stdout.close()
	ps.wait()
	if  output != b'1\n':
		load_process(name);
		check_process(name);
	else:
		print_info("Process {0} is running!".format(name));
	
def load_process(name):
	print_err("Process not running, loading {0}!".format(name))
	daemonize(name)
	sleep(1)

def execute(command):
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE);
	output, errors = p.communicate();
	return str(output.decode("ascii"));

def load_magnet(self, magnet):
	execute("({0} \"{1}\") > /dev/null".format(self.get_conf('torrentcmd'), magnet));
	return True

def magnet_name(magnet):
	if not magnet.startswith('magnet'):
		return magnet
	else:
		return urllib.parse.unquote(find_between(magnet, "&dn=", "&"))

def download_file(url, filename):
	try:
		with urllib.request.urlopen(url) as response, open(os.getenv("HOME") + '/' + filename, 'wb') as outf:
			outf.write(response.read());
			outf.close();
	except Exception as e:
		print_err("download_file -> error downloading file: ", str(e));
		pass;
		return False

	return True
