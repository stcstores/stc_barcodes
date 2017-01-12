
import sys
import os
import time
import re
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from sqlite3 import IntegrityError

import stc_barcodes
from tabler import Tabler


class AddBarcodesApp:
    def __init__(self):
        self.root = Tk()
        self.script_dir = os.path.realpath(os.path.dirname(__file__))
        self.icon_dir = os.path.join(os.path.dirname(self.script_dir), 'Icons')
        self.root.iconbitmap(os.path.join(self.icon_dir, 'add.ico'))
        self.root.title('Add Barcodes')
        self.barcode_dir = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        self.barcode_database = stc_barcodes.BarcodeDatabase(
            self.barcode_dir)
        self.add_widgets()
        home_folder = os.path.expanduser('~')
        desktop = os.path.join(home_folder, 'Desktop')
        if os.path.exists(desktop):
            self.open_dir = desktop
        else:
            self.open_dir = home_folder

    def add_widgets(self):
        self.open_label = Label(self.root, text='Open barcode import files: ')
        self.open_label.grid(row=0, column=0)
        self.open_button = ttk.Button(
            self.root, text='Open', command=self.get_files)
        self.open_button.grid(row=0, column=1)
        self.status_bar = Text(self.root)
        self.status_bar.config(state='normal')
        self.status_bar.grid(
            row=1, column=0, sticky='EW', pady=5, padx=5, columnspan=3,
            rowspan=4)

    def set_status(self, message, colour='black'):
        if isinstance(message, list):
            message = "\n".join(message)
        self.status_bar.configure(state='normal')
        self.status_bar.delete('1.0', END)
        self.status_bar.insert(END, message)
        self.status_bar.config(foreground=colour)
        self.status_bar.configure(state='disabled')

    def get_files(self):
        filenames = filedialog.askopenfilenames(
            defaultextension='.csv', initialdir=self.open_dir)
        barcode_files = []
        for filename in filenames:
            barcode_files.append(Tabler(filename))
        self.save_barcodes(barcode_files)

    def is_barcode(self, barcode):
        if len(barcode) == 13:
            if barcode.isdigit():
                return True
        return False

    def save_barcodes(self, barcode_files):
        barcodes = []
        errors = []
        for barcode_file in barcode_files:
            for row in barcode_file:
                barcode = str(row[0])
                if self.is_barcode(barcode):
                    barcodes.append(barcode)
                else:
                    row_number = barcode_file.rows.index(row)
                    file_name = os.path.basename(barcode_file)
                    errors.append(
                        'Row {} in file {}: {} is not a valid EAN barcode'
                    ).format(
                        row_number, file_name, barcode)
        if len(errors) == 0:
            try:
                self.barcode_database.add_barcodes(barcodes)
            except IntegrityError:
                self.set_status(
                    'Barcode in import already present in database', 'red')
            else:
                self.set_status(
                    "{} barcodes added to database.".format(
                        str(len(barcodes))),
                    'green')
        else:
            self.set_status(errors, 'red')


def main():
    app = AddBarcodesApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
