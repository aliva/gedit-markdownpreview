from gi.repository import GObject, Gedit, WebKit2, Gtk
from markdown import markdown

scrolljs = """
height = document.body.scrollHeight;
pos = {value} * height;
scroll({{
    top: pos,
    behavior: 'smooth',
}});
"""


class MarkdownPreviewViewActivatable(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "MarkdownPreviewViewActivatable"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.scrolledwindow = self.view.get_parent()
        self.webview = None
        self.signal_handlers = [None, None, None]

        buffer = self.view.get_buffer()
        buffer.connect('notify::language', self.language_changed)
        self.language_changed(buffer, None)

    def language_changed(self, buffer, language):
        language = buffer.get_language()

        if language is None:
            return

        lang_id = language.get_id()

        if self.webview is None and lang_id == 'markdown':
            self.webview = WebKit2.WebView()

            buffer.connect('changed', self.changed)
            adjustment = self.scrolledwindow.get_vadjustment()
            adjustment.connect('changed', self.scrolled)
            adjustment.connect('value-changed', self.scrolled)

            box = self.scrolledwindow.get_parent()
            box.pack_end(self.webview, True, True, 0)

            self.webview.show_all()
            self.changed(buffer)
        elif self.webview:
            self.do_deactivate()

    def changed(self, buffer):
        text = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            True,
        )
        text = markdown(
            text,
            extensions=['codehilite', 'fenced_code'],
            extension_configs={
                'codehilite': {
                    'linenums': False,
                    'noclasses': True,
                }
            }
        )
        value = self.get_scroller_pos()
        text = text + "<script>" + scrolljs.format(value=value) + "</script>"
        self.webview.load_html(text)
        self.scrolled(None)

    def get_scroller_pos(self):
        adj = self.scrolledwindow.get_vadjustment()
        value = adj.get_value() / (adj.get_upper() - adj.get_lower())
        return value

    def scrolled(self, adjustment):
        value = self.get_scroller_pos()
        self.webview.run_javascript(scrolljs.format(value=value))

    def do_deactivate(self):
        self.webview.destroy()
        self.webview = None

        buffer = self.view.get_buffer()
        buffer.disconnect_by_func(self.changed)

        adjustment = self.scrolledwindow.get_vadjustment()
        adjustment.disconnect_by_func(self.scrolled)
        adjustment.disconnect_by_func(self.scrolled)

    def do_update_state(self):
        pass
