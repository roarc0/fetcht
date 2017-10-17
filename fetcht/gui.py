import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from fetcht.core import *
from fetcht.gui_add import *
from fetcht.utils import *

guiTitle = "fetcht"

class FetchtWindow(Gtk.Window):
	def __init__(self, core):
		self.core = core
		Gtk.Window.__init__(self, title=guiTitle)

		self.set_border_width(10)
		self.set_default_size(800, 600)

		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = guiTitle
		self.set_titlebar(hb)

		#button = Gtk.Button()
		#icon = Gio.ThemedIcon(name="settings")
		#image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		#button.add(image)
		#hb.pack_end(button)

		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		Gtk.StyleContext.add_class(box.get_style_context(), "linked")

		button = Gtk.Button("Add")
		icon = Gio.ThemedIcon(name="list-add")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.connect("clicked", self.on_add_button_clicked)
		box.add(button)

		button = Gtk.Button("Remove")
		icon = Gio.ThemedIcon(name="list-remove")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.connect("clicked", self.on_remove_button_clicked)
		box.add(button)

		#button = Gtk.Button()
		#button.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
		#box.add(button)

		hb.pack_start(box)

		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(False)
		self.grid.set_row_homogeneous(False)
		self.add(self.grid)

		self.item_liststore = Gtk.ListStore(int, str, str, bool)
		self.item_list = core.list()
		for item_ref in self.item_list:
			self.item_liststore.append(list(item_ref))

		self.current_filter_source = "all"
		self.current_filter_name = ""
		self.filter = self.item_liststore.filter_new()
		self.filter.set_visible_func(self.filter_func)

		self.treeview = Gtk.TreeView.new_with_model(self.filter)
		for i, column_title in enumerate(["ID", "Name", "Source", "Enabled"]):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			self.treeview.append_column(column)

		self.buttons = list()
		for name in ["all", "eztv", "nyaa", "pirate"]:
			button = Gtk.Button(name)
			self.buttons.append(button)
			button.connect("clicked", self.on_selection_button_clicked)

		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)
		self.grid.attach(self.scrollable_treelist, 0, 0, 5, 10)

		self.labelFilterName = Gtk.Label("Filter name")
		self.grid.attach_next_to(self.labelFilterName, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
		self.entryFilter = Gtk.Entry()
		self.entryFilter.connect("changed", self.on_entry_filter_changed)
		self.grid.attach_next_to(self.entryFilter, self.labelFilterName, Gtk.PositionType.RIGHT, 1, 1)

		self.labelFilterSource = Gtk.Label("Filter source")
		self.grid.attach_next_to(self.labelFilterSource, self.labelFilterName, Gtk.PositionType.BOTTOM, 1, 1)
		self.grid.attach_next_to(self.buttons[0], self.labelFilterSource, Gtk.PositionType.RIGHT, 1, 1)
		for i, button in enumerate(self.buttons[1:]):
			self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
		self.scrollable_treelist.add(self.treeview)

		self.show_all()

	def filter_func(self, model, iter, data):
		"""Tests the filters"""
		if self.current_filter_source != "all" and model[iter][2] != self.current_filter_source:
			return False
		if self.current_filter_name.lower() not in model[iter][1].lower():
			return False
		return True

	def on_entry_filter_changed(self, widget):
		"""Called on any change of entryFilter"""
		self.current_filter_name = widget.get_text()
		self.filter.refilter()

	def on_selection_button_clicked(self, widget):
		"""Called on any of the button clicks"""
		self.current_filter_source = widget.get_label()
		self.filter.refilter()

	def on_remove_button_clicked(self, widget):
		"""Called add button clicks"""
		model, treeiter = self.treeview.get_selection().get_selected()
		if treeiter != None:
		   self.core.delete(model[treeiter][0])
		   for row in self.item_liststore:
			   if row[0] == model[treeiter][0]:
				   self.item_liststore.remove(row.iter)
				   break

	def on_add_button_clicked(self, widget):
		"""Called add button clicks"""
		dialog = AddDialog(self)
		response = dialog.run()

		if response == Gtk.ResponseType.OK and (not dialog.source_str is None) and ( not dialog.name_str is None or dialog.name_str == ""):
			self.core.insert(dialog.name_str, dialog.source_str)
			item_id = self.core.find_id_by_name(dialog.name_str)
			self.item_liststore.append(list([int(item_id), dialog.name_str, dialog.source_str, True]))

		dialog.destroy()

def load_gui(core):
	print_info("Loading gui");
	win = FetchtWindow(core)
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
