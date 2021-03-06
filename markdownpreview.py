import os
from string import Template

import importlib.util

import gi
from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

gi.require_version('WebKit2', '4.0')

from gi.repository import Gedit, Gio, GObject, Gtk, WebKit2  # isort:skip




class AutoDirection(Treeprocessor):
    def run(self, root):
        for element in root.iter('p'):
            element.set('dir', 'auto')


class AutoDirectionExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('autodirection', AutoDirection(md), '_end')
        md.registerExtension(self)


class MarkdownPreviewAppActivatable(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = "MarkdownPreviewAppActivatable"

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.app.set_accels_for_action(
            "win.toggle_markdown_preview",
            ["<Ctrl><alt>m"],
        )
        self.menu_ext = self.extend_menu("tools-section")
        item = Gio.MenuItem.new(
            "Toggle markdown preview",
            "win.toggle_markdown_preview"
        )
        self.menu_ext.prepend_menu_item(item)


class MarkdownPreviewWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "MarkdownPreviewWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        action = Gio.SimpleAction(name="toggle_markdown_preview")
        action.connect('activate', self.menu_button_handler)
        self.window.add_action(action)

        self.webviews = {}
        self.style_template = None
        self.html_template = None

    def do_deactivate(self):
        for view in self.webviews:
            self.disable_preview(view)

    def do_update_state(self):
        pass

    def menu_button_handler(self, action, parameter):
        self.attach_to_view()

    def attach_to_view(self):
        view = self.window.get_active_view()

        if view is None:
            return

        if view not in self.webviews:
            buffer = view.get_buffer()
            self.webviews[view] = None
            buffer.connect('notify::language', self.toggle_preview, view)

        self.toggle_preview(None, None, view)

    def toggle_preview(self, buffer, language, view):
        language = view.get_buffer().get_language()

        if language is None:
            return

        lang_id = language.get_id()

        if lang_id == 'markdown' and self.webviews[view] is None:
            self.enable_preview(view)
        else:
            self.disable_preview(view)

    def enable_preview(self, view):
        buffer = view.get_buffer()
        scrolledwindow = self.get_scrolledwindow(view)

        webview = WebKit2.WebView()
        self.webviews[view] = webview

        buffer.connect('changed', self.buffer_changed, view)

        adjustment = scrolledwindow.get_vadjustment()
        adjustment.connect('changed', self.buffer_scrolled, view)
        adjustment.connect('value-changed', self.buffer_scrolled, view)

        box = scrolledwindow.get_parent()
        box.pack_end(webview, True, True, 0)

        webview.show_all()
        self.buffer_changed(buffer, view)

    def disable_preview(self, view):
        if self.webviews[view]:
            self.webviews[view].destroy()
            self.webviews[view] = None

            try:
                buffer = view.get_buffer()
                buffer.disconnect_by_func(self.buffer_changed)

                adjustment = self.get_scrolledwindow(view).get_vadjustment()
                adjustment.disconnect_by_func(self.buffer_scrolled)
                adjustment.disconnect_by_func(self.buffer_scrolled)
            except TypeError:
                pass

    def buffer_changed(self, buffer, view):
        plugin_dir = os.path.dirname(__file__)
        if self.style_template is None:
            style_path = os.path.join(plugin_dir, 'style.css')
            self.style_template = open(style_path, 'r').read()
        if self.html_template is None:
            html_path = os.path.join(plugin_dir, 'template.html')
            self.html_template = open(html_path, 'r').read()

        buffer = view.get_buffer()

        text = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            True,
        )
        if importlib.util.find_spec('pymdownx') is not None:
            html = markdown(
                text,
                extensions=[
                    'pymdownx.caret',
                    'pymdownx.extra',
                    'pymdownx.mark',
                    'pymdownx.tasklist',
                    'pymdownx.tilde',
                    'codehilite',
                    AutoDirectionExtension(),
                ],
                extension_configs={
                    'codehilite': {
                        'linenums': False,
                        'noclasses': True,
                    }
                }
            )
        else:
            html = markdown(
                text,
                extensions=[
                    'extra',
                    'codehilite',
                    AutoDirectionExtension(),
                ],
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
            scroll_position=self.get_scroller_pos(view),
        )
        self.webviews[view].load_html(html)
        self.buffer_scrolled(None, view)

    def get_scroller_pos(self, view):
        adj = self.get_scrolledwindow(view).get_vadjustment()
        value_limit = adj.get_upper() - adj.get_lower() - adj.get_page_size()
        if value_limit == 0:
            return 0
        value = adj.get_value() / value_limit
        return value

    def buffer_scrolled(self, adjustment, view):
        scroll_position = self.get_scroller_pos(view)
        webview = self.webviews[view]
        webview.run_javascript("scrollWebkit(%s)" % scroll_position)

    def get_scrolledwindow(self, view):
        return view.get_parent()
