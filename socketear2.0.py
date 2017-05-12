import json

import sys

import os

import os.path

import functools

import six

import pandas as pd

import numpy as np

from threading import Timer

from PyQt5 import QtWidgets, QtGui, QtCore
from intel_window_text import Ui_MainWindow
from settings_popup import Ui_SettingsWindow

import matplotlib
# matplotlib.use('GTKAgg')

from matplotlib.backends.backend_qt5agg import(
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure

import matplotlib.image as mpimg

import matplotlib.gridspec as gridspec

# import win32com.client

import json

from datetime import datetime

from drawPredictions_ import DrawPredictions

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

"""try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s"""

class LoadImage(QtWidgets.QMainWindow, Ui_MainWindow):
    """Load board images from the menu and the pins icon list."""

    def __init__(self):
        """Set up the user interference from the QT Designer.

        Initiate the menu bar and clicks on menu options.
        """
        super().__init__()
        """Set up the user interference from QT Designer."""
        self.setupUi(self)

        self.df_cls = None
        self.board_type = None
        self.board_label = None
        self.first_load = True
        self.first_resize = True
        self.resize_timer = None
        self.list_items = {}

        self.centralwidget.setDisabled(True)

        # Creating two menu options: Boards and Export
        self.file_menu = self.menuBar().addMenu('&File')
        self.boards_menu = self.menuBar().addMenu('&Boards')
        # self.export_menu = self.menuBar().addMenu('&Export')

        self.refresh_menus()

        self.export_action = self.file_menu.addAction('Save Board Label')
        self.run_macro_action = self.file_menu.addAction('Run the Macro File')
        self.exit_action = self.file_menu.addAction('Exit')
        self.exit_action.triggered.connect(QtWidgets.qApp.quit)

        # self.export_action = self.export_menu.addAction('Save Board Label')

    def refresh_menus(self):
        self.boards_menu.clear()

        unprocessed_menu = self.boards_menu.addMenu('Unprocessed')
        processed_menu = self.boards_menu.addMenu('Processed')

        config = ConfigParser()

        config.read('socketear.ini')

        file_path = os.path.normpath(config.get('path', 'dirpath'))

        # Going through the Board folder to create the appropriate actions
        for dirpath, dirnames, filenames in os.walk(os.path.join(file_path, 'Processed')):

            if 'pins' in dirnames and all(fn in filenames for fn in
                                          ['classification.csv',
                                           'stitched.png',
                                           'info.txt']):
                # Add actions for the right path
                action_cb = processed_menu.addAction(os.path.split(os.path.basename(dirpath))[-1])
                action_cb.triggered.connect(functools.partial(self.load_image, dirpath))

        for dirpath, dirnames, filenames in os.walk(os.path.join(file_path, 'Unprocessed')):
            if all(fn.endswith(".tif") for fn in filenames) and not dirnames:

                board_name = os.path.split(os.path.split(dirpath)[0])[1]
                save_path = os.path.join(file_path, 'Processed')
                action_nb = unprocessed_menu.addAction(board_name)
                action_nb.triggered.connect(functools.partial(
                    self.load_model, dirpath, board_name, save_path))

    def remove_board(self):
        """Remove the layer of matplotlib container and widgetlist.

        Also, disconnects all the buttons.
        """
        self.mpl_vl.removeWidget(self.canvas)
        self.canvas.close()
        # self.mpl_vl.removeWidget(self.toolbar)
        # self.toolbar.close()
        self.mpl_figs.clear()
        self.mpl_figs.currentItemChanged.disconnect()
        self.nwo_button.disconnect()
        self.nco_button.disconnect()
        self.normal_button.disconnect()
        self.hnp_button.disconnect()
        self.sb_button.disconnect()
        self.type1_button.disconnect()
        self.type2_button.disconnect()
        self.type3_button.disconnect()
        self.type4_button.disconnect()
        self.reject_button.disconnect()
        # self.no_crack_button.disconnect()
        self.type_a_button.disconnect()
        self.type_b_button.disconnect()
        self.type_c_button.disconnect()
        self.type_d_button.disconnect()
        self.type_e_button.disconnect()
        self.refresh_sjr_button.disconnect()
        self.refresh_sjq_button.disconnect()
        self.sjr_image_button.disconnect()
        self.export_action.disconnect()
        self.export_action.setDisabled(True)

    def add_mpl(self):
        """Add a layer of matplotlib container."""

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.mpl_vl.addWidget(self.canvas)
        self.canvas.draw()
        # self.toolbar = NavigationToolbar(self.canvas,
        #                                  self.mpl_window,
        #                                  coordinates=True)
        # self.addToolBar(self.toolbar)

    def button_clicked(self, value):
        """Change the radio button.

        Updates the CSV file after a radio button was clicked.
        """
        pin_index = self.mpl_figs.currentItem().data(32)

        if self.board_type == 'SJR':
            if isinstance(value, six.string_types):
                self.df_cls.set_value(pin_index, 'DYE Correction', value)

            elif isinstance(value, int):
                self.df_cls.set_value(pin_index, 'SJR Correction', value)

        elif self.board_type == 'SJQ':
            self.df_cls.set_value(pin_index, 'SJQ Correction', value)

        image_path = self.df_cls.loc[pin_index]['Image Path']

        csv_path = os.path.split(os.path.split(os.path.normpath(image_path))[0])[0]

        # Saving the CSV file
        header = ['Row', 'Col', 'StitchedX', 'StitchedY', 'Pin', 'SJQ', 'SJR', 'DYE', 'SJQ Correction',
                  'SJR Correction', 'DYE Correction', 'Type Change', 'Sorted SJQ', 'Image Path', 'Label Coords', 'DYE Image Path']
        self.df_cls.to_csv(os.path.join(csv_path, 'classification.csv'), columns=header)

    def nwo_button_clicked(self, enabled):
        """Activate the nwo button for SJQ."""
        if enabled:
            self.button_clicked(0)

    def nco_button_clicked(self, enabled):
        """Activate the nco button for SJQ."""
        if enabled:
            self.button_clicked(1)

    def normal_button_clicked(self, enabled):
        """Activate the normal button for SJQ."""
        if enabled:
            self.button_clicked(2)

    def hnp_button_clicked(self, enabled):
        """Activate the hnp button for SJQ."""
        if enabled:
            self.button_clicked(3)

    def sb_button_clicked(self, enabled):
        """Activate the sb button for SJQ."""
        if enabled:
            self.button_clicked(4)

    def type1_button_clicked(self, enabled):
        """Activate the type1 button for SJR."""
        if enabled:
            self.button_clicked(0)

    def type2_button_clicked(self, enabled):
        """Activate the type2 button for SJR."""
        if enabled:
            self.button_clicked(1)

    def type3_button_clicked(self, enabled):
        """Activate the normal button for SJR."""
        if enabled:
            self.button_clicked(2)

    def type4_button_clicked(self, enabled):
        """Activate the type4 button for SJR."""
        if enabled:
            self.button_clicked(3)

    def reject_button_clicked(self, enabled):
        """Activate the type4 button for SJR."""
        if enabled:
            self.button_clicked(4)

    # def no_crack_button_clicked(self, enabled):
    #     """Activate the no crack button for SJR."""
    #     if enabled:
    #         self.button_clicked('O')

    def type_a_button_clicked(self, enabled):
        """Activate the typeA button for SJR."""
        if enabled:
            self.button_clicked('A')

    def type_b_button_clicked(self, enabled):
        """Activate the typeB button for SJR."""
        if enabled:
            self.button_clicked('B')

    def type_c_button_clicked(self, enabled):
        """Activate the typeC button for SJR."""
        if enabled:
            self.button_clicked('C')

    def type_d_button_clicked(self, enabled):
        """Activate the typeD button for SJR."""
        if enabled:
            self.button_clicked('D')

    def type_e_button_clicked(self, enabled):
        """Activate the typeE button for SJR."""
        if enabled:
            self.button_clicked('E')

    def refresh(self, predictions, dye_predictions=None):

        # start_refresh = datetime.now()

        self.board_label = self.drawing_tool(shape=1000, pred=predictions, dyepred=dye_predictions)

        # print('remove scatters!')

        self.axes1_scatter.remove()
        self.axes2_scatter.remove()

        self.axes2_image = self.axes2.imshow(self.board_label)

        self.canvas.draw()

        self.background_board = self.canvas.copy_from_bbox(self.axes2.bbox)

        pin_index = self.mpl_figs.currentItem().data(32)

        self.load_pin_cls(pin_index)

        cx_image = self.df_cls.ix[pin_index, 'StitchedX']
        cy_image = self.df_cls.ix[pin_index, 'StitchedY']

        self.axes1_scatter = self.axes1.scatter(cy_image, cx_image,
                                                edgecolor='#ff01d0',
                                                marker='s',
                                                s=80,
                                                linewidth='2',
                                                facecolors='none')

        cx_label = self.df_cls.ix[pin_index, 'Label Coords'][0] * 1000
        cy_label = self.df_cls.ix[pin_index, 'Label Coords'][1] * 1000

        self.axes2_scatter = self.axes2.scatter(cy_label, cx_label,
                                                edgecolor='#ff01d0',
                                                marker='s',
                                                s=80,
                                                linewidth='2',
                                                facecolors='none')

        self.canvas.blit(self.axes1.bbox)
        self.canvas.blit(self.axes2.bbox)


        # print('timer canvas.draw: ', datetime.now() - start_refresh)
        # start_refresh = datetime.now()

        self.sort_classification()

        # print('timer sort_classification: ', datetime.now() - start_refresh)
        # start_refresh = datetime.now()

        self.pin_dividers()

        # print('timer pin_dividers: ', datetime.now() - start_refresh)

        self.mpl_figs.clear()

        # start_refresh = datetime.now()

        self.load_pins()

        # print('timer load_pins: ', datetime.now() - start_refresh)

        self.mpl_figs.setCurrentItem(self.mpl_figs.item(0))
        board_pin_info = self.board_info + "\nPin name: {0}".format(str(self.df_cls.ix[pin_index, 'Pin']))
        self.board_display_label.setText(board_pin_info)


    def refresh_sjq_clicked(self):
        """Redraw the label board for SJQ model."""

        # start_refresh = datetime.now()
        print('Starting to refresh...')

        predictions = self.df_cls.set_index('Pin')['SJQ Correction'].to_dict()
        dye_predictions = None

        self.refresh(predictions, dye_predictions)

        # print('start_refresh: ', datetime.now() - start_refresh)

    def refresh_sjr_clicked(self):
        """Redraw the label board for SJQ model."""

        # start_refresh = datetime.now()
        print('Starting to refresh...')

        predictions = self.df_cls.set_index('Pin')['SJR Correction'].to_dict()
        dye_predictions = self.df_cls.set_index('Pin')['DYE Correction'].to_dict()


        self.refresh(predictions, dye_predictions)

        # print('start_refresh: ', datetime.now() - start_refresh)

    def sjr_image_switch(self):
        """Switch the pin image and dyed pin image for SJR models."""

        print("switch the pin/ dye image!")
        print(self.df_cls)

        pin_index = self.mpl_figs.currentItem().data(32)
        print(self.df_cls.loc[pin_index, 'Image Path'])
        print(self.df_cls.loc[pin_index, 'DYE Image Path'])

        if self.pin_dye_image == self.df_cls.loc[pin_index, 'Image Path']:
            self.pin_dye_image = self.df_cls.loc[pin_index, 'DYE Image Path']
            self.pin_image.setPixmap(QtGui.QPixmap(QtGui.QImage(self.pin_dye_image)))
            

        elif self.pin_dye_image == self.df_cls.loc[pin_index, 'DYE Image Path']:
            self.pin_dye_image = self.df_cls.loc[pin_index, 'Image Path']
            self.pin_image.setPixmap(QtGui.QPixmap(QtGui.QImage(self.pin_dye_image)))


    def on_click(self, event):

        if not event.inaxes:
            print('Clicked outside axes bounds but inside plot window')
            return

        if event.inaxes == self.axes1:

            self.df_cls['Image Coords'] = self.df_cls[['StitchedX', 'StitchedY']].apply(tuple, axis=1)
            z = self.df_cls[['StitchedX', 'StitchedY']].values
            distance = np.linalg.norm((z - np.array([event.ydata, event.xdata])), axis=1)
            row_index = np.argmin(distance)

            current_item = None
            for index in range(self.mpl_figs.count()):
                item = self.mpl_figs.item(index)
                if item.data(32) == row_index:
                    current_item = item

            if current_item:
                self.mpl_figs.setCurrentItem(current_item)
                pin_index = current_item.data(32)
                self.load_pin_cls(pin_index)
            else:
                print('No item found for row {}'.format(row_index))

        if event.inaxes == self.axes2:
            z = np.zeros(shape=(len(self.guide.pins), 2))

            for j, pin in enumerate(self.guide.pins):
                z[j] = 1000 * np.array(self.guide.position(pin))

            distance = np.linalg.norm((z - np.array([event.ydata, event.xdata])), axis=1)

            k = np.argmin(distance)

            pin_name = self.guide.pins[k]
            row = self.df_cls.Pin[self.df_cls.Pin == pin_name].index.tolist()[0]

            current_item = None
            for index in range(self.mpl_figs.count()):
                item = self.mpl_figs.item(index)
                if item.data(32) == row:
                    current_item = item

            if current_item:
                self.mpl_figs.setCurrentItem(current_item)
                pin_index = current_item.data(32)
                self.load_pin_cls(pin_index)
            else:
                print('No item found for row {}'.format(row))

    def current_item_changed(self):
        """Update the zoom-in pin image and the board image position.

        Based on the items in the scrollable list(WidgetListItem).
        """
        if self.mpl_figs.currentItem():

            pin_index = self.mpl_figs.currentItem().data(32)

            self.load_pin_cls(pin_index)
            cx_label = self.df_cls.ix[pin_index, 'Label Coords'][0] * 1000
            cy_label = self.df_cls.ix[pin_index, 'Label Coords'][1] * 1000

            try:
                self.axes2_scatter.remove()
            except:
                pass

            self.axes2_scatter = self.axes2.scatter(cy_label, cx_label,
                                                    edgecolor='#ff01d0',
                                                    marker='s',
                                                    s=80,
                                                    linewidth='2',
                                                    facecolors='none')

            cx_image = self.df_cls.ix[pin_index, 'StitchedX']
            cy_image = self.df_cls.ix[pin_index, 'StitchedY']

            try:
                self.axes1_scatter.remove()
            except:
                pass

            self.axes1_scatter = self.axes1.scatter(cy_image, cx_image,
                                                    edgecolor='#ff01d0',
                                                    marker='s',
                                                    s=80,
                                                    linewidth='2',
                                                    facecolors='none')

            start_canvas = datetime.now()

            self.canvas.restore_region(self.background_image)
            self.canvas.restore_region(self.background_board)
            self.axes1.draw_artist(self.axes1_scatter)
            self.axes2.draw_artist(self.axes2_scatter)
            self.canvas.blit(self.axes1.bbox)
            self.canvas.blit(self.axes2.bbox)

            self.canvas.flush_events()
            # print('canvas: ', datetime.now() - start_canvas)
            board_pin_info = self.board_info + "\nPin name: {0}".format(str(self.df_cls.ix[pin_index, 'Pin']))
            self.board_display_label.setText(board_pin_info)

    def load_pin_cls(self, pin_index):
        """Load the zoom-in pin image.

        And activate the appropriate radio button.
        """

        self.pin_dye_image = self.df_cls.ix[pin_index, 'Image Path']
        self.pin_image.setScaledContents(True)
        self.pin_image.setPixmap(QtGui.QPixmap(
                                 QtGui.QImage(self.pin_dye_image)))

        if self.board_type == 'SJR':

            classification = self.df_cls.ix[pin_index, 'SJR Correction']
            dye_cls = self.df_cls.ix[pin_index, 'DYE Correction']

            if classification == 0:
                self.type1_button.setChecked(True)
            elif classification == 1:
                self.type2_button.setChecked(True)
            elif classification == 2:
                self.type3_button.setChecked(True)
            elif classification == 3:
                self.type4_button.setChecked(True)
            elif classification == 4:
                self.reject_button.setChecked(True)

            # if dye_cls == 'O':
            #     self.no_crack_button.setChecked(True)
            if dye_cls == 'A':
                self.type_a_button.setChecked(True)
            elif dye_cls == 'B':
                self.type_b_button.setChecked(True)
            elif dye_cls == 'C':
                self.type_c_button.setChecked(True)
            elif dye_cls == 'D':
                self.type_d_button.setChecked(True)
            elif dye_cls == 'E':
                self.type_e_button.setChecked(True)

        elif self.board_type == 'SJQ':

            classification = self.df_cls.ix[pin_index, 'SJQ Correction']

            if classification == 0:
                self.nwo_button.setChecked(True)
            elif classification == 1:
                self.nco_button.setChecked(True)
            elif classification == 2:
                self.normal_button.setChecked(True)
            elif classification == 3:
                self.hnp_button.setChecked(True)
            elif classification == 4:
                self.sb_button.setChecked(True)

    def sort_sjq(self, row):

        if row['SJQ Correction'] == 0:
            value = 'a'
        elif row['SJQ Correction'] == 1:
            value = 'b'
        elif row['SJQ Correction'] == 2:
            value = 'e'
        elif row['SJQ Correction'] == 3:
            value = 'c'
        elif row['SJQ Correction'] == 4:
            value = 'd'
        else:
            raise ValueError('Unknown classification')

        return value

    def set_buttons(self, column_names):

        if all(cn in column_names for cn in ['SJR', 'SJQ', 'DYE']):

            if not(self.df_cls['SJR'].isnull().all()) and \
                    not(self.df_cls['DYE'].isnull().all()) and \
                    self.df_cls['SJQ'].isnull().all():

                self.board_type = 'SJR'
                self.nwo_button.setDisabled(True)
                self.nco_button.setDisabled(True)
                self.normal_button.setDisabled(True)
                self.hnp_button.setDisabled(True)
                self.sb_button.setDisabled(True)
                self.refresh_sjq_button.setDisabled(True)
                self.type1_button.setDisabled(False)
                self.type2_button.setDisabled(False)
                self.type3_button.setDisabled(False)
                self.type4_button.setDisabled(False)
                self.reject_button.setDisabled(False)
                # self.no_crack_button.setDisabled(False)
                self.type_a_button.setDisabled(False)
                self.type_b_button.setDisabled(False)
                self.type_c_button.setDisabled(False)
                self.type_d_button.setDisabled(False)
                self.type_e_button.setDisabled(False)
                self.refresh_sjr_button.setDisabled(False)
                self.sjr_image_button.setDisabled(False)

            elif not(self.df_cls['SJR'].isnull().all()) and \
                    not(self.df_cls['SJQ'].isnull().all()) and \
                    self.df_cls['DYE'].isnull().all():

                self.board_type = 'SJQ'
                self.nwo_button.setDisabled(False)
                self.nco_button.setDisabled(False)
                self.normal_button.setDisabled(False)
                self.hnp_button.setDisabled(False)
                self.sb_button.setDisabled(False)
                self.refresh_sjq_button.setDisabled(False)
                self.type1_button.setDisabled(True)
                self.type2_button.setDisabled(True)
                self.type3_button.setDisabled(True)
                self.type4_button.setDisabled(True)
                self.reject_button.setDisabled(True)
                # self.no_crack_button.setDisabled(True)
                self.type_a_button.setDisabled(True)
                self.type_b_button.setDisabled(True)
                self.type_c_button.setDisabled(True)
                self.type_d_button.setDisabled(True)
                self.type_e_button.setDisabled(True)
                self.refresh_sjr_button.setDisabled(True)
                self.sjr_image_button.setDisabled(True)

            else:
                raise ValueError('Incomplete CSV file')

        else:
            raise ValueError('Unknown board')

    def sort_classification(self):

        if self.board_type == 'SJQ':
            self.df_cls['Sorted SJQ'] = self.df_cls['SJQ Correction']

            self.df_cls['Sorted SJQ'] = self.df_cls.apply(self.sort_sjq,  axis=1)
            self.df_cls = self.df_cls.sort_values(by=['Sorted SJQ', 'SJR Correction'], ascending=[True, True])
            self.df_cls = self.df_cls.reset_index(drop=True)

        if self.board_type == 'SJR':

            self.df_cls = self.df_cls.sort_values(by=['SJR Correction', 'DYE Correction'], ascending=[True, False])
            self.df_cls = self.df_cls.reset_index(drop=True)

    def pin_dividers(self):

        # Create columns to indicate the divider location for the QListWidgetItem
        if self.board_type == 'SJQ':
            self.df_cls['Type Change'] = self.df_cls['SJQ Correction'].shift(-1) != self.df_cls['SJQ Correction']
            if self.df_cls.ix[0, 'SJQ Correction'] != self.df_cls.ix[1, 'SJQ Correction']:
                self.df_cls.ix[0, 'Type Change'] = True
            else:
                self.df_cls.ix[0, 'Type Change'] = False

        elif self.board_type == 'SJR':
            self.df_cls['Type Change'] = self.df_cls['SJR Correction'].shift(-1) != self.df_cls['SJR Correction']
            if self.df_cls.ix[0, 'SJR Correction'] != self.df_cls.ix[1, 'SJR Correction']:
                self.df_cls.ix[0, 'Type Change'] = True
            else:
                self.df_cls.ix[0, 'Type Change'] = False

    def load_pins(self, first_load=False):

        if first_load:
            self.list_items = {}

        count_image_cat = 0

        # Create a list of the 'Image Path'  column
        image_path_values = self.df_cls['Image Path'].values.tolist()
        for image_path in self.df_cls['Image Path'].tolist():

            if first_load:
                icon = QtGui.QIcon(image_path)
            else:
                icon = self.list_items[image_path]

            # Adding the pin images to the scrollable list (WidgetListItem)
            item = QtWidgets.QListWidgetItem()
            item.setIcon(icon)
            self.list_items[image_path] = icon

            index = image_path_values.index(image_path)
            item.setData(32, index)

            self.mpl_figs.addItem(item)

            count_image_cat += 1

            if self.df_cls.iloc[index]['Type Change'] == True:

                mod_of_5 = count_image_cat % 5
                if mod_of_5 != 0:
                    amount_of_white = (5 - mod_of_5) + 5
                else:
                    amount_of_white = 5

                for x in range(0, amount_of_white):

                    item = QtWidgets.QListWidgetItem()  # delimiter
                    item.setData(32, -1)
                    item.setFlags(QtCore.Qt.NoItemFlags)  # item should not be selectable
                    self.mpl_figs.addItem(item)

                count_image_cat = 0

    def get_pins(self, root):
        """Load list of pin icons."""

        # Reading the CSV file from the appropriate path
        self.df_cls = pd.read_csv(os.path.join(root, 'classification.csv'))

        if not('SJQ Correction' in self.df_cls.columns):
            self.df_cls['SJQ Correction'] = self.df_cls['SJQ'].copy()
        if not('SJR Correction' in self.df_cls.columns):
            self.df_cls['SJR Correction'] = self.df_cls['SJR'].copy()
        if not('DYE Correction' in self.df_cls.columns):
            self.df_cls['DYE Correction'] = self.df_cls['DYE'].copy()

        # Adding the Pin column and adding the pin names to it by
        # combining the Col and Row Columns
        self.df_cls['Pin'] = self.df_cls[['Row', 'Col']].apply(
            lambda x: '{}{}{}'.format(x[0], '_', x[1]), axis=1)

        # Adding a label for the index column
        self.df_cls.columns.names = ['Index']

        column_names = list(self.df_cls)

        self.set_buttons(column_names)

        self.sort_classification()

        df_pin_list = self.df_cls['Pin'].tolist()

        # Adding the path of the each pin image to the Dataframe

        # Create a column in the dataframe to store the image paths
        self.df_cls['Image Path'] = np.nan

        # Create a column in the dataframe to store the DYE image paths
        self.df_cls['DYE Image Path'] = np.nan

        # Matching the pins with the correct image and adding them to
        # the 'Image Path' column

        # for every file (image_path) in the pins folder:
        for f in os.listdir(os.path.join(root, 'pins')):

            if f.endswith("_1.tif"):
                image_path = os.path.join(os.getcwd(),
                                      os.path.join(root, 'pins'), f)
                pin_name = os.path.basename(image_path).replace("_1.tif", "")

                # finding the index of the row where the pin is located in
                # the dataframe
                if pin_name in df_pin_list:

                    index = self.df_cls[self.df_cls['Pin'] == pin_name].index[0]

                    # adding the pin's image path to the same row in the dataframe
                    # where the pin is located
                    self.df_cls.loc[index, 'Image Path'] = image_path

        if self.board_type == 'SJR':
            if 'dye' in os.listdir(os.path.join(root, '')):
                for f in os.listdir(os.path.join(root, 'dye')):

                    dye_path = os.path.join(os.getcwd(),
                                            os.path.join(root, 'dye'), f)
                    pin_name = os.path.basename(dye_path).replace("_1.tif", "")

                    if pin_name in df_pin_list:

                        index = self.df_cls[self.df_cls['Pin'] == pin_name].index[0]

                        self.df_cls.loc[index, 'DYE Image Path'] = dye_path
                        
            else:
                print('Unable to locate the DYE folder. Thus no dye images')
                self.sjr_image_button.setDisabled(True)


        self.pin_dividers()

        self.load_pins(first_load=True)

    def load_board(self, root):
        """Load the appropriate board based on the menu clicked."""
        self.centralwidget.setDisabled(True)

        print('Path: ', root)
        board_name = os.path.basename(root)

        print('Board name: ', board_name)
        print('Board type: ', self.board_type)

        new_font = QtGui.QFont("Arial", 10, QtGui.QFont.Bold)
        self.board_display_label.setFont(new_font)
        self.board_info = "Board name: {0}\nBoard type: {1}".format(board_name, self.board_type)
        self.board_display_label.setText(self.board_info)

        with open(os.path.join(root, 'info.txt')) as json_file:
            data = json.load(json_file)
            print('guide path: ', data['guidePath'])

        csvpath = data['guidePath']
        b2p_ratio = int(data['b2p_ratio'])
        from guides.generalguide import GeneralGuide

        self.guide = GeneralGuide(csvpath, b2p_ratio)

        pin_coords = []

        for pin in self.df_cls['Pin'].tolist():
            if pin in self.guide.pins:
                pin_coords.append(tuple(self.guide.position(pin)))

        self.df_cls['Label Coords'] = pd.Series(pin_coords, index=self.df_cls.index)

        self.drawing_tool = DrawPredictions(guide=self.guide, mode=self.board_type)

        cls_corrected_col = "{} Correction".format(self.board_type)
        # print('cls_corrected_col', cls_corrected_col)

        predictions = self.df_cls.set_index('Pin')[cls_corrected_col].to_dict()

        if self.board_type == 'SJR':
            dye_predictions = self.df_cls.set_index('Pin')['DYE Correction'].to_dict()
            self.board_label = self.drawing_tool(shape=1000, pred=predictions, dyepred=dye_predictions)
        elif self.board_type == 'SJQ':
            self.board_label = self.drawing_tool(shape=1000, pred=predictions)
        else:
            raise ValueError('Unknown board')

        self.board_img = mpimg.imread(os.path.join(root, 'stitched.png'))

        gs = gridspec.GridSpec(1, 2)
        gs.update(left=0.005, right=0.99, wspace=0.05)

        self.axes1 = self.figure.add_subplot(gs[0])
        self.axes1.get_xaxis().set_visible(False)
        self.axes1.get_yaxis().set_visible(False)

        self.axes2 = self.figure.add_subplot(gs[1])
        self.axes2.get_xaxis().set_visible(False)
        self.axes2.get_yaxis().set_visible(False)

        # print('init scatter')

        self.axes1_scatter = None
        self.axes2_scatter = None

        self.canvas.mpl_connect('resize_event', self.connect_resize)
        self.export_action.triggered.connect(functools.partial(self.save_board_label, root))
        self.export_action.setDisabled(False)

        self.run_macro_action.triggered.connect(functools.partial(self.run_excel_macro, root))

        self.first_load = False

        self.centralwidget.setDisabled(False)

    def connect_resize(self, event):
        print('resize event', event)

        self.centralwidget.setDisabled(True)

        self.perform_resize()

        # try:
        #     print('resize event try', event)
        #     self.resize_timer.cancel()
        # except:
        #     pass
        #
        # self.resize_timer = Timer(1, self.perform_resize)
        # self.resize_timer.start()

    def perform_resize(self):
        # print('perform_resize')

        self.axes1.imshow(self.board_img)
        self.axes2.imshow(self.board_label)

        try:
            self.axes1_scatter.remove()
        except:
            print('Unable to remove axes1_scatter')
            pass

        try:
            self.axes2_scatter.remove()
        except:
            print('Unable to remove axes2_scatter')
            pass

        self.canvas.draw()

        self.background_image = self.canvas.copy_from_bbox(self.axes1.bbox)
        self.background_board = self.canvas.copy_from_bbox(self.axes2.bbox)

        self.centralwidget.setDisabled(False)

    def connect_click(self):
        """Just testing this."""

        # connect the click or arrow keys press on the the scrollable
        # image list to the currentItemChanged
        self.mpl_figs.currentItemChanged.connect(self.current_item_changed)

        self.nwo_button.toggled.connect(self.nwo_button_clicked)

        self.nco_button.toggled.connect(self.nco_button_clicked)

        self.normal_button.toggled.connect(self.normal_button_clicked)

        self.hnp_button.toggled.connect(self.hnp_button_clicked)

        self.sb_button.toggled.connect(self.sb_button_clicked)

        self.type1_button.toggled.connect(self.type1_button_clicked)

        self.type2_button.toggled.connect(self.type2_button_clicked)

        self.type3_button.toggled.connect(self.type3_button_clicked)

        self.type4_button.toggled.connect(self.type4_button_clicked)

        self.reject_button.toggled.connect(self.reject_button_clicked)

        # self.no_crack_button.toggled.connect(self.no_crack_button_clicked)

        self.type_a_button.toggled.connect(self.type_a_button_clicked)

        self.type_b_button.toggled.connect(self.type_b_button_clicked)

        self.type_c_button.toggled.connect(self.type_c_button_clicked)

        self.type_d_button.toggled.connect(self.type_d_button_clicked)

        self.type_e_button.toggled.connect(self.type_e_button_clicked)

        self.refresh_sjq_button.clicked.connect(self.refresh_sjq_clicked)

        self.refresh_sjr_button.clicked.connect(self.refresh_sjr_clicked)

        self.sjr_image_button.clicked.connect(self.sjr_image_switch)

        self.canvas.callbacks.connect('button_press_event', self.on_click)

    def save_board_label(self, path):
        import cv2
        cv2.imwrite(os.path.join(path, 'board.png'), 255*self.board_label[:, :, ::-1])

    def run_excel_macro(self, path):

        try:
            xlApp = win32com.client.Dispatch('Excel.Application')
            xlsPath = os.path.abspath(os.path.join(path, 'MacroTest.xlsm'))
            print(xlsPath)
            macroxl = xlApp.Workbooks.Open(xlsPath)
            xlApp.Run('MacroTest.xlsm!TEST_1')
            macroxl.Save()
            xlApp.Quit()
            print("Macro ran successfully!")

        except Exception as e:
            print("Error found while running the excel macro!")
            raise


    def load_image(self, root):
        """Construct the board image and load it on matplotlib container."""
        # Rest the matplotlib container and the buttons

        print('Starting to load the images...')

        if not self.first_load:
            self.remove_board()

        # Add a matplotlib container
        self.add_mpl()

        # load pin images in the zoom-in container and
        # the scrollable image list
        self.get_pins(root)

        self.load_pin_cls(0)

        self.load_board(root)

        self.connect_click()

    def closeEvent(self, event):
        try:
            self.resize_timer.cancel()
        except:
            pass

    def load_model(self, root, board_name, save_path):

        default_settings = {'sampleID': board_name,
                            'rawImgPath': root,
                            'cropSavePath': os.path.join(save_path, "{}", 'pins'),
                            'savePath': os.path.join(save_path, "{}"),
                            'additionalCrop': 'None',
                            'b2p_ratio': '150',
                            'device': 'gpu0'}

        dialog = Ui_SettingsWindow(default_settings)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        exit_code = dialog.exec_()
        # print(exit_code)

        if exit_code:
            # print(dialog.values)
            settings_dict = dialog.values

            userName = settings_dict['userName']
            sampleID = settings_dict['sampleID']
            analysisType = settings_dict['analysisType']
            rawImgPath = settings_dict['rawImgPath']
            cropSavePath = settings_dict['cropSavePath']
            segDataPath = settings_dict['segDataPath']
            savePath = settings_dict['savePath']
            guidePath = settings_dict['guidePath']
            additionalCrop = settings_dict['additionalCrop']
            b2p_ratio = int(settings_dict['b2p_ratio'])
            device = settings_dict['device']

            class TaskThread(QtCore.QThread):
                def run(self):
                    print("task is running")
                    try:
                        from guides.generalguide import GeneralGuide
                        guide = GeneralGuide(guidePath, b2p_ratio)

                        from model import Model
                        valid_additionalCrop = None if additionalCrop == 'None' else (int(additionalCrop), int(additionalCrop))

                        f_model = Model(sampleID, analysisType, guide, valid_additionalCrop, rawImgPath, segDataPath, cropSavePath, savePath, device)

                        from time import time
                        st = time()
                        print('Starting the analysis...')
                        f_model(saveResults=True)
                        sp = time() - st
                        print('Analysis took {} seconds'.format(sp))
                    except Exception as e:
                        print(e)

            task_thread = TaskThread()

            from progress_bar import ConstantProgressBar
            progress_dialog = ConstantProgressBar(task_thread)
            exit_code = progress_dialog.exec_()
            print(exit_code)

            json.dump(settings_dict, open(os.path.join(savePath, 'info.txt'), 'w'), indent=4)

            self.refresh_menus()

            self.load_image(savePath)

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = LoadImage()
    window.showMaximized()
    sys.exit(app.exec_())
