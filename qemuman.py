# A small manager program for QEMU. Tested on Windows
# https://github.com/yeppiidev/qemu-manager

import os
import tkinter as tk
import atexit

from subprocess import PIPE
from subprocess import Popen, CalledProcessError

from tkinter.messagebox import showinfo as alert
from tkinter.messagebox import askyesno as confirm

from ttkthemes import ThemedTk
from tkinter import ttk
from shutil import which

qemu_process = None
qemu_type_box = None
cdrom_path = None

class Manager():
    def __init__(self) -> None:
        self.root = ThemedTk()
        self.root.title("QEMU Manager")
        self.root.geometry("600x500")
        self.root.wm_resizable(False, False)

        self.root.style = ttk.Style()
        self.root.style.theme_use('arc')
        self.root.style.configure('raised.TButton', borderwidth=1)
        
        # Variables
        self.qemu_kill_on_exit = tk.BooleanVar()
        self.qemu_kill_on_exit.set(True)
        
        self.qemu_sdl_window = tk.BooleanVar()
        self.qemu_sdl_window.set(False)
        
        self.qemu_use_haxm = tk.BooleanVar()
        self.qemu_use_haxm.set(False)

        atexit.register(self.exit_handler)
        
        self.create_widgets()
        self.root.mainloop()

    def is_tool(self, name):
        # Check whether `name` is on PATH and marked as executable
        # https://stackoverflow.com/a/34177358/15871490

        return which(name) is not None

    def exit_handler(self):
        if self.qemu_kill_on_exit.get():
            self.qemu_process.kill()
            
    def kill_vm(self):
        if confirm("Terminate QEMU", "Are you sure you want to terminate the QEMU process? Any unsaved changes inside the virtual machine will be lost!", icon='warning') == 'yes':
            self.qemu_process.kill()
    
    def start_vm(self):
        try:
            if not self.is_tool(self.qemu_type_box.get()):
                alert("Unable to start the VM", "It seems like QEMU is not installed on your system. Please install it and try again.", icon='error')
                return 1
            
            if not os.path.exists(self.cdrom_path.get()):
                alert("Unable to start the VM", "The specified CD-ROM file does not exist", icon='error')
                return 1

            self.qemu_process = Popen(f"{self.qemu_type_box.get()} -cdrom {self.cdrom_path.get()} {'-sdl' if self.qemu_sdl_window.get() else ''}", stdout=PIPE, stderr=PIPE)
        except CalledProcessError as e:
            alert(
                title='QEMU Returned an error',
                message=f'QEMU Returned an error: {str(e.output)}',
            )

    def create_widgets(self):
        # Add a label to root
        title_label = ttk.Label(self.root, 
                                text="QEMU Manager",
                                anchor='w',
                                background=self.root.cget("background"),
                                font=("Tahoma", 30))
        title_label.pack(fill="both", padx=18, pady=18)

        # Add a button to start the VM
        start_vm = ttk.Button(self.root, text="Start VM", command=self.start_vm)
        start_vm.pack(ipadx=10, ipady=10, padx=10, pady=10)
        start_vm.place(x=490, y=445)
        
        # Add a button to kill the VM
        kill_vm = ttk.Button(self.root, text="Terminate QEMU", command=self.kill_vm)
        kill_vm.pack(ipadx=10, ipady=10, padx=10, pady=10)
        kill_vm.place(x=360, y=445)

        qemu_type_box_label = ttk.Label(self.root, text="CPU Architecture:", background=self.root.cget("background"))
        qemu_type_box_label.pack(fill='x', padx=15)

        qemu_type_box_current = tk.StringVar()

        self.qemu_type_box = ttk.Combobox(self.root, state='readonly', textvariable=qemu_type_box_current)
        self.qemu_type_box['values'] = ("qemu-system-i386",
                                   "qemu-system-x86_64",
                                   "qemu-system-ppc",
                                   "qemu-system-ppc64")
        self.qemu_type_box.current(1)
        self.qemu_type_box.pack(fill=tk.X, padx=15, pady=5)
        
        cdrom_path_label = ttk.Label(self.root, text="CD-ROM (ISO) File Path:", background=self.root.cget("background"))
        cdrom_path_label.pack(fill='x', padx=15, pady=5)

        self.cdrom_path = ttk.Entry(self.root, textvariable="text")
        self.cdrom_path.pack(fill='x', padx=15)
        self.cdrom_path.focus()

        qemu_sdl_window = ttk.Checkbutton(self.root, text="Use SDL as the window library?", variable=self.qemu_sdl_window, offvalue=False, onvalue=True)
        qemu_sdl_window.pack(fill='x', padx=15, pady=(10, 2))

        qemu_use_haxm = ttk.Checkbutton(self.root, text="Use Intel HAXM? (Requires you to have HAXM installed)", variable=self.qemu_use_haxm, offvalue=False, onvalue=True)
        qemu_use_haxm.pack(fill='x', padx=15, pady=2)

        qemu_kill_on_exit_box = ttk.Checkbutton(self.root, text="Kill QEMU on Exit?", variable=self.qemu_kill_on_exit, offvalue=False, onvalue=True)
        qemu_kill_on_exit_box.pack(fill='x', padx=15, pady=2)
        
        # Uncomment for fun :]        
        # self.selected_theme = tk.StringVar()
        
        # for theme_name in self.root.get_themes():
        #     self.rb = ttk.Radiobutton(
        #         self.root,
        #         text=theme_name,
        #         value=theme_name,
        #         variable=self.selected_theme,
        #         command=(lambda: self.root.set_theme(theme_name=self.selected_theme.get()))
        #     )
        #     self.rb.pack(expand=True, fill='both')

# Start the manager by constructing a new class
manager = Manager()