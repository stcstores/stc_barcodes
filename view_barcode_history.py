
import os
from flask import Flask
import webbrowser
import json
import time

import stc_barcodes

app = Flask(__name__)


@app.route('/')
def load_page():
    barcode_dir = os.path.dirname(os.path.dirname(__file__))
    barcode_database = stc_barcodes.BarcodeDatabase(barcode_dir)

    template = barcode_database.get_template('order_history_template.html')
    orders = []
    for order in barcode_database.completed_orders:
        orders.append({
            'order_id': order.order_id,
            'date': order.date,
            'name': order.name,
            'email': order.email,
            'barcodes': order.barcodes
        })
    html = template.render(orders=json.dumps(orders))
    return html


def main():
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()

if __name__ == "__main__":
    main()
