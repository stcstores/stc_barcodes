
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import subprocess
import os

from barcode_order import BarcodeOrderApp, TextInput, InputValues


class BarcodeStaffOrderApp(BarcodeOrderApp):
    def __init__(self):
        self.title = 'Staff Barcode Order'
        super().__init__()
        self.set_status('Ready', 'green')

    def add_widgets(self):
        self.staff_name = TextInput(
            self.root, "Staff Name", row=1, column=0, padx=5, pady=5,
            sticky='EW')

        self.barcode_count = TextInput(
            self.root, "Barcode Count", row=3, column=0, padx=5, pady=5,
            sticky='EW')

        self.cancel_button = ttk.Button(
            self.root, text="Cancel", command=self.cancel)
        self.cancel_button.grid(
            row=4, column=0, sticky='EW', pady=5, padx=5)
        self.clear_button = ttk.Button(
            self.root, text="Clear", command=self.clear)
        self.clear_button.grid(
            row=4, column=1, sticky='EW', pady=5, padx=5)
        self.confirm_button = ttk.Button(
            self.root, text="Confirm", command=self.confirm)
        self.confirm_button.grid(
            row=4, column=2, sticky='EW', pady=5, padx=5)

        self.status_bar = Text(self.root)
        self.status_bar.config(state='normal')
        self.status_bar.grid(
            row=5, column=0, sticky='EW', pady=5, padx=5, columnspan=3,
            rowspan=4)

    def get_inputs(self):
        inputs = []
        inputs += self.staff_name.widgets
        inputs += self.barcode_count.widgets
        inputs.append(self.cancel_button)
        inputs.append(self.clear_button)
        inputs.append(self.confirm_button)
        return inputs

    def get_input_values(self):
        staff_name = self.staff_name.get()
        barcode_count = self.barcode_count.get()
        return StaffOrderValues(
            self.barcode_database, staff_name, barcode_count)

    def clear(self):
        self.staff_name.set('')
        self.barcode_count.set('')
        self.set_status('')

    def write_files(self, order):
        self.empty_save_dir()
        order.table.write(os.path.join(
            self.save_dir, "Barcodes For {} ({}).csv".format(
                order.customer_name, order.date_string)))
        subprocess.Popen('explorer "{}"'.format(self.save_dir))


class StaffOrderValues(InputValues):
    def __init__(self, barcode_database, staff_name, barcode_count):
        self.barcode_database = barcode_database
        self.staff_name = staff_name
        self.barcode_count = barcode_count
        self.validation_message = self.validate()
        if len(self.validation_message) > 0:
            self.valid = False
        else:
            self.valid = True

    def validate(self):
        message = []
        message += self.validate_staff_name(self.staff_name)
        message += self.validate_barcode_count(self.barcode_count)
        return message

    def validate_staff_name(self, staff_name):
        message = []
        if len(staff_name) < 3:
            message.append("Staff Name must be supplied")
        return message

    def confirm_message(self):
        confirmation_message = "\n".join([
            'Staff Name: {}'.format(self.order.customer_name),
            'Barcode Count: {}'.format(self.order.barcode_count),
            '',
            'Is this Correct?'
            ])
        return confirmation_message

    def make_order(self):
        order = self.barcode_database.new_staff_order(
            int(self.barcode_count), self.staff_name)
        order.get_barcodes()
        self.order = order

    def make_success_mesage(self):
        order = self.order
        success_message = [
            'Order completed',
            'Staff Name: {}'.format(order.customer_name),
            'Barcode Count: {}'.format(order.barcode_count),
            'Reference: {}'.format(order.reference)]
        return success_message


def main():
    app = BarcodeStaffOrderApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
