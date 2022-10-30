import os
import sys
from multiprocessing import Queue
import signal
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W

from multiprocessing import Process, Queue
from dragonfly import monitors

try:  # Style C -- may be imported into Caster, or externally
    BASE_PATH = os.path.realpath(__file__).rsplit(os.path.sep + "castervoice", 1)[0]
    if BASE_PATH not in sys.path:
        sys.path.append(BASE_PATH)
finally:
    from castervoice.lib.merge.communication import Communicator
    from castervoice.lib import settings

def hud_manager(conn):
    '''
    Entry-point for the subprocess. Initializes a tk application, but does not
    show the window. This function is called at program startup.
    '''
    app = Hud(conn)
    app.mainloop()

class Hud(tk.Tk):
    def __init__(self, queue):
        super().__init__()
        self.message_queue = queue
        self.title('Caster Hud')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Create the panes and frames
        vertical_pane = ttk.PanedWindow(self, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)
        console_frame = ttk.Labelframe(horizontal_pane, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(console_frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('fDICTATION', foreground='black')
        self.scrolled_text.tag_config('MESSAGE', foreground='gray')
        self.scrolled_text.tag_config('ENGINE', foreground='orange')
        self.scrolled_text.tag_config('COMMAND', foreground='red')
        self.scrolled_text.tag_config('DICTATIONe', foreground='red', underline=1)
        self.duplicate_count = 1
        self.last_message = None
        # Initialize all frames
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)
        self.rulesui = RulesUi(self)
        self.rulesui.withdraw()
        self.withdraw() # Hide HUD
        # Start polling messages from the queue
        self.after(50, self.poll_message_queue)

    def display_text(self, message_type, message):
        if self.last_message != message:
            self.scrolled_text.insert(tk.END, message + '\n')
            self.duplicate_count = 1
        else:
            self.duplicate_count += 1
            self.scrolled_text.mark_set("insert", "%d.%d" % (float(self.scrolled_text.index("current")) - 1, 0))
            self.scrolled_text.replace('end-2c linestart', 'end-2c', message + f"({self.duplicate_count})")
        self.last_message = message
        # add text formatting
        self.scrolled_text.tag_add(message_type, 'end-2c linestart', 'end-2c')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def save_all_text(self):
        self.saveText = self.scrolled_text.get('1.0', tk.END)  # Get all text in widget.
        print('self.saveText:', self.saveText)

    def clear_text(self):
        self.scrolled_text.delete("1.0", tk.END)

    def poll_message_queue(self):
        # Check every 50ms if there is a new message in the queue to display
        while True:
            try:
                message = self.message_queue.get_nowait()
            except Exception:
                break
            else:
                self.prosses_queue(message)
        self.after(50, self.poll_message_queue)

    def prosses_queue(self, record):
        if record is None:
             self.quit()
        try:
            (message_type, message) = record
            self.scrolled_text.configure(state='normal')
            if message_type in ["fDICTATION", "DICTATION", "COMMAND", "MESSAGE", "ENGINE"]:
                self.display_text(message_type, message)
            elif message_type == "SHOW_HUD":
               self.showhud()
            elif message_type == "HIDE_HUD":
               self.hidehud()
            elif message_type == "SHOW_RULES":
                self.rulesui.setrules(message)
                self.rulesui.showrules()
            elif message_type == "HIDE_RULES":
                self.rulesui.hiderules()
            elif message_type == "CLEAR_HUD":
                self.clear_text()
            elif message_type == "CLOSE_HUD":
                self.quit()
        finally:
            self.scrolled_text.configure(state='disabled')
    
    def hidehud(self):
        self.withdraw()

    def showhud(self):
        self.deiconify()
    
    def quit(self, *args):
        self.destroy()
        os.kill(os.getpid(), signal.SIGTERM)


class RulesUi(tk.Toplevel):
    """Display messages in a scrolled text widget"""
    def __init__(self, parent):
        super().__init__(parent, relief=tk.SUNKEN, bd=2)
        self.menubar = tk.Menu(self)
        self.title("RulesUi")
        self.winfo_toplevel().configure(menu=self.menubar)

        self.treeview = ttk.Treeview(self, columns = ('Phrase', 'Action'))

        self.yscrollbar = ttk.Scrollbar(self, orient='vertical', command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.yscrollbar.set)

        self.treeview.grid(row=0, column=0, sticky="nsew")
        self.yscrollbar.grid(row=0, column=1, sticky='nse')
        self.yscrollbar.configure(command=self.treeview.yview)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.treeview.heading('#0', text = 'Phrase')
        self.treeview.heading('#1', text = 'Action')

    def setrules(self, rules_dict):
        for g in rules_dict:
            print(g)
            gram = g["name"] if len(g["rules"]) > 1 else None # nested rules in a grammar
            if gram:
                self.treeview.insert('', '0', gram, text = gram) # Insert grammar name to top level tree view
            for r in g["rules"]:
                parent = gram if gram is not None else '' # Insert rule into parent grammar or '' as top level tree view
                self.treeview.insert(parent, '0', r["name"], text = r["name"])
                for s in r["specs"]:
                    if '::' in s:
                        phrase, action = s.split('::', 1)
                        self.treeview.insert(r["name"], 'end', phrase, text=phrase, value=[action])
                    else:
                        self.treeview.insert(r["name"], 'end', s, text=s)

    def clearrules(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)
    
    def hiderules(self):
        self.withdraw()
    
    def showrules(self):
        self.deiconify()

if __name__ == "__main__":
    # Quick and dirty way to test the hud window
    from multiprocessing import Process, Queue
    import time
    conn = Queue()
    p = Process(target=hud_manager, args=(conn,), daemon=True)
    p.start()
    conn.put(("SHOW_HUD", ""), block=False)
    conn.put(("ENGINE", "No rules loaded"), block=False)
    #Whoconn.put(None, block=False)
    #conn.put(("CLEAR_HUD", "Test"), block=False)
    #conn.put(("CLOSE_HUD", ""), block=False)
    conn.put(("SHOW_RULES", ""), block=False)
    conn.put(("COMMAND", "COMMAND 1"), block=False)
    conn.put(("fDICTATION", "This is a test dictation"), block=False)
    conn.put(("MESSAGE", "MESSAGE 12"), block=False)
    conn.put(("COMMAND", "COMMAND 1"), block=False)
    p.join()