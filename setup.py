#!python3

import os
import sys
import json
import sqlite3
import shutil
import site
import datetime
import virtualenv

from win32com.client import Dispatch

from scripts import scripts


class BarcodeSetup():
    def __init__(self, target_dir):
        self.package_name = 'stc_barcodes'
        self.source_dir = os.path.realpath(os.path.dirname(__file__))
        self.target_dir = target_dir

    def set_directories(self):
        self.desktop = os.path.join(
            os.path.expanduser("~"), 'Desktop')
        self.site_packages_dir = site.getsitepackages()[1]
        self.package = os.path.join(self.source_dir, self.package_name)
        self.python_target_dir = os.path.join(self.target_dir, 'Python')
        self.icon_source_dir = os.path.join(self.source_dir, 'icons')
        self.icon_target_dir = os.path.join(self.target_dir, 'Icons')
        self.template_source_dir = os.path.join(self.source_dir, 'templates')
        self.template_target_dir = os.path.join(self.target_dir, 'Templates')
        self.config_file = os.path.join(self.target_dir, 'settings.json')
        self.backup_dir = os.path.join(self.target_dir, 'Backup')
        self.order_log_dir = os.path.join(self.target_dir, 'Order Logs')
        self.env_dir = os.path.join(self.target_dir, 'env')
        self.scripts = scripts

    def create_environment(self):
        if os.path.exists(self.env_dir):
            try:
                shutil.rmtree(self.env_dir)
            except:
                raise Exception('Existing environment cannot be removed')
        virtualenv.create_environment(self.env_dir)

    def install_requirements(self):
        requirements_path = os.path.join(self.source_dir, 'requirements.txt')
        with open(requirements_path, 'r') as requirements_file:
            requirements = requirements_file.readlines()
        for requirement in requirements:
            self.install_requirement(requirement)

    def add_api_token(self):
        token = input('Linnworks Token: ')
        executable = os.path.join(self.env_dir, 'Scripts/python.exe')
        script = os.path.join(
            self.env_dir, 'Lib/site-packages/pylinnworks/update_token.py')
        command = ' '.join([executable, script, token])
        os.system(command)

    def install(self):
        print("Installing database to " + target_dir)
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)
        self.set_directories()
        self.create_config_file()
        self.make_dirs()
        self.install_scripts()
        self.create_database()
        self.install_templates()
        self.create_environment()
        self.install_package('pylinnworks')
        self.install_package('stc_barcodes')
        self.install_requirements()
        self.add_api_token()
        shutil.copyfile(
            os.path.join(self.source_dir, 'scripts.py'),
            os.path.join(self.python_target_dir, 'scripts.py'))

    def create_config_file(self):
        default_config = self.get_default_config()
        if os.path.exists(self.config_file):
            existing_config = json.load(open(self.config_file, 'r'))
            self.config = self.merge_dicts(existing_config, default_config)
        else:
            self.config = default_config
        json.dump(
            self.config, open(self.config_file, 'w'), indent=4, sort_keys=True)

    def install_scripts(self):
        for script in self.scripts:
            self.install_script(script)

    def install_script(self, script):
        script_path = os.path.join(self.source_dir, script.filename)
        script_target = os.path.join(self.python_target_dir, script.filename)
        self.copy_script(script_path, script_target)
        filetypes = ('.ico', '.png', '.gif')
        if script.icon_name is not None:
            for filetype in filetypes:
                icon_file = os.path.join(
                    self.icon_source_dir, script.icon_name + filetype)
                icon_target = os.path.join(
                    self.icon_target_dir, script.icon_name + filetype)
                shutil.copyfile(icon_file, icon_target)
            icon_target = os.path.join(
                self.icon_target_dir, script.icon_name + '.ico')
        else:
            icon_target = None
        if script.shortcut is True:
            print("Creating shortcut for {}".format(script.shortcut_name))
            self.create_shortcut(
                script_target, script.shortcut_name, location=self.desktop,
                working_dir=self.desktop, icon=icon_target)

    def copy_script(self, script_path, script_target):
        if script_path[-1] == 'w':
            exe = 'pythonw.exe'
        else:
            exe = 'python.exe'
        shebang = os.path.join(self.env_dir, 'Scripts', exe)
        with open(script_path, 'r') as original_script:
            data = original_script.read()
        with open(script_target, 'w') as modified_script:
            modified_script.write("#!{}\n{}".format(shebang, data))

    def make_dirs(self):
        required_target_directories = [
            self.python_target_dir,
            self.template_target_dir,
            self.icon_target_dir]

        dirs_to_make = required_target_directories + self.config[
            'BACKUP_LOCATIONS'] + self.config['ORDER_LOG_LOCATIONS']

        for directory in dirs_to_make:
            if not os.path.exists(directory):
                os.mkdir(directory)

    def get_default_config(self):
        default_config = {
            'DB': 'stc_barcodes.db',
            'DB_TABLE': 'stc_barcodes',
            'TEMPLATE_PATH': self.template_target_dir,
            'PRINT_TEMPLATE_NAME': 'barcode_print_template.html',
            'INSTALL_PATH': self.target_dir,
            'BACKUP_LOCATIONS': [self.backup_dir],
            'ORDER_LOG_LOCATIONS': [self.order_log_dir]}
        return default_config

    def create_database(self):
        self.database_path = os.path.join(self.target_dir, self.config['DB'])
        if not os.path.exists(self.database_path):
            conn = sqlite3.connect(self.database_path)
            create_barcode_table_query = (
                'CREATE TABLE ' + self.config['DB_TABLE'] +
                ' (barcode TEXT PRIMARY KEY, order_id TEXT NULL);')
            create_order_history_table_query = (
                'CREATE TABLE `order_history` (' +
                '`order_id`	TEXT NOT NULL,' +
                '`date`	TEXT NOT NULL,' +
                '`name`	TEXT NOT NULL,' +
                '`email`	TEXT,' +
                'PRIMARY KEY(order_id)' +
                ');')
            conn.execute(create_barcode_table_query)
            conn.execute(create_order_history_table_query)
            print("Created " + self.database_path)
        else:
            datestring = str(
                datetime.datetime.now()).replace(':', '-').replace('.', '-')
            backup_name = datestring + self.config['DB']
            for location in self.config['BACKUP_LOCATIONS']:
                shutil.copyfile(
                    self.database_path, os.path.join(location, backup_name))

    def install_templates(self):
        templates = os.listdir(self.template_source_dir)
        for template in templates:
            template_file = os.path.join(self.template_source_dir, template)
            template_target = os.path.join(self.template_target_dir, template)
            shutil.copyfile(template_file, template_target)

    def install_package(self, package_name):
        cwd = os.getcwd()
        executable = os.path.join(self.env_dir, 'Scripts/python.exe')
        package_path = os.path.join(self.source_dir, package_name)
        os.chdir(package_path)
        script = os.path.join(package_path, 'setup.py')
        command = executable + " " + script + " install"
        os.system(command)
        os.chdir(cwd)

    def install_requirement(self, package_name):
        executable = os.path.join(self.env_dir, 'Scripts/pip.exe')
        command = executable + " install " + package_name
        os.system(command)

    def create_shortcut(
            self, target, name, location=None, working_dir=None, icon=None):
        if location is None:
            location = os.path.join(os.path.expanduser("~"), 'Desktop')
        if working_dir is None:
            working_dir = location
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(os.path.join(location, name + '.lnk'))
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = working_dir
        if icon is not None:
            shortcut.IconLocation = icon
        shortcut.save()

    def merge_dicts(self, old_dict, new_dict):
        merge_dict = {}
        for entry in new_dict:
            if entry not in old_dict:
                merge_dict[entry] = new_dict[entry]
            elif isinstance(new_dict[entry], dict):
                if isinstance(old_dict[entry], dict):
                    merge_dict[entry] = merge_dicts(
                        old_dict[entry], new_dict[entry])
                else:
                    merge_dict[entry] = new_dict[entry]
            elif isinstance(new_dict[entry], list):
                if isinstance(old_dict[entry], list):
                    merge_dict[entry] = list(
                        set(old_dict[entry] + new_dict[entry]))
                else:
                    merge_dict[entry] = new_dict[entry]
            else:
                merge_dict[entry] = old_dict[entry]
        return merge_dict


if __name__ == "__main__":
    if os.path.exists(sys.argv[0]):
        target_dir = os.path.join(sys.argv[1], 'Barcodes')
        installer = BarcodeSetup(target_dir)
        installer.install()

    else:
        print("No install location selected")
        exit()
