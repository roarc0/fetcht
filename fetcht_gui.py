import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from prettyprint import *
from fetcht_core import *

guiTitle = "fetcht v0.4"

class FetchtWindow(Gtk.Window):
    def __init__(self, core):
        Gtk.Window.__init__(self, title=guiTitle)
        self.set_border_width(10)
        self.core = core

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.item_liststore = Gtk.ListStore(int, str, str, bool)
        item_list = core.list()
        print(item_list)
        for item_ref in item_list:
            self.item_liststore.append(list(item_ref))
        self.current_filter_source = None


        self.source_filter = self.item_liststore.filter_new()
        self.source_filter.set_visible_func(self.source_filter_func)

        self.treeview = Gtk.TreeView.new_with_model(self.source_filter)
        for i, column_title in enumerate(["ID", "Name", "Source", "Enabled"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        self.buttons = list()
        for name in ["eztv", "nyaa", "showrss"]:
            button = Gtk.Button(name)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def source_filter_func(self, model, iter, data):
        """Tests if the source in the row is the one in the filter"""
        if self.current_filter_source is None or self.current_filter_source == "None":
            return True
        else:
            return model[iter][2] == self.current_filter_source

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        self.current_filter_source = widget.get_label()
        print_info("%s selected!" % self.current_filter_source)
        self.source_filter.refilter()

def load_gui(core):
    print_info("Loading gui");
    win = FetchtWindow(core)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
