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
from tkinter import ACTIVE, E, LEFT, N, RIGHT, S, W
from tkinter import ttk, simpledialog
from shutil import which

qemu_process = None
qemu_type_box = None
cdrom_path = None

# TODO: Pls fix this :(
class NewImageDialog(object):
    root = None

    def __init__(self, msg, dict_key=None):
        self.top = tk.Toplevel(NewImageDialog.root)
        self.top.title("HDD Image Wizard")
        self.top.geometry("450x300")
        self.top.wm_resizable(False, False)

        frame = ttk.Frame(self.top, borderwidth=4)
        frame.pack(fill="both", expand=True)

        label = tk.Label(
            frame,
            text="Create a new HDD Image",
            anchor="w",
            background=self.top.cget("background"),
            font=("Tahoma", 18),
        )
        label.pack(padx=4, pady=4)
        label.place(x=15, y=15)

        self.hdd_name_text = tk.StringVar()

        self.hdd_name = ttk.Entry(self.top, textvariable=self.hdd_name_text)
        self.hdd_name.pack(fill="x", padx=15)
        self.hdd_name.focus()

        b_cancel = ttk.Button(self.top, text="Cancel", command=self.top.destroy)
        b_cancel.pack()
        b_cancel.place(x=260, y=260)
        
        b_submit = ttk.Button(
            self.top, text="Create", command=lambda: self.entry_to_dict(dict_key)
        )
        b_submit.pack()
        b_submit.place(x=350, y=260)
        
    def entry_to_dict(self, dict_key):
        data = self.entry.get()
        if data:
            d, key = dict_key
            d[key] = data
            self.top.destroy()


class Manager:
    def __init__(self) -> None:
        self.root = ThemedTk()
        self.root.title("QEMU Manager")
        self.root.geometry("600x500")
        self.root.wm_resizable(False, False)

        self.root.style = ttk.Style()
        self.root.style.theme_use("arc")
        self.root.style.configure("raised.TButton", borderwidth=1)

        # Variables
        self.qemu_kill_on_exit = tk.BooleanVar()
        self.qemu_kill_on_exit.set(True)

        self.qemu_sdl_window = tk.BooleanVar()
        self.qemu_sdl_window.set(False)

        self.qemu_use_haxm = tk.BooleanVar()
        self.qemu_use_haxm.set(False)

        atexit.register(self.exit_handler)

        self.create_menu_items()
        self.create_widgets()

        self.running = True
        self.root.config(menu=self.menubar)

        self.root.mainloop()

    def is_tool(self, name):
        # Check whether `name` is on PATH and marked as executable
        # https://stackoverflow.com/a/34177358/15871490

        return which(name) is not None

    def exit_handler(self):
        if self.qemu_kill_on_exit.get() and hasattr(self, 'qemu_process'):
            self.qemu_process.kill()

    def kill_vm(self):
        # Show an error message if the VM is not running
        try:
            if not self.qemu_process.poll() is None:
                alert(
                    title="VM is not running", message="The VM is not running",
                )
                return 1
        except:
            alert(
                title="VM is not running", message="The VM is not running",
            )
            return 1

        # Do you really want to terminate the VM?
        if (
            confirm(
                "Terminate QEMU",
                "Are you sure you want to terminate the QEMU process? Any unsaved changes inside the virtual machine will be lost!",
                icon="warning",
            )
            == "yes"
        ):
            # TODO: Make this work lol
            self.qemu_process.kill()

    def create_image(self):
        dlg = NewImageDialog
        dlg.root = self.root

        NewImageDialog("Hello", (None, "user"))

    def start_vm(self):
        try:
            # Check if QEMU is installed
            if not self.is_tool(self.qemu_type_box.get()):
                alert(
                    "Unable to start the VM",
                    "It seems like QEMU is not installed on your system. Please install it and try again.",
                    icon="error",
                )
                return 1

            # Check if the CD-ROM file exists
            if not os.path.exists(self.cdrom_path.get()):
                alert(
                    "Unable to start the VM",
                    "The specified CD-ROM file does not exist",
                    icon="error",
                )
                return 1

            # Open QEMU in the background using subprocess.Popen()
            self.qemu_process = Popen(
                f"{self.qemu_type_box.get()} -cdrom {self.cdrom_path.get()} {'-sdl' if self.qemu_sdl_window.get() else ''} {'-accel hax' if self.qemu_use_haxm.get() else ''}",
                stdout=PIPE,
                stderr=PIPE,
            )

        except CalledProcessError as e:
            # TODO: Improve error messages
            alert(
                title="QEMU Returned an error",
                message=f"QEMU Returned an error: {str(e.output)}",
            )

    def get_first_file_with_ext(self, path, ext):
        # Loop through the specified directory and
        # find a file that has the specified extension
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(ext):
                    return file

        # Return an empty string if no file with the
        # specified extension was found
        return ""

    def not_implemented(self):
        alert("Not Implemented", "This feature has not been implemented yet :P")

    def create_menu_items(self):
        # Create the menu bar
        self.menubar = tk.Menu(self.root)

        # Adding File Menu and commands
        file = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file)
        file.add_command(label="Preferences...", command=self.not_implemented)
        file.add_separator()
        file.add_command(label="Exit", command=self.root.destroy)

        virtual_machine = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Machine", menu=virtual_machine)
        virtual_machine.add_command(label="Start", command=self.start_vm)
        virtual_machine.add_command(label="Terminate", command=self.kill_vm)

        tools = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools)
        tools.add_command(label="Create HDD Image", command=self.not_implemented)

        about = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=about)
        about.add_command(
            label="About",
            command=lambda: alert(
                "About",
                "QEMU Manager is a simple GUI frontend for QEMU written in TKinter and Python.\n\nCreated by yeppiidev",
            ),
        )

    def create_widgets(self):
        # Which formatter should I use to make this look better?
        title_label = ttk.Label(
            self.root,
            text="QEMU Manager",
            anchor="w",
            background=self.root.cget("background"),
            font=("Tahoma", 30),
        )
        title_label.pack(fill="both", padx=18, pady=18)

        # Add a button to start the VM
        self.start_vm_btn = ttk.Button(
            self.root, text="Start VM", command=self.start_vm
        )
        self.start_vm_btn.pack(ipadx=10, ipady=10, padx=10, pady=10)
        self.start_vm_btn.place(x=490, y=445)

        # Add a button to kill the VM
        self.kill_vm_btn = ttk.Button(
            self.root, text="Terminate QEMU", command=self.kill_vm
        )
        self.kill_vm_btn.pack(ipadx=10, ipady=10, padx=10, pady=10)
        self.kill_vm_btn.place(x=360, y=445)

        qemu_type_box_label = ttk.Label(
            self.root, text="CPU Architecture:", background=self.root.cget("background")
        )
        qemu_type_box_label.pack(fill="x", padx=15)

        self.qemu_type_box_value = tk.StringVar()
        self.qemu_type_box_value.set("qemu-system-i386")

        self.qemu_type_box = ttk.Combobox(
            self.root, state="readonly", textvariable=self.qemu_type_box_value
        )
        self.qemu_type_box["values"] = (
            "qemu-system-i386",
            "qemu-system-x86_64",
            "qemu-system-ppc",
            "qemu-system-ppc64",
        )
        self.qemu_type_box.current(1)
        self.qemu_type_box.pack(fill=tk.X, padx=15, pady=5)

        cdrom_path_label = ttk.Label(
            self.root,
            text="CD-ROM (ISO) File Path:",
            background=self.root.cget("background"),
        )
        cdrom_path_label.pack(fill="x", padx=15, pady=5)

        self.cdrom_path_text = tk.StringVar()
        self.cdrom_path_text.set(self.get_first_file_with_ext(os.getcwd(), ".iso"))

        self.cdrom_path = ttk.Entry(self.root, textvariable=self.cdrom_path_text)
        self.cdrom_path.pack(fill="x", padx=15)
        self.cdrom_path.focus()

        hdd_path_label = ttk.Label(
            self.root,
            text="HDD (QCOW2) File Path:",
            background=self.root.cget("background"),
        )
        hdd_path_label.pack(fill="x", padx=15, pady=5)

        self.hdd_path_text = tk.StringVar()
        self.hdd_path_text.set(self.get_first_file_with_ext(os.getcwd(), ".qcow2"))

        self.hdd_path_frame = tk.Frame(
            self.root, bg=self.root.cget("background"), width=450, height=50
        )
        self.hdd_path_frame.grid_columnconfigure(0, weight=1)

        self.hdd_path = ttk.Entry(self.hdd_path_frame, textvariable=self.hdd_path_text)
        self.hdd_path.grid(padx=(15, 0), row=0, column=0, columnspan=1, sticky="we")
        self.hdd_path.focus()

        self.create_hdd_btn = ttk.Button(
            self.hdd_path_frame, text="Create HDD", command=self.not_implemented
        )
        self.create_hdd_btn.grid(row=0, column=1, padx=(5, 15))

        self.hdd_path_frame.pack(fill="x")

        qemu_sdl_window = ttk.Checkbutton(
            self.root,
            text="Use SDL as the window library?",
            variable=self.qemu_sdl_window,
            offvalue=False,
            onvalue=True,
        )
        qemu_sdl_window.pack(fill="x", padx=15, pady=(10, 2))

        qemu_use_haxm = ttk.Checkbutton(
            self.root,
            text="Use Intel HAXM? (Requires you to have HAXM installed)",
            variable=self.qemu_use_haxm,
            offvalue=False,
            onvalue=True,
        )
        qemu_use_haxm.pack(fill="x", padx=15, pady=2)

        qemu_kill_on_exit_box = ttk.Checkbutton(
            self.root,
            text="Terminate QEMU on Exit?",
            variable=self.qemu_kill_on_exit,
            offvalue=False,
            onvalue=True,
        )
        qemu_kill_on_exit_box.pack(fill="x", padx=15, pady=2)

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
