import sys, os, subprocess
import urllib
from urllib.request import Request, urlopen
from time import sleep

from fetcht.utils import *
from fetcht.jconfig import *

dl_path = os.getenv("HOME")

def check_process(name):
	ps = subprocess.Popen("ps -ax | awk '/" + name + "/{print \"1\";exit}'",
						  shell=True,
						  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output = ps.stdout.read()
	ps.stdout.close()
	ps.wait()
	if  output != b'1\n':
		ERROR("Process not running, loading {0}!".format(name))
		daemonize(name)
		sleep(1)

def execute(command):
	ps = subprocess.Popen(command, shell=True,
						stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, errors = ps.communicate()
	return ps.returncode

def load_torrent(torrentcmd, link, item):
	if link.startswith("magnet"):
		return load_magnet(torrentcmd, link)
	else:
		return download_file(link, item + ".torrent")

def load_magnet(torrentcmd, magnet):
	return execute("({0} \"{1}\") > /dev/null".format(torrentcmd, magnet))

def get_magnet_name(data):
	if not data.startswith('magnet'):
		return data
	else:
		return urllib.parse.unquote(find_between(data, "&dn=", "&"))

# TODO dowload dir variable
def download_file(url, filename):
	try:
		with urllib.request.urlopen(url) as response, open(os.getenv("HOME") + '/' + filename, 'wb') as outf:
			outf.write(response.read())
			outf.close()
	except Exception as e:
		ERROR("download_file -> error downloading file: ", str(e))
		pass
		return False

	return True

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
