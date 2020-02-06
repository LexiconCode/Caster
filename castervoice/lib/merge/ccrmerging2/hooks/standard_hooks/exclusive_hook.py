from castervoice.lib import settings, textformat
from castervoice.lib.merge.ccrmerging2.hooks.base_hook import BaseHook
from castervoice.lib.merge.ccrmerging2.hooks.events.event_types import EventType


def _apply_exclusiveness(grammar):
        try:
            grammar.set_exclusiveness(1)
        except Exception as e:
            print(e)


class ExclusiveHook(BaseHook):
    def __init__(self):
        super(ExclusiveHook, self).__init__(EventType.GRAMMERS_LOADED)

    def get_pronunciation(self):
        return "exclusive"

    def run(self, event_data):
        grammar = event_data.grammar
        _apply_exclusiveness(grammar)


def get_hook():
    return ExclusiveHook
