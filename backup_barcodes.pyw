
from tkinter import *
from tkinter import ttk
import os
import time
import win32api

import stc_barcodes


class Drive():
    def __init__(self, letter, name):
        self.letter = letter
        self.name = name
        self.text = self.name + ' (' + self.letter + ')'

    def __str__(self):
        return self.text


class BarcodeBackupApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Barcode Backup")
        self.load_barcode_database()
        self.set_icon()
        self.location_select_window()

    def set_icon(self):
        icon_path = os.path.join(self.barcode_dir, 'Icons', 'backup.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

    def location_select_window(self):
        style = ttk.Style()
        style.configure('vista')
        self.drives = self.get_drive_list()
        self.drive_list = [x.text for x in self.drives]
        self.drive_lookup = {x.text: x for x in self.drives}
        self.text = ttk.Label(self.root, text="Target")
        self.drive_options = ttk.Combobox(
            self.root, values=self.drive_list, state="readonly")
        self.drive_options.current(0)
        self.backup_button = ttk.Button(
            self.root, text='Backup', command=lambda: self.backup(None))
        self.text.grid(row=0, column=0, padx=10, pady=10, sticky='EW')
        self.drive_options.grid(
            row=0, column=1, padx=10, pady=10, sticky='EW')
        self.backup_button.grid(
            row=0, column=3, padx=10, pady=10, sticky='EW')
        self.feedback_text = StringVar()
        self.feedback_box = ttk.Entry(
            self.root, textvariable=self.feedback_text, state="readonly")
        self.feedback_box.grid(
            row=1, column=0, columnspan=4, padx=10, pady=10, sticky='EW')

    def give_feedback(self, message):
        self.feedback_text.set(message)

    def backup(self, event):
        target_dir = self.get_backup_location()
        self.give_feedback('Backing up to ' + target_dir)
        backup_name = self.barcode_database.backup(target_dir)
        self.check_backup_successful(target_dir, backup_name)

    def get_backup_location(self):
        option = self.drive_options.get()
        drive = self.drive_lookup[option]
        target_dir = os.path.join(drive.letter, 'Barcode Backup')
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        return target_dir

    def check_backup_successful(self, target_dir, backup_name):
        if os.path.exists(os.path.join(target_dir, backup_name)):
            self.give_feedback("Backup Successfull")
            return True
        self.give_feedback("Backup Failed!")
        return False

    def load_barcode_database(self):
        self.barcode_dir = os.path.dirname(os.path.dirname(__file__))
        self.barcode_database = stc_barcodes.BarcodeDatabase(self.barcode_dir)

    def get_drive_list(self):
        drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        drives = []
        for letter in drive_letters:
            try:
                volume_label = win32api.GetVolumeInformation(letter)[0]
            except:
                pass
            else:
                drives.append(Drive(letter, volume_label))
        return drives


if __name__ == "__main__":
    app = BarcodeBackupApp()
    app.root.mainloop()
