import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class AddDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        self.set_border_width(6)

        box = self.get_content_area()
        box.set_spacing(4)

        self.label = Gtk.Label("Type name and select source")
        box.add(self.label)

        self.name_entry = Gtk.Entry()
        self.name_entry.connect("changed", self.on_name_entry_changed)
        box.add(self.name_entry)
        
        source_store = Gtk.ListStore(str)
        sources = ["eztv", "nyaa", "showrss"]
        for source in sources:
            source_store.append([source])

        self.source_combo = Gtk.ComboBox.new_with_model(source_store)
        self.source_combo.connect("changed", self.on_source_combo_changed)
        
        renderer_text = Gtk.CellRendererText()
        self.source_combo.pack_start(renderer_text, True)
        self.source_combo.add_attribute(renderer_text, "text", 0)
        
        self.source_combo.set_active(0)
        
        box.add(self.source_combo)

        self.show_all()

    def on_source_combo_changed(self, widget):
        tree_iter = self.source_combo.get_active_iter()
        if tree_iter != None:
            model = self.source_combo.get_model()
            self.source_str = model[tree_iter][0]

    def on_name_entry_changed(self, widget):
        self.name_str = self.name_entry.get_text()
