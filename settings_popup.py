from collections import defaultdict

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QDialog, QGridLayout, QComboBox, QFileDialog


class Ui_SettingsWindow(QDialog):
    def __init__(self, values):
        super().__init__()

        self.values = defaultdict(str, values)

        self.setupUi()

    def setupUi(self):

        userName = QLabel('Enter the user name:')
        sampleID = QLabel('Enter the sample ID:')
        analysisType = QLabel('Enter the analysis type:')
        rawImgPath = QLabel('Enter the path for raw images:')
        segDataPath = QLabel('Enter the path for segmentation data:')
        savePath = QLabel('Enter the path to save the documents:')
        guidePath = QLabel('Enter the path for the guide csv file:')
        cropSavePath = QLabel('Enter the path for the crop images:')
        additionalCrop = QLabel('Enter the additional crop information:')
        b2p_ratio = QLabel('Enter the board to pin ratio:')
        device = QLabel('Enter the device:')

        self.userName_edit = QLineEdit(self.values['userName'])
        self.sampleID_edit = QLineEdit(self.values['sampleID'])
        self.sampleID_edit.textChanged.connect(self.on_sampleID_text_changed)

        self.analysisType_edit = QComboBox()
        self.analysisType_edit.addItem('PackageSJQ')
        self.analysisType_edit.addItem('PackageSJR')
        self.analysisType_edit.addItem('SocketSJQ')
        self.analysisType_edit.addItem('SocketSJR')

        self.savePath_edit = QLineEdit(self.values['savePath'].format(self.values['sampleID']))
        self.savePath_edit.setEnabled(False)
        self.cropSavePath_edit = QLineEdit(self.values['cropSavePath'].format(self.values['sampleID']))
        self.cropSavePath_edit.setEnabled(False)

        self.rawImgPath_edit = QLineEdit(self.values['rawImgPath'])
        rawImg_csv_open_button = QPushButton("Open")
        rawImg_csv_open_button.clicked.connect(self.rawImg_csv_open_button_click)

        self.guidePath_edit = QLineEdit(self.values['guidePath'])
        guide_csv_open_button = QPushButton("Open")
        guide_csv_open_button.clicked.connect(self.guide_csv_open_button_click)

        self.segDataPath_edit = QLineEdit(self.values['segDataPath'])
        segData_csv_open_button = QPushButton("Open")
        segData_csv_open_button.clicked.connect(self.segData_csv_open_button_click)


        self.additionalCrop_edit = QLineEdit(self.values['additionalCrop'])
        self.b2p_ratio_edit = QLineEdit(self.values['b2p_ratio'])
        self.device_edit = QLineEdit(self.values['device'])

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(userName, 0, 0)
        grid.addWidget(self.userName_edit, 0, 1)

        grid.addWidget(sampleID, 1, 0)
        grid.addWidget(self.sampleID_edit, 1, 1)

        grid.addWidget(analysisType, 2, 0)
        grid.addWidget(self.analysisType_edit, 2, 1)

        grid.addWidget(rawImgPath, 3, 0)
        grid.addWidget(self.rawImgPath_edit, 3, 1)
        grid.addWidget(rawImg_csv_open_button, 3, 2)

        grid.addWidget(guidePath, 4, 0)
        grid.addWidget(self.guidePath_edit, 4, 1)
        grid.addWidget(guide_csv_open_button, 4, 2)

        grid.addWidget(segDataPath, 5, 0)
        grid.addWidget(self.segDataPath_edit, 5, 1)
        grid.addWidget(segData_csv_open_button, 5, 2)

        grid.addWidget(savePath, 6, 0)
        grid.addWidget(self.savePath_edit, 6, 1)

        grid.addWidget(cropSavePath, 7, 0)
        grid.addWidget(self.cropSavePath_edit, 7, 1)

        grid.addWidget(additionalCrop, 8, 0)
        grid.addWidget(self.additionalCrop_edit, 8, 1)

        grid.addWidget(b2p_ratio, 9, 0)
        grid.addWidget(self.b2p_ratio_edit, 9, 1)

        grid.addWidget(device, 10, 0)
        grid.addWidget(self.device_edit, 10, 1)

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        grid.addWidget(ok_button, 11, 0)
        grid.addWidget(cancel_button, 12, 0)

        self.setLayout(grid)

        self.setFixedSize(850, 600)
        self.setWindowTitle('Input Paths')

        ok_button.clicked.connect(self.ok_button_click)
        cancel_button.clicked.connect(self.cancel_button_click)

    def on_sampleID_text_changed(self):
        self.savePath_edit.setText(self.values['savePath'].format(self.sampleID_edit.text()))
        self.cropSavePath_edit.setText(self.values['cropSavePath'].format(self.sampleID_edit.text()))

    def rawImg_csv_open_button_click(self):
        directory_name = str(QFileDialog.getExistingDirectory(self, 'Select Directory'))

        if directory_name:
            self.rawImgPath_edit.setText(directory_name)

    def guide_csv_open_button_click(self):
        file_name, extension = QFileDialog.getOpenFileName(self, 'Open file', self.values['guidePath'], "CSV files (*.csv)")

        if file_name:
            self.guidePath_edit.setText(file_name)

    def segData_csv_open_button_click(self):
        file_name, extension = QFileDialog.getOpenFileName(self, 'Open file', self.values['segDataPath'], "CSV files (*.csv)")

        if file_name:
            self.segDataPath_edit.setText(file_name)

    def ok_button_click(self):

        dict = {'userName': self.userName_edit.text(),
                'sampleID': self.sampleID_edit.text(),
                'analysisType': self.analysisType_edit.currentText(),
                'rawImgPath': self.rawImgPath_edit.text(),
                'segDataPath': self.segDataPath_edit.text(),
                'savePath': self.savePath_edit.text(),
                'guidePath': self.guidePath_edit.text(),
                'cropSavePath': self.cropSavePath_edit.text(),
                'additionalCrop': self.additionalCrop_edit.text(),
                'b2p_ratio': self.b2p_ratio_edit.text(),
                'device': self.device_edit.text()}

        self.values = dict

        self.accept()

    def cancel_button_click(self):
        self.reject()
