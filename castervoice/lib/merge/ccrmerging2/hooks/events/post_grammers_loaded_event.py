from castervoice.lib.merge.ccrmerging2.hooks.events.base_event import BaseHookEvent
from castervoice.lib.merge.ccrmerging2.hooks.events.event_types import EventType


class PostGrammersLoadedEvent(BaseHookEvent):
    def __init__(self, grammar):
        super(PostGrammersLoadedEvent, self).__init__(EventType.GRAMMERS_LOADED)
        self.grammar = grammar