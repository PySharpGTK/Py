from gi import require_version
require_version("Gtk", "3.0")
from argparse import ArgumentParser
from json import load
from threading import Thread
from gi.repository import Gtk
from libs import networking


server = networking.Server()

class Objects:
    Label  = Gtk.Label
    Button = Gtk.Button
    Box    = Gtk.Box
    Entry  = Gtk.Entry

class Constants:
    class SupportedLayouts:
        Box = Objects.Box
    class EventEnabled:
        Button = Objects.Button
    class EntryEnabled:
        Entry  = Gtk.Entry


class BaseWindow(Gtk.Window):
    def __init__(
        self,
        name = "BaseWindow",
        config = {},
        server = None
    ) -> None:
        super().__init__(
            title="BaseWindow"
        )
        self.set_border_width(10)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.vbox.set_homogeneous(False)
        self.add(self.vbox)
        server.window = self
        self.server = server
        self.TransmutableObjects = {}
        self.loadOwnProperties(
            config
        )
        # Tell the server our context
        _ = {}
        for key in self.TransmutableObjects:
            _[key] = self.TransmutableObjects[key].__class__.__name__
        self.server.send(
            {
                "type": "ctx",
                "data": _
            }
        )
        print(self.TransmutableObjects)

    def loadOwnProperties(
        self,
        config
    ):
        # Loop over every key and category
        for _object in config["Objects"]:
            if _object["type"] in Objects.__dict__:

                _rebuilt_args = self.rebuild_args(_object["args"])

                self.process_object(_object, _rebuilt_args)

    def update(self, component):
        print(component)
        obj = self.TransmutableObjects[component["id"]]
        obj.set_label(component["data"])
    

    def process_object(self, _object, _rebuilt_args, target=None):
        if target == None: target = self.vbox

        if _object["type"] in Constants.SupportedLayouts.__dict__:
            _new_object = Objects.__dict__[_object["type"]](
                **_rebuilt_args
            )
            for child in _object["children"]:
                self.process_child(_new_object, child)
        elif _object["type"] in Constants.EventEnabled.__dict__:
            _new_object = Objects.__dict__[_object["type"]](
                **_rebuilt_args
            )
            _new_object.server = self.server
            _new_object.id     = _object["id"]
            def __internal__(_):
                print("Current queue:", _.server.queue)
                _.server.send(
                    {
                        "id":_.id,
                        "type":type(_).__name__
                    }
                )
                print("New queue:", _.server.queue)
            _new_object.connect("clicked", __internal__)
        elif _object["type"] in Constants.EntryEnabled.__dict__:
            _new_object = Objects.__dict__[_object["type"]](
                **_rebuilt_args
            )
            _new_object.server = self.server
            _new_object.id     = _object["id"]
            def __internal_changed__(_):
                print("Text changed to:", _.get_text())
                print("Current queue:", _.server.queue)
                _.server.send(
                    {
                        "id":_.id,
                        "type":type(_).__name__,
                        "text": _.get_text()
                    }
                )
                print("New queue:", _.server.queue)
            _new_object.connect("changed", __internal_changed__)
        else:
            _new_object = Objects.__dict__[_object["type"]](
                **_rebuilt_args
            )
            # if _new_object.__class__.__name__ == "Label":
            #     fontdesc = pango.FontDescription("Courier 18")
            #     _new_object.modify_font(fontdesc)

        if "align" in _object:
            if _object["align"] == "right":
                target.pack_end(
                    _new_object, True, True, 0
                )
        else:
            target.pack_start(
                    _new_object, True, True, 0
                )
        
        if "id" in _object:
            self.TransmutableObjects[_object["id"]] = _new_object

    def rebuild_args(self, args):
        _rebuilt_args = {} 
        for arg in args:
            if arg[0] == "$":
                _rebuilt_args[arg[1:]] = eval(args[arg])
            else: _rebuilt_args[arg] = args[arg]

        return _rebuilt_args

    def process_child(self, target, child):
        _rebuilt_args = self.rebuild_args(child["args"])

        self.process_object(child, _rebuilt_args, target)

def __main__(
    args
):
    win = BaseWindow(
        config = load(open(args.config, "r")),
        server = server
    )
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    # print(server)
    s = Thread(target=server.cycle, args=())
    s.start()
    # Start the main thread
    Gtk.main()

parse = ArgumentParser()

parse.add_argument('--config', action='store', 
                    type=str, 
                    required=True,
                    help='load config from file path')

args = parse.parse_args()

if __name__ == "__main__":
    __main__(args)

# nuitka3 --standalone --onefile -j=8 --static-libpython=yes gui.py -o pysharpgtk_py