class Script:
    def __init__(
            self, filename, shortcut_name, icon_name=None, app=False,
            shortcut=False):
        self.filename = filename
        self.shortcut_name = shortcut_name
        self.icon_name = icon_name
        self.app = app
        self.shortcut = shortcut


scripts = [
    Script(
        'barcode_customer_order.pyw', 'Customer Order',
        icon_name='order', app=True),
    Script(
        'barcode_order.py', None),
    Script(
        'barcode_staff_order.pyw', 'Staff Order',
        icon_name='order', app=True),
    Script(
        'add_barcodes.pyw', 'Add Barcodes', icon_name='add', app=True),
    Script(
        'view_barcode_history.py', 'Order History',
        icon_name='history', app=True),
    Script(
        'backup_barcodes.pyw', 'Backup Barcodes',
        icon_name='backup', app=True),
    Script(
        'barcode_gui.pyw', 'Barcode Database',
        icon_name='barcode', app=True, shortcut=True), ]
