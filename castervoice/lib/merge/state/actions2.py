from dragonfly.actions.action_function import Function
from castervoice.lib.merge.state.actions import RegisteredAction


class NullAction(RegisteredAction):
    def __init__(self, rspec="default", rdescript="unnamed command (RA)", show=False):
        RegisteredAction.__init__(
            self,
            Function(lambda: None),
            rspec=rspec,
            rdescript=rdescript,
            rundo=None,
            show=show)
