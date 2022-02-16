import sys
from castervoice.lib import printer

if sys.platform == "win32":
    from .windows_virtual_desktops import show_workwork_spaces
    from .windows_virtual_desktops import create_work_space
    from .windows_virtual_desktops import close_workspace
    from .windows_virtual_desktops import close_all_workspaces
    from .windows_virtual_desktops import go_next_desktop
    from .windows_virtual_desktops import go_previous_desktop
    from .windows_virtual_desktops import go_to_desktop_number
    from .windows_virtual_desktops import move_current_window_to_desktop
    from .windows_virtual_desktops import pin_or_unpin_current_app
    from .windows_virtual_desktops import pin_or_unpin_current_window

else:
    def show_workwork_spaces():
        printer.out("show_workwork_spaces: Virtual desktop commands are not implemented on this platform")

    def create_work_space():
        printer.out("create_work_space: Virtual desktop commands are not implemented on this platform")
    
    def close_workspace():
        printer.out("close_workspace: Virtual desktop commands are not implemented on this platform")

    def close_all_workspaces():
        printer.out("close_all_workspaces: Virtual desktop commands are not implemented on this platform")

    def go_next_desktop():
        printer.out("go_next_desktop: Virtual desktop commands are not implemented on this platform")

    def go_previous_desktop():
        printer.out("go_previous_desktop: Virtual desktop commands are not implemented on this platform")

    def go_to_desktop_number(n: int):
        printer.out("go_to_desktop_number: Virtual desktop commands are not implemented on this platform")

    def move_current_window_to_desktop(n=1, follow=False):
        printer.out("move_current_window_to_desktop: Virtual desktop commands are not implemented on this platform")

    def pin_or_unpin_current_app():
        printer.out("pin_or_unpin_current_app: Virtual desktop commands are not implemented on this platform")

    def pin_or_unpin_current_window():
        printer.out("pin_or_unpin_current_window: Virtual desktop commands are not implemented on this platform")