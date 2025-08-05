
class CyrillicKeybindsMixin:

    @staticmethod
    def enable_cyrillic_keybinds(root):
        root.bind("<Control-Key>", CyrillicKeybindsMixin.copy_paste)

    @staticmethod
    def copy_paste(e):
        if e.keycode == 86 and e.keysym != 'v':
            e.widget.event_generate('<<Paste>>')
        elif e.keycode == 67 and e.keysym != 'c':
            e.widget.event_generate('<<Copy>>')
        elif e.keycode == 88 and e.keysym != 'x':
            e.widget.event_generate('<<Cut>>')
