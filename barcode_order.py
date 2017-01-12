
import sys
import os
import time
import re
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import stc_barcodes


class InputValues:
    def __init__(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def make_order(self):
        raise NotImplementedError

    def make_success_mesage(self):
        raise NotImplementedError

    def validate_barcode_count(self, barcode_count):
        message = []
        if '.' in barcode_count:
            message.append('Barcode Count is not a whole number')
        try:
            barcode_count = int(barcode_count)
        except:
            message.append("Barcode Count is not a number")
        else:
            if barcode_count < 1:
                message.append("Barcode Count must be greater than 1")
            if barcode_count > len(self.barcode_database.unused):
                message.append("Insufficient barcodes available")
        return message


class TextInput:
    def __init__(
            self, root, label, row=0, column=0, padx=0, pady=0, sticky=None):
        self.label = Label(root, text=label)
        self.value = StringVar(root)
        self.entry = Entry(root, textvariable=self.value)
        self.widgets = [self.label, self.entry]
        self.elements = [self.label, self.value, self.entry]
        self.label.grid(
            row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        self.entry.grid(
            row=row, column=column + 1, padx=padx, pady=pady, sticky=sticky)

    def set(self, value):
        self.value.set(value)

    def get(self):
        return self.value.get()


class BarcodeOrderApp:
    def __init__(self):
        self.root = Tk()
        self.script_dir = os.path.realpath(os.path.dirname(__file__))
        self.icon_dir = os.path.join(os.path.dirname(self.script_dir), 'Icons')
        self.root.iconbitmap(os.path.join(self.icon_dir, 'order.ico'))
        self.add_widgets()
        self.root.title(self.title)
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.save_dir = os.path.join(desktop, 'Barcode Order Files')
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
        self.barcode_dir = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        self.set_status("Loading barcode database", 'black')
        self.barcode_database = stc_barcodes.BarcodeDatabase(self.barcode_dir)

    def empty_save_dir(self):
        for file_object in os.listdir(self.save_dir):
            file_object_path = os.path.join(self.save_dir, file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

    def set_status(self, message, colour='black'):
        if isinstance(message, list):
            message = "\n".join(message)
        self.status_bar.configure(state='normal')
        self.status_bar.delete('1.0', END)
        self.status_bar.insert(END, message)
        self.status_bar.config(foreground=colour)
        self.status_bar.configure(state='disabled')

    def disable_inputs(self):
        for widget in self.get_inputs():
            widget.config(state='disabled')

    def enable_inputs(self):
        for widget in self.get_inputs():
            widget.config(state='normal')

    def confirm(self):
        self.disable_inputs()
        values = self.get_input_values()
        if values.valid is False:
            self.set_status(values.validation_message)
            self.enable_inputs()
            return False
        else:
            self.set_status('Information Valid', 'green')
            self.process_order(values)
            self.enable_inputs()

    def confirm_order(self, values):
        confirmation = messagebox.askquestion(
            "Confirm Barcode Order", values.confirm_message(), icon='question')
        if confirmation != 'yes':
            self.set_status('Canceled', 'red')
            return False
        return True

    def process_order(self, values):
        print('processing')
        values.make_order()
        if not self.confirm_order(values):
            return False
        table = values.order.commit()
        self.write_files(values.order)
        success_message = values.make_success_mesage()
        self.barcode_database.get_orders()
        self.clear()
        self.set_status(success_message)
        return True

    def cancel(self):
        self.root.destroy()

    def write_files(self, order):
        raise NotImplementedError

    def add_widgets(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def get_input_values(self):
        raise NotImplementedError

    def get_inputs(self):
        raise NotImplementedError


def main():
    app = BarcodeOrderApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
