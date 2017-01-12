
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os
import subprocess

import pdfkit

from barcode_order import BarcodeOrderApp, TextInput, InputValues


class BarcodeCustomerOrderApp(BarcodeOrderApp):
    def __init__(self):
        self.title = 'Customer Barcode Order'
        super().__init__()
        self.load_linnworks_orders()
        if self.linnworks_orders_loaded is False:
            self.set_status("Linnworks Orders Unavailable", 'red')
        else:
            self.set_status('Ready', 'green')

    def load_linnworks_orders(self):
        try:
            import pylinnworks
            api_session = pylinnworks.LinnworksAPISession()
            self.linnworks_orders = pylinnworks.orders.OpenOrders(
                api_session, load=True)
            self.linnworks_orders_loaded = True
        except Exception as error:
            print(repr(error))
            self.order_search_button.config(state='disabled')
            self.order_number.entry.bind('<Return>', None)
            self.linnworks_orders_loaded = False

    def add_widgets(self):
        self.order_number = TextInput(
            self.root, "Order Number", row=0, column=0, padx=5, pady=5,
            sticky='EW')
        self.order_number.entry.bind("<Return>", self.search_orders)
        self.order_search_button = ttk.Button(
            self.root, text="Search", command=self.search_orders)
        self.order_search_button.grid(
            row=0, column=2, sticky='EW', pady=5, padx=5)

        self.customer_name = TextInput(
            self.root, "Customer Name", row=1, column=0, padx=5, pady=5,
            sticky='EW')

        self.customer_email = TextInput(
            self.root, "Customer Email", row=2, column=0, padx=5, pady=5,
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
        inputs += self.order_number.widgets
        inputs += self.customer_name.widgets
        inputs += self.customer_email.widgets
        inputs += self.barcode_count.widgets
        inputs.append(self.cancel_button)
        inputs.append(self.clear_button)
        inputs.append(self.confirm_button)
        return inputs

    def get_input_values(self):
        order_number = self.order_number.get()
        customer_name = self.customer_name.get()
        customer_email = self.customer_email.get()
        barcode_count = self.barcode_count.get()
        return CustomerOrderValues(
            self.barcode_database, order_number, customer_name, customer_email,
            barcode_count)

    def search_orders(self, event=None):
        order_number = self.order_number.get()
        if self.linnworks_orders_loaded is True:
            try:
                linn_order = self.linnworks_orders[order_number]
            except:
                self.set_status("Order not found", 'Orange')
            else:
                message = []
                message.append(
                    "Order {} found".format(linn_order.order_number))
                message.append(
                    "Customer Name: {}".format(linn_order.customer_name))
                message.append('')
                message.append("Items:")
                for item in linn_order.items:
                    if item.quantity == 1:
                        message.append(''.join([item.sku, ' - ', item.title]))
                    else:
                        message.append(''.join([
                            str(item.quantity), 'x ', item.sku, ' - ',
                            item.title]))
                self.clear()
                self.order_number.set(linn_order.order_number)
                self.customer_name.set(linn_order.customer_name)
                self.customer_email.set(linn_order.customer_email)
                self.set_status(message, 'black')

    def clear(self):
        self.order_number.set('')
        self.customer_name.set('')
        self.customer_email.set('')
        self.barcode_count.set('')
        self.set_status('')

    def write_files(self, order):
        self.empty_save_dir()
        order.table.write(os.path.join(
            self.save_dir, "Barcode Order {}.csv".format(order.order_id)))
        print_file_name = os.path.join(
            self.save_dir, '{} barcodes printable.pdf'.format(
                order.order_id))
        html = order.make_printable_html()
        pdfkit.from_string(html, print_file_name)
        subprocess.Popen('explorer "{}"'.format(self.save_dir))


class CustomerOrderValues(InputValues):
    def __init__(self, barcode_database, order_number, customer_name,
                 customer_email, barcode_count):
        self.barcode_database = barcode_database
        self.order_number = order_number
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.barcode_count = barcode_count
        self.validation_message = self.validate()
        if len(self.validation_message) > 0:
            self.valid = False
        else:
            self.valid = True

    def validate(self):
        message = []
        message += self.validate_order_number(self.order_number)
        message += self.validate_customer_name(self.customer_name)
        message += self.validate_barcode_count(self.barcode_count)
        return message

    def validate_order_number(self, order_number):
        message = []
        if len(order_number) < 3:
            message.append("Order Number must be supplied")
        elif order_number in \
                self.barcode_database.completed_order_numbers:
            message.append('Order Number already completed')
        else:
            try:
                int(order_number)
            except:
                message.append("Order Number is not valid")
        return message

    def validate_customer_name(self, customer_name):
        message = []
        if len(customer_name) < 3:
            message.append("Customer Name must be supplied")
        return message

    def confirm_message(self):
        confirmation_message = "\n".join([
            'Order Number: {}'.format(self.order.order_id),
            'Customer Name: {}'.format(self.order.customer_name),
            'Customer Email: {}'.format(self.order.customer_email),
            'Barcode Count: {}'.format(self.order.barcode_count),
            '',
            'Is this Correct?'
            ])
        return confirmation_message

    def make_order(self):
        order = self.barcode_database.new_customer_order(
            int(self.barcode_count), self.order_number)
        order.customer_name = self.customer_name
        order.customer_email = self.customer_email
        order.get_barcodes()
        self.order = order

    def make_success_mesage(self):
        order = self.order
        success_message = [
            'Order completed',
            'Order Number: {}'.format(order.order_id),
            'Customer Name: {}'.format(order.customer_name),
            'Customer Email: {}'.format(order.customer_email),
            'Barcode Count: {}'.format(len(order.barcodes))]
        return success_message


if __name__ == "__main__":
    app = BarcodeCustomerOrderApp()
    app.root.mainloop()
