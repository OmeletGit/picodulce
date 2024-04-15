import sys
import subprocess
import picomc
from PyQt5.QtWidgets import QApplication, QComboBox, QWidget, QVBoxLayout, QPushButton, QMessageBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QCheckBox
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt


class PicomcVersionSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PicoDulce Launcher')  
        self.setWindowIcon(QIcon('launcher_icon.ico'))  # Set window icon
        self.setGeometry(100, 100, 400, 250)

        # Create title label
        title_label = QLabel('PicoDulce Launcher')  
        title_label.setFont(QFont("Arial", 24, QFont.Bold))

        # Create installed versions section
        installed_versions_label = QLabel('Installed Versions:')
        installed_versions_label.setFont(QFont("Arial", 14))
        self.installed_version_combo = QComboBox()
        self.installed_version_combo.setMinimumWidth(200)
        self.populate_installed_versions()

        # Create buttons layout
        buttons_layout = QVBoxLayout()

        # Create play button for installed versions
        self.play_button = QPushButton('Play')
        self.play_button.setFocusPolicy(Qt.NoFocus)  # Set focus policy to prevent highlighting
        self.play_button.clicked.connect(self.play_instance)
        self.play_button.setStyleSheet("background-color: #1E90FF; color: white;")
        buttons_layout.addWidget(self.play_button)

        # Create button to open version download menu
        self.version_download_button = QPushButton('Download Version')
        self.version_download_button.clicked.connect(self.open_version_menu)
        buttons_layout.addWidget(self.version_download_button)

        # Create button to manage accounts
        self.manage_accounts_button = QPushButton('Manage Accounts')
        self.manage_accounts_button.clicked.connect(self.manage_accounts)
        buttons_layout.addWidget(self.manage_accounts_button)

        # Create About button
        self.about_button = QPushButton('About')
        self.about_button.clicked.connect(self.show_about_dialog)
        buttons_layout.addWidget(self.about_button)

        # Set buttons layout alignment and spacing
        buttons_layout.setAlignment(Qt.AlignTop)
        buttons_layout.setSpacing(10)

        # Set layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(installed_versions_label)
        main_layout.addWidget(self.installed_version_combo)
        main_layout.addLayout(buttons_layout)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        self.setLayout(main_layout)

    def populate_installed_versions(self):
        # Run the command and get the output
        try:
            process = subprocess.Popen(['picomc', 'version', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, error)
        except FileNotFoundError:
            print("Error: 'picomc' command not found. Please make sure it's installed and in your PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
            sys.exit(1)

        # Parse the output and replace '[local]' with a space
        versions = output.splitlines()
        versions = [version.replace('[local]', ' ').strip() for version in versions]

        # Populate installed versions combo box
        self.installed_version_combo.clear()
        self.installed_version_combo.addItems(versions)

    def play_instance(self):
        selected_instance = self.installed_version_combo.currentText()
        try:
            subprocess.run(['picomc', 'play', selected_instance], check=True)
        except subprocess.CalledProcessError as e:
            error_message = f"Error playing {selected_instance}: {e.stderr.decode()}"
            QMessageBox.critical(self, "Error", error_message)

    def open_version_menu(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Download Version')
        dialog.setFixedSize(300, 250)

        # Create title label
        title_label = QLabel('Download Version')
        title_label.setFont(QFont("Arial", 14))

        # Create checkboxes for different version types
        release_checkbox = QCheckBox('Releases')
        snapshot_checkbox = QCheckBox('Snapshots')
        alpha_checkbox = QCheckBox('Alpha')
        beta_checkbox = QCheckBox('Beta')

        # Create dropdown menu for versions
        version_combo = QComboBox()

        def update_versions():
            version_combo.clear()
            options = []
            if release_checkbox.isChecked():
                options.append('--release')
            if snapshot_checkbox.isChecked():
                options.append('--snapshot')
            if alpha_checkbox.isChecked():
                options.append('--alpha')
            if beta_checkbox.isChecked():
                options.append('--beta')
            if options:
                try:
                    process = subprocess.Popen(['picomc', 'version', 'list'] + options, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    output, error = process.communicate()
                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, process.args, error)
                except FileNotFoundError:
                    print("Error: 'picomc' command not found. Please make sure it's installed and in your PATH.")
                    sys.exit(1)
                except subprocess.CalledProcessError as e:
                    print("Error:", e.stderr)
                    sys.exit(1)

                # Parse the output and replace '[local]' with a space
                versions = output.splitlines()
                versions = [version.replace('[local]', ' ').strip() for version in versions]
                version_combo.addItems(versions)

        release_checkbox.clicked.connect(update_versions)
        snapshot_checkbox.clicked.connect(update_versions)
        alpha_checkbox.clicked.connect(update_versions)
        beta_checkbox.clicked.connect(update_versions)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(release_checkbox)
        layout.addWidget(snapshot_checkbox)
        layout.addWidget(alpha_checkbox)
        layout.addWidget(beta_checkbox)
        layout.addWidget(version_combo)

        # Create download button
        download_button = QPushButton('Download')
        download_button.clicked.connect(lambda: self.prepare_version(dialog, version_combo.currentText()))

        layout.addWidget(download_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def prepare_version(self, dialog, version):
        dialog.close()
        try:
            subprocess.run(['picomc', 'version', 'prepare', version], check=True)
            QMessageBox.information(self, "Success", f"Version {version} prepared successfully!")
            self.populate_installed_versions()  # Refresh the installed versions list after downloading
        except subprocess.CalledProcessError as e:
            error_message = f"Error preparing {version}: {e.stderr.decode()}"
            QMessageBox.critical(self, "Error", error_message)

    def manage_accounts(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Manage Accounts')
        dialog.setFixedSize(300, 150)

        # Create title label
        title_label = QLabel('Manage Accounts')
        title_label.setFont(QFont("Arial", 14))

        # Create dropdown menu for accounts
        account_combo = QComboBox()
        self.populate_accounts(account_combo)

        # Create select button
        select_button = QPushButton('Select')
        select_button.clicked.connect(lambda: self.set_default_account(dialog, account_combo.currentText()))

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(account_combo)
        layout.addWidget(select_button)

        # Create a separate section for creating a new account
        create_account_layout = QHBoxLayout()
        new_account_input = QLineEdit()
        create_account_button = QPushButton('Create')
        create_account_button.clicked.connect(lambda: self.create_account(dialog, new_account_input.text()))
        create_account_layout.addWidget(new_account_input)
        create_account_layout.addWidget(create_account_button)

        layout.addLayout(create_account_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def populate_accounts(self, account_combo):
        # Run the command and get the output
        try:
            process = subprocess.Popen(['picomc', 'account', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, error)
        except FileNotFoundError:
            print("Error: 'picomc' command not found. Please make sure it's installed and in your PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print("Error:", e.stderr)
            sys.exit(1)

        # Parse the output and remove ' *' from account names
        accounts = output.splitlines()
        accounts = [account.replace(' *', '').strip() for account in accounts]

        # Populate accounts combo box
        account_combo.clear()
        account_combo.addItems(accounts)

    def create_account(self, dialog, username):
        if username.strip() == '':
            QMessageBox.warning(dialog, "Warning", "Username cannot be blank.")
            return
        try:
            subprocess.run(['picomc', 'account', 'create', username], check=True)
            QMessageBox.information(self, "Success", f"Account {username} created successfully!")
            self.populate_accounts(dialog.findChild(QComboBox))
        except subprocess.CalledProcessError as e:
            error_message = f"Error creating account: {e.stderr.decode()}"
            QMessageBox.critical(self, "Error", error_message)

    def set_default_account(self, dialog, account):
        dialog.close()
        try:
            subprocess.run(['picomc', 'account', 'setdefault', account], check=True)
            QMessageBox.information(self, "Success", f"Default account set to {account}!")
        except subprocess.CalledProcessError as e:
            error_message = f"Error setting default account: {e.stderr.decode()}"
            QMessageBox.critical(self, "Error", error_message)

    def show_about_dialog(self):
        about_message = "PicoDulce Launcher\n\nA simple gui for the picomc proyect."
        QMessageBox.about(self, "About", about_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PicomcVersionSelector()
    window.show()
    sys.exit(app.exec_())
