# Gedit Markdown Preview

## Install
This plugin depends on the `python3-markdown` package (install via your preferred method)

```sh
mkdir -p ~/.local/share/gedit/plugins/
cd ~/.local/share/gedit/plugins/
git clone https://github.com/aliva/gedit-markdownpreview.git markdownpreview
```
Optionally install `pymdown-extensions` for extra utility with:   
`pip3 install pymdown-extensions`

Tested on gedit 3.30.2

## Features:
This plugin supports standard Markdown, plus:
- [Code Highlighting](https://python-markdown.github.io/extensions/code_hilite/)
- [Abbreviations](https://python-markdown.github.io/extensions/abbreviations/)
- [Attribute Lists](https://python-markdown.github.io/extensions/attr_list/)
- [Definition Lists](https://python-markdown.github.io/extensions/definition_lists/)
- [Fenced Code Blocks](https://python-markdown.github.io/extensions/fenced_code_blocks/)
- [Footnotes](https://python-markdown.github.io/extensions/footnotes/)
- [Tables](https://python-markdown.github.io/extensions/tables/)

With optional `pymdown-extensions`:   
- [Caret](https://facelessuser.github.io/pymdown-extensions/extensions/caret/) superscripting
- [Better Emphasis](https://facelessuser.github.io/pymdown-extensions/extensions/betterem/) for bold, itallic, and underscore
- [SuperFences](https://facelessuser.github.io/pymdown-extensions/extensions/superfences/) Improved Fenced Code Blocks
- [extrarawHTML](https://facelessuser.github.io/pymdown-extensions/extensions/extrarawhtml/) to Parse MD inside HTML blocks
- [Mark](https://facelessuser.github.io/pymdown-extensions/extensions/mark/) for simple highlighting
- [Task Lists](https://facelessuser.github.io/pymdown-extensions/extensions/tasklist/)
- [Tilde](https://facelessuser.github.io/pymdown-extensions/extensions/tilde/) for subscripting and strikethrough

## Usage

When viewing a markdown file press `ctrl+alt+m` to toggle markdown preview

## Screenshot

![screenshot](/screenshot.png)
