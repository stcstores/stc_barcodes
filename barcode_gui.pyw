
import os
from tkinter import *
from tkinter import ttk
import base64
import sys
import subprocess

import stc_barcodes
from scripts import scripts


class BarcodeGui:
    def __init__(self):
        self.root = Tk()
        self.barcode_dir = os.path.dirname(os.path.dirname(__file__))
        self.barcode_database = stc_barcodes.BarcodeDatabase(self.barcode_dir)
        self.root.title('Barcode Database')
        self.style = ttk.Style()
        self.style.configure('.', font=(None, 16), justify='left')
        self.scripts = scripts
        self.script_dir = os.path.realpath(os.path.dirname(__file__))
        self.icon_dir = os.path.join(os.path.dirname(self.script_dir), 'Icons')
        self.root.iconbitmap(os.path.join(self.icon_dir, 'barcode.ico'))
        self.buttons = []
        self.label_text_size = 16

        for script in self.scripts:
            if script.app is True:
                if script.filename == os.path.basename(sys.argv[0]):
                    continue
                name = script.shortcut_name
                command = self.get_command_for_script(script)
                icon_path = os.path.join(
                    self.icon_dir, script.icon_name + '.gif')
                script.button = ttk.Button(self.root, text=name)
                icon_image = PhotoImage(file=icon_path)
                script.button.image = icon_image
                script.button.configure(
                    image=icon_image, width="20", compound="top",
                    command=lambda command=command: self.run_command(command))
                self.buttons.append(script.button)
        row = 0
        for widget in self.buttons:
            widget.grid(
                row=row, column=0, sticky='EW', pady=5)
            row += 1

        self.status = Frame(self.root)
        self.status.grid(row=0, column=1, columnspan=len(self.scripts) - 1)
        self.total_barcodes_string = StringVar(self.status)
        self.total_barcodes_label = Label(
            self.status, text="Total Barcodes:")
        self.total_barcodes_label.config(font=(None, self.label_text_size))
        self.total_barcodes_label.grid(
            row=0, column=0, sticky='EW', pady=5, padx=5)
        self.total_barcodes_value = Label(
            self.status, textvariable=self.total_barcodes_string)
        self.total_barcodes_value.grid(
            row=0, column=1, sticky='EW', pady=5, padx=5)
        self.total_barcodes_value.config(font=(None, self.label_text_size))

        self.used_barcodes_string = StringVar(self.status)
        self.used_barcodes_label = Label(
            self.status, text="Used Barcodes:")
        self.used_barcodes_label.config(font=(None, self.label_text_size))
        self.used_barcodes_label.grid(
            row=1, column=0, sticky='EW', pady=5, padx=5)
        self.used_barcodes_value = Label(
            self.status, textvariable=self.used_barcodes_string)
        self.used_barcodes_value.grid(
            row=1, column=1, sticky='EW', pady=5, padx=5)
        self.used_barcodes_value.config(font=(None, self.label_text_size))

        self.unused_barcodes_string = StringVar(self.status)
        self.unused_barcodes_label = Label(
            self.status, text="Unused Barcodes:")
        self.unused_barcodes_label.config(font=(None, self.label_text_size))
        self.unused_barcodes_label.grid(
            row=3, column=0, sticky='EW', pady=5, padx=5)
        self.unused_barcodes_value = Label(
            self.status, textvariable=self.unused_barcodes_string)
        self.unused_barcodes_value.grid(
            row=3, column=1, sticky='EW', pady=5, padx=5)
        self.unused_barcodes_value.config(font=(None, self.label_text_size))

        self.refresh_status_button = ttk.Button(
            self.status, text="Refresh", command=self.get_status)
        self.refresh_status_button.grid(row=4, column=0, columnspan=2)

        self.get_status()

    def get_status(self):
        self.barcode_database.reload()
        self.barcode_count = len(self.barcode_database.barcodes)
        print(self.barcode_count)
        self.used_barcode_count = len(self.barcode_database.used)
        print(self.used_barcode_count)
        self.unused_barcode_count = len(self.barcode_database.unused)
        print(self.unused_barcode_count)
        self.total_barcodes_string.set(str(self.barcode_count))
        self.used_barcodes_string.set(str(self.used_barcode_count))
        self.unused_barcodes_string.set(str(self.unused_barcode_count))

    def get_command_for_script(self, script):
        script_path = os.path.join(self.script_dir, script.filename)
        if '.pyw' in script.filename:
            command = 'python ' + script_path
        else:
            command = script_path
        return command

    def run_command(self, command):
        if '.pyw' in command:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.call(command, startupinfo=si)
        else:
            os.system(command)
        self.get_status()


if __name__ == "__main__":
    app = BarcodeGui()
    app.root.mainloop()
