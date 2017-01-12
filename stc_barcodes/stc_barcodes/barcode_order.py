import datetime
import os

from jinja2 import Template
import pdfkit

from tabler import Tabler


class BarcodeOrder:
    def __init__(
            self, barcode_database, barcode_count, order_id):
        self.barcode_database = barcode_database
        self.order_id = order_id
        self.customer_name = None
        self.customer_email = None
        self.barcode_count = barcode_count
        self.config = self.barcode_database.config
        self.date_string = str(
            datetime.datetime.now()).replace(':', '-').replace('.', '-')
        self.order_name = order_id + ' ' + self.date_string
        self.reference = self.order_id

    def barcodes_available(self):
        return self.barcode_database.check_barcodes_available(
            self.barcode_count)

    def get_barcodes(self):
        self.barcodes = self.barcode_database.allocate_barcodes(
            self.barcode_count)
        self.make_table

    def make_table(self):
        self.table = Tabler(header=['EAN'])
        for barcode in self.barcodes:
            self.table.append([barcode.ean])

    def commit(self):
        self.make_table()
        barcodes = self.barcodes
        order_id = self.reference
        name = self.customer_name
        date_string = self.date_string
        email = self.customer_email

        self.barcode_database.mark_barcodes_used(
            barcodes, order_id, name, date_string, email)
        self.save_order_log()
        return self.table

    def make_printable_html(self):
        row_count = 3
        barcodes = [barcode.ean for barcode in self.barcodes]
        barcode_rows = [[
            [str(barcodes.index(
                barcode) + 1), barcode] for barcode in barcodes[
                i: i + row_count]] for i in range(
                0, len(barcodes), row_count)]
        template = self.barcode_database.get_template(
            'barcode_print_template.html')

        html = template.render(
            reference=self.reference, date=self.date_string[:10],
            barcode_count=self.barcode_count, barcode_rows=barcode_rows)
        return html

    def get_order_details(self):
        order_details = [
            'Order ID: ' + self.order_id,
            'Barcode Count: ' + str(self.barcode_count)]
        if self.customer_name is not None:
            order_details.append('Customer Name: ' + self.customer_name)
        if self.customer_email is not None:
            order_details.append('Customer Email: ' + self.customer_email)
        return order_details

    def save_order_log(self):
        print('saving')
        print('Locations:')
        print(self.config['ORDER_LOG_LOCATIONS'])
        print()
        order_details = self.get_order_details()
        folder_name = ' - '.join([self.date_string, self.reference])
        for location in list(set(self.config['ORDER_LOG_LOCATIONS'])):
            print(location)
            order_folder = os.path.join(location, folder_name)
            os.mkdir(order_folder)
            self.table.write(
                os.path.join(order_folder, self.order_name + '.csv'))
            info_filename = os.path.join(
                order_folder, self.order_name + '_info.txt')
            with open(info_filename, 'w') as order_info:
                order_info.writelines(
                    ["{}\n".format(line) for line in order_details])
            printable_filename = os.path.join(
                order_folder, self.reference + '_printable.pdf')
            html = self.make_printable_html()
            pdfkit.from_string(html, printable_filename)
