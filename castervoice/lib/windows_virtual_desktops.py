# https://github.com/mrob95/py-VirtualDesktopAccessor
from dragonfly import Key
from castervoice.lib import printer

try:
    import pyvda  # pylint: disable=import-error
except Exception as e:
    # This could fail on linux or windows <10
    print(f"Importing package pyvda failed with exception {e}")


def is_workspace_valid(n: int) -> int:
    """Vlaidate if n is in the number of available workspaces
        returns: boolean
    """
    if n not in range(1, len(pyvda.get_virtual_desktops()) + 1):
        printer.out(f"Requested {n} workspace does not exist")
        return False
    return True


def show_workwork_spaces() -> None:
    """Show all virtual desktops"""
    Key("w-tab").execute()


def create_work_space() -> None:
    """Create a new virtual desktop"""
    n = len(pyvda.get_virtual_desktops())
    if n != 1:
        n + 1
    pyvda.VirtualDesktop(n).create()


def close_workspace() -> None:
    """Close the current virtual desktop"""
    Key("wc-f4/10").execute()


def close_all_workspaces() -> None:
    """Close all virtual desktops"""
    total = len(pyvda.get_virtual_desktops())
    for n in range(total):
        Key("wc-f4/10:" + str(n)).execute()


def go_to_desktop_number(n: int) -> int:
    """Move the current foreground window to the nth virtual desktop"""
    if is_workspace_valid(n):
        pyvda.VirtualDesktop(n).go()


def go_next_desktop(n: int) -> int:
    """Move the current foreground window to the nth virtual desktop"""
    target = pyvda.VirtualDesktop(current=True).number + n
    if is_workspace_valid(target):
        pyvda.VirtualDesktop(target).go()


def go_previous_desktop(n: int) -> int:
    """Move the current foreground window to the nth virtual desktop"""
    target = pyvda.VirtualDesktop(current=True).number - n
    if is_workspace_valid(target):
        pyvda.VirtualDesktop(target).go()


def move_current_window_to_desktop(n: int, follow: bool = False):
    """Move the current foreground window to the nth virtual desktop"""
    if is_workspace_valid(n):
        current_window = pyvda.AppView.current()
        target_desktop = pyvda.VirtualDesktop(n)
        current_window.move(target_desktop)
        if follow:
            pyvda.VirtualDesktop(n).go()


def pin_or_unpin_current_window(pin=True) -> bool:
    """Pin or unpin the current foreground window"""
    if pin:
        pyvda.AppView.current().pin()
    else:
        pyvda.AppView.current().unpin()


def pin_or_unpin_current_app(pin=True) -> bool:
    """Pin or unpin the current application
        Args: pin (bool): True to pin, False to unpin
    """
    if pin:
        pyvda.AppView.current().pin_app()
    else:
        pyvda.AppView.current().unpin_app()
