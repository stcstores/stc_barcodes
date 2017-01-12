import datetime
import os

from . barcode_order import BarcodeOrder


class StaffBarcodeOrder(BarcodeOrder):
    def __init__(
            self, barcode_database, barcode_count, staff_name):
        self.barcode_database = barcode_database
        self.customer_name = staff_name
        self.customer_email = None
        self.barcode_count = barcode_count
        self.config = self.barcode_database.config
        self.date_string = str(
            datetime.datetime.now()).replace(':', '-').replace('.', '-')
        self.order_name = staff_name + ' ' + self.date_string
        self.reference = self.order_name

    def get_order_details(self):
        order_details = [
            'Staff member: ' + self.customer_name,
            'Barcode Count: ' + str(self.barcode_count),
            'Date Time: ' + self.date_string]
        return order_details
