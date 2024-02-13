from util import show_configuration

from lauterbach.trace32.pystart import (
    FontSize,
    Language,
    Palette,
    PowerView,
    USBConnection,
    WindowMode,
    defaults,
)

powerview = PowerView(USBConnection(), "t32marm")

defaults.font_size = FontSize.MEDIUM
defaults.clear_type = None
defaults.palette = Palette.DEFAULT
defaults.full_screen = False
defaults.ionic = False
defaults.invisible = False
defaults.window_mode = WindowMode.MDI
defaults.language = Language.ENGLISH

powerview.title = "New Title"
powerview.font_size = FontSize.SMALL
powerview.clear_type = False
powerview.palette = Palette.DEFAULT
powerview.full_screen = True
powerview.ionic = False
powerview.invisible = False
powerview.window_mode = WindowMode.FDI
powerview.language = Language.ENGLISH


show_configuration(powerview)
