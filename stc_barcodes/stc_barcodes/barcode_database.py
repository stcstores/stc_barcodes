import os
import sqlite3
import json
import shutil
import datetime

from jinja2 import Template

import pylinnworks

from . barcode_order import BarcodeOrder
from . staff_order import StaffBarcodeOrder


class LinnworksLoginError(IOError):
    def __init__(self, message):
        super(IOError, self).__init__(message)


class CompletedOrder:
    def __init__(self, order_id, date, name, email, barcodes=None):
        self.order_id = order_id
        self.date = date
        self.name = name
        self.email = email
        self.barcodes = []
        if barcodes is not None:
            self.barcodes = barcodes


class Barcode:
    def __init__(self, barcode, order_id=None):
        self.barcode = barcode
        self.ean = barcode
        self.upc = '0' + barcode
        self.order_id = order_id
        if self.order_id is None:
            self.used = False
        else:
            self.used = True

    def __str__(self):
        return self.barcode


class BarcodeDatabase:
    def __init__(self, barcode_dir):
        self.linn_orders = None
        self.barcode_orders = []
        self.barcode_dir = barcode_dir
        config_path = os.path.join(self.barcode_dir, 'settings.json')
        self.config = json.load(open(config_path, 'r'))
        self.template_path = self.config['TEMPLATE_PATH']
        self.database_filepath = os.path.join(
            self.barcode_dir, self.config['DB'])
        self.barcode_table = 'stc_barcodes'
        self.order_history_table = 'order_history'
        self.conn = sqlite3.connect(self.database_filepath)
        self.reload()

    def reload(self):
        self.clear()
        self.get_barcodes()
        self.get_orders()

    def backup(self, target=None):
        datestring = str(
            datetime.datetime.now()).replace(':', '-').replace('.', '-')
        backup_name = datestring + self.config['DB']
        targets = self.config['BACKUP_LOCATIONS']
        if target is not None:
            targets.append(target)
        for location in targets:
            shutil.copyfile(
                self.database_filepath, os.path.join(location, backup_name))
        return backup_name

    def new_customer_order(self, barcode_count, order_id):
        return BarcodeOrder(self, barcode_count, order_id)

    def new_staff_order(self, barcode_count, staff_name):
        return StaffBarcodeOrder(self, barcode_count, staff_name)

    def commit(self):
        self.backup()
        self.conn.commit()
        self.reload()

    def clear(self):
        self.barcodes = []
        self.used = []
        self.unused = []
        self.completed_orders = []
        self.completed_order_numbers = []

    def check_barcodes_available(self, count):
        if len(self.unused) < count:
            return False
        return True

    def allocate_barcodes(self, count):
        try:
            barcodes = self.unused[:count]
        except IndexError:
            raise ValueError('Insufficient barcodes available.')
        else:
            return barcodes

    def mark_barcodes_used(self, barcodes, order_id, name, date_string, email):
        for barcode in barcodes:
            self.mark_barcodes_used_query(barcode, order_id)
        self.insert_order_history_query(order_id, date_string, name, email)
        self.commit()
        self.get_barcodes()

    def insert_query(self, query, commit=True):
        self.conn.execute(query)
        if commit is True:
            self.commit()

    def update_query(self, query, commit=True):
        self.conn.execute(query)
        if commit is True:
            self.commit()

    def select_query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor

    def sqlite_string(self, value):
        string = str(value)
        quoted_string = '"{}"'.format(string)
        return quoted_string

    def get_barcodes_from_database_query(self):
        query = 'SELECT barcode, order_id FROM {}'.format(self.barcode_table)
        cursor = self.select_query(query)
        for record in cursor:
            yield {'barcode': record[0], 'order_id': record[1]}

    def get_orders_from_database_query(self):
        query = 'SELECT order_id, date, name, email FROM {}'.format(
            self.order_history_table)
        cursor = self.select_query(query)
        for record in cursor:
            yield {
                'order_id': record[0], 'date': record[1], 'name': record[2],
                'email': record[3]}

    def get_used_barcodes_by_order_query(self, order_id):
        query = 'SELECT barcode FROM {} WHERE order_id={}'.format(
            self.barcode_table, self.sqlite_string(order_id))
        cursor = self.select_query(query)
        for record in cursor:
            yield record[0]

    def add_barcodes_query(self, barcodes):
        insert_lines = ['({}, NULL)'.format(
            self.sqlite_string(barcode)) for barcode in barcodes]
        insert_string = ', '.join(insert_lines)
        query = 'INSERT into {} (barcode, order_id) VALUES {}'.format(
            self.barcode_table, insert_string)
        self.insert_query(query)

    def mark_barcodes_used_query(self, barcode, order_id):
        barcode_query = \
            "UPDATE {} SET order_id = {} WHERE barcode={}".format(
                self.barcode_table, self.sqlite_string(order_id),
                self.sqlite_string(barcode.ean))
        self.update_query(barcode_query, False)

    def insert_order_history_query(self, order_id, date_string, name, email):
        if email is None:
            insert_email = 'NULL'
        else:
            insert_email = self.sqlite_string(email)
        order_history_query = \
            "INSERT INTO {} (`order_id`,`date`,`name`,`email`) \
                VALUES ({}, {}, {}, {});".format(
                    self.order_history_table, self.sqlite_string(order_id),
                    self.sqlite_string(date_string), self.sqlite_string(name),
                    insert_email)
        self.insert_query(order_history_query, False)

    def get_template(self, template_name):
        template_path = os.path.join(self.template_path, template_name)
        with open(template_path, 'r') as template_file:
            template = Template(template_file.read())
        return template

    def get_barcodes(self):
        self.clear()
        for record in self.get_barcodes_from_database_query():
            barcode = Barcode(record['barcode'], record['order_id'])
            self.barcodes.append(barcode)
            if barcode.used:
                self.used.append(barcode)
            else:
                self.unused.append(barcode)

    def get_orders(self):
        self.completed_orders = []
        for record in self.get_orders_from_database_query():
            order = CompletedOrder(
                record['order_id'], record['date'], record['name'],
                record['email'])
            order.barcodes = list(
                self.get_used_barcodes_by_order_query(record['order_id']))
            self.completed_order_numbers.append(record['order_id'])
            self.completed_orders.append(order)

    def add_barcodes(self, barcodes):
        self.add_barcodes_query(barcodes)
        self.get_barcodes()

    def print_r(self):
        for row in self.get_all():
            print(row)
