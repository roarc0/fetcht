#!/usr/bin/env python3

import sys, getopt

from fetcht.core import *
from fetcht.utils import *
#from fetcht.gui import *

__program_name__ = "fetcht"
__version__ = '0.6'

import cmd
commands = []
class CmdParse(cmd.Cmd): #TODO port core itself to this cmd structure
	prompt = "> "
	def set_core(self, core):
		self.core = core
		return self
	def onecmd(self, line):
		if self.core is None:
			return
		self.core.process_command(line)
		commands.append(line)
		if self.core.status == False:
			return True

def load_cmd(core, line):
	prompt = True if line in ["",[]] else False
	if prompt:
		CmdParse().set_core(core).cmdloop()
	else:
		core.process_command(line)
		core.status = False

def usage(): # prettytable
	INFO("""Usage:\n
	--help	-h : you already know this one.
	--silent  -s  : verbosity off
	--gui	 -g : load gui
	--cmd	 -c : load command prompt\n
	if none of the above is specified it will try to execute arglist to the database prompt
	""")

def main():
	INFO("{0} v{1} (hexec) GPLv2\n".format(__program_name__, __version__))

	fcore = core()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hsgc", ["help","silent", "gui", "cmd"])
	except getopt.GetoptError as err:
		ERROR(err)
		sys.exit(2)

	verbose = True
	parsed = False
	for o, param in opts:
		parsed = True
		if o in ("-s", "--silent"):
			verbose = False
		elif o in ("-h", "--help"):
			usage()
		#elif o in ("-g", "--gui"):
		#	load_gui(core)
		elif o in ("-c", "--cmd"):
			load_cmd(fcore, "")

	if not parsed:
		load_cmd(fcore, sys.argv[1:])

	fcore.close()

if __name__ == '__main__':
	main();
