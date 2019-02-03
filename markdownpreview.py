import os
from string import Template

from gi.repository import Gedit, GObject, Gtk, WebKit2
from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class AutoDirection(Treeprocessor):
    def run(self, root):
        for element in root.iter('p'):
            element.set('dir', 'auto')


class AutoDirectionExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('autodirection', AutoDirection(md), '_end')
        md.registerExtension(self)


class MarkdownPreviewViewActivatable(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "MarkdownPreviewViewActivatable"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.scrolledwindow = self.view.get_parent()
        self.webview = None

        self.style_template = None
        self.html_template = None

        buffer = self.view.get_buffer()
        buffer.connect('notify::language', self.language_changed)
        self.language_changed(buffer, None)

    def language_changed(self, buffer, language):
        language = buffer.get_language()

        if language is None:
            return

        lang_id = language.get_id()

        if lang_id == 'markdown':
            self.webview = WebKit2.WebView()

            buffer.connect('changed', self.changed)
            adjustment = self.scrolledwindow.get_vadjustment()
            adjustment.connect('changed', self.scrolled)
            adjustment.connect('value-changed', self.scrolled)

            box = self.scrolledwindow.get_parent()
            box.pack_end(self.webview, True, True, 0)

            self.webview.show_all()
            self.changed(buffer)
        else:
            self.do_deactivate()

    def changed(self, buffer):
        plugin_dir = os.path.dirname(__file__)
        if self.style_template is None:
            style_path = os.path.join(plugin_dir, 'style.css')
            self.style_template = open(style_path, 'r').read()
        if self.html_template is None:
            html_path = os.path.join(plugin_dir, 'template.html')
            self.html_template = open(html_path, 'r').read()


        text = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            True,
        )
        html = markdown(
            text,
            extensions=['codehilite', 'fenced_code', AutoDirectionExtension()],
            extension_configs={
                'codehilite': {
                    'linenums': False,
                    'noclasses': True,
                }
            }
        )
        html = Template(self.html_template).substitute(
            content=html,
            style=self.style_template,
            scroll_position=self.get_scroller_pos(),
        )
        self.webview.load_html(html)
        self.scrolled(None)

    def get_scroller_pos(self):
        adj = self.scrolledwindow.get_vadjustment()
        value = adj.get_value() / (adj.get_upper() - adj.get_lower())
        return value

    def scrolled(self, adjustment):
        scroll_position = self.get_scroller_pos()
        self.webview.run_javascript("scrollWebkit(%s)" % scroll_position)

    def do_deactivate(self):
        if self.webview:
            self.webview.destroy()
            self.webview = None

            buffer = self.view.get_buffer()
            buffer.disconnect_by_func(self.changed)

            adjustment = self.scrolledwindow.get_vadjustment()
            adjustment.disconnect_by_func(self.scrolled)
            adjustment.disconnect_by_func(self.scrolled)

    def do_update_state(self):
        pass
