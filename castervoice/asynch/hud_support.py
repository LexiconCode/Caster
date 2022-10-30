import sys, traceback

from dragonfly import CompoundRule, MappingRule, get_engine, get_current_engine, RecognitionObserver

if get_engine().name == "natlink":
    from dragonfly.engines.backend_natlink.dictation_format import WordFormatter

from pathlib import Path

try:  # Style C -- may be imported into Caster, or externally
    BASE_PATH = str(Path(__file__).resolve().parent.parent)
    if BASE_PATH not in sys.path:
        sys.path.append(BASE_PATH)
finally:
    from castervoice.lib import settings

from castervoice.lib import printer, control, utilities
from castervoice.lib.rules_collection import get_instance
from multiprocessing import Process, Queue
from castervoice.asynch.hud import hud_manager

HUD = Queue()
WinProcess = None

class initializeHUD:
    """
    Start a new process initialized from the hud_manager function
    in the process module. All communication happens over a subprocess for HUD.
    """
    def __init__(self):
        global WinProcess
        WinProcess = Process(target=hud_manager, args=(HUD,), daemon=True)

    def start(self):
        try:
            if not WinProcess.is_alive():
                WinProcess.start()
        except Exception as e:
            print(traceback.print_exc())

    def stop(self):
        WinProcess.close()

class processEngineResults:
    # TODO: Move this to its own file.
    # TODO: Need to change how functions handle self.pr
    """Standardizes engine results into common format then if needed applies formatting to dictation"""
    def __init__(self) -> None:
        self.engine = get_current_engine().name
        self.pr = []
        
    def process(self, results):
        if self.engine == "natlink":
           self.standardize_natlink(results)
        if self.engine == "kaldi":
            self.standardize_kaldi(results)
        self.compact_utterance(self.pr)    
        self.apply_engine_formatting(self.pr)
        return self.pr

    def compact_utterance(self, pr):
        """Concatenate words that have identical recognition type per chain
        for formatting utterance"""
        # Before [('say', 'COMMAND'), ('say', 'COMMAND'), ('hi', DICTATIONe), ('you', DICTATIONe), ('say', 'COMMAND')]
        # After [('say say', 'COMMAND'), ('hi you', 'DICTATIONe'), ('say', 'COMMAND')]
        result = []
        last_recognition_type = None
        for item in self.pr:
            word, recognition_type = item
            if last_recognition_type == recognition_type:
                result[-1] = (result[-1][0] + ' ' + word, result[-1][-1])
            else:
                result.append((word, recognition_type))
            last_recognition_type = recognition_type
        self.pr = result

    def standardize_natlink(self, results):
        # TODO: Is it possible handle mimic?
        for word, recognition_type in results.getResults(0)[:]:
            if recognition_type in [1,2]:
                self.pr.append((word,"COMMAND")) # Command
            elif recognition_type == 1000000:
                self.pr.append((word,"DICTATION")) # Dictation element
            elif recognition_type == 0:
                self.pr.append((word,"fDICTATION")) # Free dictation
            elif recognition_type not in [1,2,1000000,0]:
                # FIXME: handle engine commands with differing types DNS "minimize win"
                # compact_utterance only handles the same recognition type.
                self.pr.append((word,"ENGINE"))

    def standardize_kaldi(self, results):
        # Recognition object dir 'acceptable', 'confidence', 'construct_empty', 'engine', 'expected_error_rate', 'fail', 'finalized', 
        # 'has_dictation', 'kaldi_rule', 'mimic', 'parsed_output', 'process', 'words', 'words_are_dictation_mask']
        results = list(map(lambda x, y:(x,y), results.words, results.words_are_dictation_mask))
        for word, recognition_type in results:
            if recognition_type is False:
                self.pr.append((word,"COMMAND")) # Command
            elif recognition_type is True:
                self.pr.append((word,"DICTATION")) # Dictation element
                # TODO: handle mimic?
        
    def apply_engine_formatting(self, results):
        for index, item in enumerate(results):
            words, recognition_type = item
            if self.engine == "natlink":
                from dragonfly.engines.backend_natlink.dictation_format import WordFormatter
                if recognition_type == "fDICTATION":
                    formatted_word = WordFormatter().format_dictation(words.split())
                    results[index] = (''.join(map(str, formatted_word)), "fDICTATION")
                # TODO: Apply integer formatting Natlink, Dragonfly or third-party

class Observer(RecognitionObserver):
    def __init__(self):
        self.mic_mode = None
        self.output = []
        self._engine_modes_manager = control.nexus().engine_modes_manager

    def on_begin(self):
        self.mic_mode = self._engine_modes_manager.get_mic_mode()

    def on_recognition(self, words, results):
        if not self.mic_mode == "sleeping":
            results = processEngineResults().process(results)
            for item in results:
                HUD.put((item[1] , "{}".format(item[0])), block=False)
                # 'acceptable', 'confidence', 'construct_empty', 'engine', 'expected_error_rate', 'fail', 'finalized', 
                # 'has_dictation', 'kaldi_rule', 'mimic', 'parsed_output', 'process', 'words', 'words_are_dictation_mask']
                #print(results.words_are_dictation_mask)
                #print(results.words)
                #print(results.words_are_dictation_mask)
                #print(results.has_dictation)

    def on_failure(self):
        if not self.mic_mode == "sleeping":
           HUD.put(("MESSAGE", "?!"), block=False)
    
    def on_end(self):
        pass
        #HUD.put(("UTTERANCE", "{}".format(self.output)), block=False)
        #self.output = []


def show_hud():
    """
    Show the HUD GUI
    """
    try:
        HUD.put(("SHOW_HUD", ""), block=False)
    except Exception as e:
        printer.out(f"Unable to show hud. Hud not available. \n{e}")


def hide_hud():
    """
    Hide the HUD GUI
    """
    try:
        HUD.put(("HIDE_HUD", ""), block=False)
    except Exception as e:
        printer.out(f"Unable to hide hud. Hud not available. \n{e}")


def clear_hud():
    """
    Clear text in Hud window.
    """
    try:
        HUD.put(("CLEAR_HUD", ""), block=False)
    except Exception as e:
        printer.out(f"Unable to clear hud. Hud not available. \n{e}")
    #Function(utilities.clear_log).execute()


def show_rules():
    """
    Get a list of active grammars loaded into the current engine,
    including active rules and their attributes.  Send the list
    to HUD GUI for display.
    """
    grammars = []
    engine = get_current_engine()
    for grammar in engine.grammars:
        if any([r.active for r in grammar.rules]):
            rules = []
            for rule in grammar.rules:
                if rule.active and not rule.name.startswith('_'):
                    if isinstance(rule, CompoundRule):
                        specs = [rule.spec]
                    elif isinstance(rule, MappingRule):
                        specs = sorted([f"{x}::{rule._mapping[x]}" for x in rule._mapping])
                    else:
                        specs = [rule.element.gstring()]
                    rules.append({
                        "name": rule.name,
                        "exported": rule.exported,
                        "specs": specs
                    })
            grammars.append({"name": grammar.name, "rules": rules})
    grammars.extend(get_instance().serialize())
    try:
        #HUD.put(("SHOW_RULES", json.dumps(grammars)), block=False)
        HUD.put(("SHOW_RULES", grammars), block=False)
    except Exception as e:
        printer.out(f"Unable to show rules. Hud not available. \n{e}")


def hide_rules():
    """
    Instruct HUD to hide the frame with the list of rules.
    """
    HUD.put(("HIDE_RULES", ""), block=False)


class HudPrintMessageHandler(printer.BaseMessageHandler):
    """
    Hud message handler which prints formatted messages to the gui Hud. 
    """

    def __init__(self):
        super(HudPrintMessageHandler, self).__init__()
        try:
            if WinProcess.is_alive():
                show_hud()
                Observer().register()
        except Exception as e:
            printer.out(f"HudPrintMessageHandler: Hud not available. \n{e}")

    def handle_message(self, items):
        if WinProcess.is_alive():
            # TODO: handle raising exception gracefully
            try:
                HUD.put(("MESSAGE", "\n".join([str(m) for m in items])), block=False)
            except Exception as e:
                print(traceback.print_exc())
                raise("") # pylint: disable=raising-bad-type

        else:
            printer.out(f"Hud not available. \n{e}")
            raise("") # pylint: disable=raising-bad-type