from dragonfly import MappingRule, Function, ShortIntegerRef, Choice

from castervoice.lib import utilities
from castervoice.lib import virtual_desktops
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class WindowManagementRule(MappingRule):
    mapping = {
        'window maximize':
            R(Function(utilities.maximize_window)),
        'window minimize':
            R(Function(utilities.minimize_window)),
        'window restore':
            R(Function(utilities.restore_window)),
        'window close':
            R(Function(utilities.close_window)),

        # Workspace management
        "show work [spaces]":
            R(Function(virtual_desktops.show_workwork_spaces)),
        "(create | new) work [space]":
            R(Function(virtual_desktops.create_work_space)),
        "close work [space]":
            R(Function(virtual_desktops.close_workspace)),
        "close all work [spaces]":
            R(Function(virtual_desktops.close_all_workspaces)),
        "next work [space] [<n>]":
            R(Function(virtual_desktops.go_next_desktop)),
        "(previous | prior) work [space] [<n>]":
            R(Function(virtual_desktops.go_previous_desktop)),
        "go work [space] <n>":
            R(Function(virtual_desktops.go_to_desktop_number)),
        "send work [space] <n>":
            R(Function(virtual_desktops.move_current_window_to_desktop)),
        "move work [space] <n>":
            R(Function(virtual_desktops.move_current_window_to_desktop, follow=True)),
        "<pin_unpin> work [space] window":
            R(Function(virtual_desktops.pin_or_unpin_current_window)),
        "<pin_unpin> work [space] app":
            R(Function(virtual_desktops.pin_or_unpin_current_app)), 
    }

    extras = [
        ShortIntegerRef("n", 1, 20, default=1),
        Choice("pin_unpin", {
            "pin": True, 
            "unpin": False
            }, default=True),
    ]


def get_rule():
    details = RuleDetails(name="window management rule")
    return WindowManagementRule, details
