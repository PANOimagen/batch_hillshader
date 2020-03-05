# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Batch_Hillshader
                                 A QGIS plugin  to generate a three light
                                 exposure hillshade (shaded relief by
                                 combining three light exposures)

    For more information, see the program documentation.

    Plugin uses LASzip, see <https://laszip.org/>
                              -------------------
        begin                : 2016-07-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by PANOimagen S.L.
        email                : info@panoimagen.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software: you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation, either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program.  If not, see <https://www.gnu.org/licenses/> *
 ***************************************************************************/
"""

import os
from osgeo import gdal
from qgis.PyQt import QtWidgets, uic
from qgis.gui import QgsMessageBar
from . import hillshader_process
from .plugin_utils import raster_funs
from .plugin_utils import files_and_dirs_funs as dir_fns

try:
    from qgis.core import Qgis
    MESSAGE_LEVEL = Qgis.MessageLevel(0)
except ImportError:
    MESSAGE_LEVEL = QgsMessageBar.INFO

from .bh_errors import LasPyNotFoundError

try:
    from . import laspy_utils
    HAS_LASPY = True
except LasPyNotFoundError as e:
    HAS_LASPY = False

try:
    from . import version
except ImportError:
    class version(object):
        VERSION = "devel"

try:
    # Qgis 3 compat
    # getOpenFileNamesandFilter in PyQt4 becomes getOpenFileNames in PyQt5
    getOpenFileNames = QtWidgets.QFileDialog.getOpenFileNamesAndFilter
except AttributeError:
    getOpenFileNames = QtWidgets.QFileDialog.getOpenFileNames

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'batch_hillshader_dialog_base.ui'))


class batchHillshaderDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(batchHillshaderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.iface = iface
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.preparingProcess)
        self.buttonBox.rejected.connect(self.reject)
        self.loadHillShadeCheckBox.setChecked(True)
        self.loadPartialsCheckBox.setChecked(False)
        self.laspyGroupBox.setEnabled(HAS_LASPY)
        self.copyrightLabel.setText('(C) 2017 by Panoimagen S.L.')
#        self.laspyRecomendedPixelLabel.setText(
#                'Recomended pixel size: - meters')
        self.currentDEMPixelSizeLabel.setText(
                'Input DEM pixel size: - x - meters')
        self.currentPxSizeLabel.setText(
                'Selected pixel size for hillshade results: - x - meters')
        self.laspyToolButton.clicked.connect(self.laspyProcess)
        self.outputFolderToolButton.clicked.connect(self.setOutPath)
        self.inputDEMToolButton.clicked.connect(self.DEMProcess)
        self.InputFilesOptions.currentChanged.connect(self.updateUi)
        self.InputFilesOptions.currentChanged.connect(self.hillshadePixelSize)
        self.inputDEMLineEdit.textChanged.connect(self.updateDEMPixelSize)
        self.laspyPixelSizeDoubleSpinBox.valueChanged.connect(
                self.hillshadePixelSize)
        self._initVersion()
        self.initLaspyUi()
        
        if HAS_LASPY:
            self.InputFilesOptions.setCurrentIndex(0)
        else:
            self.InputFilesOptions.setCurrentIndex(1)

# TODO: connect this objects: laspyLineEdit, laspyPixelSizeDoubleSpinBox, laspyRecomendedPixelLabel, laspyGroupBox

    def _initVersion(self):
        self.versionLabel.setText('Batch Hillshader version {}'.format(
                version.VERSION))

    def initLaspyUi(self):
# TODO: user can select both (terrain and surfaces)        
#        results_options = ['Terrain', 'Surfaces',
#                           'Both (Surfaces and Terrain)']
        results_options = ['Terrain', 'Surfaces']
        interpolate_methods = ['nearest', 'linear', 'cubic']
        self.interpolatingMethodComboBox.addItems(interpolate_methods)
        self.surfaceTerrainComboBox.addItems(results_options)
        laspy_text = 'LasPy Library is {}'
        if not HAS_LASPY:
            surname_label = (u'not installed. Read plugin documentation to' +
                             u' install LasPy Library')
            label_color = 'color: red'

        else:
            surname_label = u'installed'
            label_color = 'color: black'
            
        self.LiDARLasPyTab.setEnabled(HAS_LASPY)
        self.laspyImportLabel.setText(laspy_text.format(surname_label))
        self.laspyImportLabel.setStyleSheet(label_color)
        
        
    def updateUi(self):
        """Update UI QObjects
        """
        if self.InputFilesOptions.currentIndex() == 0:
            self.laspy_checked = True
        else:
            self.laspy_checked = False

        if self.laspy_checked:
            disable_DEM = True
            self.inputDEMLineEdit.clear()
            self.currentDEMPixelSizeLabel.setText(
                'Input DEM pixel size: - x - meters')
        else:
            disable_DEM = False
            self.laspyLineEdit.clear()

        self.inputDEMLineEdit.setEnabled(not disable_DEM)
        self.inputDEMToolButton.setEnabled(not disable_DEM)
        self.currentDEMPixelSizeLabel.setEnabled(not disable_DEM)
        self.inputDEMLabel.setEnabled(not disable_DEM)
        self.laspyGroupBox.setEnabled(self.laspy_checked)

    def updateDEMPixelSize(self):
        """Set input DEM pixel size when the process starts with an input
            DEM
        """
        dem_path = self.inputDEMLineEdit.text()
        if dem_path:
            dem_ds = gdal.Open(dem_path)
            try:
                self.dem_geo_info = dem_ds.GetGeoTransform()
                pixel_with = self.dem_geo_info[1]
                pixel_height = self.dem_geo_info[5]
                pixel_size_label = ('Input DEM pixel size' +
                                    ': {} x {} meters'.format(
                        pixel_with, pixel_height))
                self.currentDEMPixelSizeLabel.setText(pixel_size_label)
                self.hillshadePixelSize()
            except AttributeError:
                self.currentDEMPixelSizeLabel.setText(
                        'Input DEM pixel size: - x - meters')
        else:
            self.dem_geo_info = None

    def hillshadePixelSize(self):
        """Set the hillshade results pixel size and update the label
        """

        try:
            
            if self.InputFilesOptions.currentIndex() == 0:
                dem_pixel_size = [self.laspyPixelSizeDoubleSpinBox.value(),
                                  -(self.laspyPixelSizeDoubleSpinBox.value())]    
                self.updateHillshadeSizeLabel(dem_pixel_size[0], 
                                              dem_pixel_size[-1])
                return
            
        except AttributeError:
            pass

        try:
            if self.dem_geo_info is None:
                self.updateHillshadeSizeLabel('-','-')
            else:
                self.hillshadePxSize = [self.dem_geo_info[1],
                                        self.dem_geo_info[5]]
                self.updateHillshadeSizeLabel(self.hillshadePxSize[0],
                                               self.hillshadePxSize[-1])
        except AttributeError:
            self.updateHillshadeSizeLabel('-','-')

    def updateHillshadeSizeLabel(self, x, y):
        """Set label for hillshade results pixel size
        """
        self.currentPxSizeLabel.setText(
                'Selected pixel size for hillshade results:' +
                 ' {} x {} meters'.format(str(x), str(y)))
    
    def laspyProcess(self):
        """ Processing with Lidar data. Using laspy library Set input file 
            and start output folder
        """
        fileNames = getOpenFileNames(self,
                "Select the input LiDAR file/s",
                self.laspyToolButton.text(),
                ("LiDAR files (*.las *.LAS);;" +
                 " All files (*)"))
        if fileNames:
            # quoted = ['"{}"'.format(fn) for fn in fileNames]
            self.laspyLineEdit.setText(", ".join(fileNames[0]))
            if not self.outputFolderLineEdit.text():
                try:
                    outPath = os.path.join(
                        os.path.split(os.path.abspath(fileNames[0][0]))[0],
                        'batch_hillshader_output')
                    self.outputFolderLineEdit.setText(outPath)
                except IndexError:
                    pass
                
    def DEMProcess(self):
        """Processing with DEM data. Set input file and start output folder
        """
        fileNames = getOpenFileNames(self,
                "Select the DEM input file/s",
                self.inputDEMToolButton.text(),
                ("Raster files (*.tif *.tiff *.TIF *.TIFF *.asc *.ASC);;" +
                 "GEOTiff (*.tif *.tiff *.TIF *.TIFF);;" +
                 " ASCII Grid (*.asc *.ASC);; All files (*)"))

        if fileNames:
            # quoted = ['"{}"'.format(fn) for fn in fileNames]
            self.inputDEMLineEdit.setText(", ".join(fileNames[0]))
            if not self.outputFolderLineEdit.text():
                outPath = os.path.join(
                    os.path.split(os.path.abspath(fileNames[0][0]))[0],
                    'batch_hillshader_output')
                self.outputFolderLineEdit.setText(outPath)

    def setOutPath(self):
        """Function to select the output folder and update the LineEdit
        """
        outPath = QtWidgets.QFileDialog.getExistingDirectory(self,
                "Select the output folder",
                self.outputFolderToolButton.text())
        if outPath:
            self.outputFolderLineEdit.setText(os.path.join(
                    outPath, 'batch_hillshader_output'))

    def preparingProcess(self):
        """Set process mode and check inputs.
            This function launch also the function to set the
            process parameters
        """
        
        if self.InputFilesOptions.currentIndex() == 0:
            filenames = self.laspyLineEdit.text()
            self.processMode = 'laspyInput'
        
        else:
            filenames = self.inputDEMLineEdit.text()
            self.processMode = 'DEMInput'

        if not filenames:
            self.showQMessage("Error: Not input file selected!\nPlease," +
                              "select one.")

        outPath = self.outputFolderLineEdit.text()
        if not outPath:
            self.showQMessage("Error: Not output folder selected!\n" +
                              "Please, select one.")
        
        self.process_option = self.surfaceTerrainComboBox.currentText()
        
        if filenames and self.processMode:
            for f in filenames.split(","):
                full_filename = f.strip()
                _, filename = os.path.split(full_filename)
                if outPath:
                    self.settingProcessParams(full_filename, outPath)

    def settingProcessParams(self, full_filename, outPath):
        """Set the params that are used in the process and call to the
            process module
        """
        self.createDictParams()
        partialsCreateAndLoad = self.loadPartialsCheckBox.isChecked()
        sombrasOutResults = self.loadHillShadeCheckBox.isChecked()
        if self.InputFilesOptions.currentIndex() == 0:
            sizeDEM = self.laspyPixelSizeDoubleSpinBox.value()
            
        _, filename = os.path.split(full_filename)
        base_name, ext = os.path.splitext(filename)
        start_index = 1
        out_path = os.path.join(
                outPath, (base_name + '_r' + str(start_index)))
        if os.path.exists(out_path):
            import glob
            key_for_glob = os.path.join(outPath, (base_name + '_r*' ))
            dirs_list = glob.glob(key_for_glob)
            indexes = []
            for directory in dirs_list:
                fn_index = int(directory[-1])
                indexes.append(fn_index)
                max_index = max(indexes)
            next_index = max_index + 1
            out_path = os.path.join(outPath,
                        (base_name + '_r' + str(next_index)))
        
        self.dir_funs = dir_fns.DirAndPaths()
        
        if self.InputFilesOptions.currentIndex() == 0:

            self.showMessage('Starting processing LiDAR data {}'.format(
                                    base_name) +
                             u' with LasPy Library', MESSAGE_LEVEL)
            
            self.inter_method = self.interpolatingMethodComboBox.currentText()
            
            # TODO
            if self.process_option == 'Surfaces':
                terrain = False
                surfaces = True
            elif self.process_option == 'Terrain':
                terrain = True
                surfaces = False

#TODO: User can select both results
#            elif self.process_option == 'Both (Surfaces and Terrain)':
#                terrain = True
#                surfaces = True

            if not os.path.exists(out_path):
                os.makedirs(out_path)

            self.laspyLidar = laspy_utils.LiDAR(full_filename,
                                                out_path,
                                                partialsCreateAndLoad,
                                                terrain, surfaces)
            try:
                self.lidar_arrays_list, self.las_file_extent, self.density =\
                        self.laspyLidar.process()
            except ValueError as message:
                self.showQMessage(str(message))
                
                self.showMessage('Batch Hillshader stoped process',
                                  Qgis.MessageLevel(1))
                
                return
                
            self.lidar_results = [self.lidar_arrays_list, 
                                  self.las_file_extent, 
                                  self.density]

            self.laspyRasterize = laspy_utils.RasterizeLiDAR(
                                                    full_filename,
                                                    self.lidar_results,
                                                    out_path,
                                                    terrain, surfaces,
                                                    self.inter_method, 
                                                    sizeDEM)
              
            self.interpolated_grid = self.laspyRasterize.interpolate_grid()
              
            dem_full_path = self.laspyRasterize.array_2_raster(
                                                    self.interpolated_grid)
            
            self.dem_array, self.no_data_value = raster_funs.raster_2_array(
                                                    dem_full_path)
            
            if partialsCreateAndLoad:
                dem_filename, _ = os.path.splitext(
                            os.path.split(dem_full_path)[-1])
                raster_funs.load_raster_layer(
                            dem_full_path,
                            dem_filename)

            self.showMessage('Processing data... {}'.format(base_name),
                                  MESSAGE_LEVEL)

            self.HillDEM = hillshader_process.HillshaderDEM(
                                                     dem_full_path,
                                                     self.dem_array,
                                                     self.no_data_value,
                                                     partialsCreateAndLoad,
                                                     sombrasOutResults,
                                                     self.hill_params,
                                                     out_path)
           
            if not partialsCreateAndLoad:
                self.dir_funs.remove_temp_file(dem_full_path)
                intermediate_folder = os.path.split(
                        self.laspyRasterize.dirs['dem'])[0]
                self.dir_funs.remove_temp_dir(self.laspyRasterize.dirs['dem'])
                self.dir_funs.remove_temp_dir(intermediate_folder)
                
            self.showMessage('Process finisehd: {} file created'.format(
                    self.HillDEM.file_templates['composed_hillshade'].format(
                            base_name)), MESSAGE_LEVEL)

        else:
            self.showMessage('Starting processing DEM data {}'.format(
                                    base_name), MESSAGE_LEVEL)

            self.dem_array, self.no_data_value = raster_funs.raster_2_array(
                                                        full_filename)

            self.HillDEM = hillshader_process.HillshaderDEM(
                                                     full_filename,
                                                     self.dem_array,
                                                     self.no_data_value,
                                                     partialsCreateAndLoad,
                                                     sombrasOutResults,
                                                     self.hill_params,
                                                     out_path)

            self.showMessage('Process finisehd: {} file created'.format(
                    self.HillDEM.file_templates['composed_hillshade'].format(
                            base_name)), MESSAGE_LEVEL)

    def createDictParams(self):
        """This function starts the dictionaries used in process module.
            One dictionary for FUSION catalog report and the other for
            the three light exposures of the hillshades
        """

        self.hill_params = {
                'azimuth1': self.azimuth1DoubleSpinBox.value(),
                'azimuth2': self.azimuth2DoubleSpinBox.value(),
                'azimuth3': self.azimuth3DoubleSpinBox.value(),
                'angle_altitude1':\
                        self.angleAltitude1DoubleSpinBox.value(),
                'angle_altitude2':\
                        self.angleAltitude2DoubleSpinBox.value(),
                'angle_altitude3':\
                        self.angleAltitude3DoubleSpinBox.value(),
                'transparency1':\
                        self.transparency1DoubleSpinBox.value()/100,
                'transparency2':\
                        self.transparency2DoubleSpinBox.value()/100,
                'transparency3':\
                        self.transparency3DoubleSpinBox.value()/100
                }

    def showMessage(self, message, msg_level):
        """This function shows a QGIS message bar when is called with the
        message and the message Level -i.e.:INFO-
        """
        self.iface.messageBar().pushMessage(
                message, level=msg_level)

    def showQMessage(self, message, msg_level = "Error message"):
        """This function shows a Qt message dialog when is called with the
        message and the message Level-
        """
        QtWidgets.QMessageBox.warning(self, msg_level, message)