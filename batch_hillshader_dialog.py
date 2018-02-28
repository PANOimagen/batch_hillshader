# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Batch_Hillshader
                                 A QGIS plugin  to generate a three light
                                 exposure hillshade (shaded relief by
                                 combining three light exposures)

    For more information, see the program documentation.

    If you uses as input LiDAR data, note that plugin uses LASTools library.
        See LASTools License at  <https://rapidlasso.com/lastools/>

    Plugin also use in LiDAR data mode FUSION LDV.
        See FUSION LDV License at <http://forsys.cfr.washington.edu/fusion.html>
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
from .plugin_utils import lidar_process_funs as lidar_funs
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
    

try:
    from . import laspy_utils
    HAS_LASPY = True
except ImportError:
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
        self.LidarFilesGroupBox.setChecked(False)
        self.runCatalogCheckBox.setChecked(False)
        self.laspyCheckBox.setChecked(False)
        self.loadHillShadeCheckBox.setChecked(True)
        self.loadPartialsCheckBox.setChecked(False)
        self.sizeDTMBox.setEnabled(False)
        self.sizeDTMLabel.setEnabled(False)
        self.laspyGroupBox.setEnabled(False)
        self.copyrightLabel.setText('(C) 2017 by Panoimagen S.L.')
#        self.laspyRecomendedPixelLabel.setText(
#                'Recomended pixel size: - meters')
        self.currentDTMPixelSizeLabel.setText(
                'Input DTM pixel size: - x - meters')
        self.currentPxSizeLabel.setText(
                'Selected pixel size for hillshade results: - x - meters')
        self.inputLidarToolButton.clicked.connect(self.lidarProcess)
        self.laspyToolButton.clicked.connect(self.laspyProcess)
        self.outputFolderToolButton.clicked.connect(self.setOutPath)
        self.inputDTMToolButton.clicked.connect(self.DTMProcess)
        self.LidarProcessCheckBox.clicked.connect(self.updateUi)
        self.LidarProcessCheckBox.clicked.connect(
                self.hillshadePixelSize)
        self.laspyCheckBox.clicked.connect(self.updateUi)
        self.laspyCheckBox.clicked.connect(self.hillshadePixelSize)
        self.runCatalogCheckBox.clicked.connect(self.updateUi)
        self.inputDTMLineEdit.textChanged.connect(self.updateDTMPixelSize)
        self.sizeDTMBox.valueChanged.connect(self.hillshadePixelSize)
        self.laspyPixelSizeDoubleSpinBox.valueChanged.connect(
                self.hillshadePixelSize)
        self._initVersion()
        self.initLastoolsPathsUi()
        self.initLaspyUi()

# TODO: connect this objects: laspyCheckBox, laspyLineEdit, laspyPixelSizeDoubleSpinBox, laspyRecomendedPixelLabel, laspyGroupBox

    def _initVersion(self):
        self.versionLabel.setText('Batch Hillshader version {}'.format(
                version.VERSION))
        
    @staticmethod
    def checkProcessingAvaible():
        """Check if processing plugin is avaible
        """
        try:
            return lidar_funs.search_lastools_path() != ''
        except AttributeError:
            return False

    @staticmethod
    def checkLASToolsPath():
        """Return LASTools_path and True if LASTools_path exists
        """
        path = lidar_funs.search_lastools_path()
        return path, path != ''

    @staticmethod
    def checkFusionPath():
        """Return Fusion_path and True if Fusion_path exists
        """
        path = lidar_funs.search_fusion_path()
        return path, path != ''

    def _initLastoolsUI(self, processing_funs, LASTools_path, Fusion_path):
        """This function enabled/disabled the lidar processing options and
            define the labels for user information
        """
        self.LidarProcessCheckBox.setEnabled(processing_funs)
        self.LidarProcessCheckBox.setEnabled(LASTools_path != '')
        self.runCatalogCheckBox.setEnabled(Fusion_path != '')

        if not processing_funs:
            processing_label = ('The Processing Plugin is not avaible,' +
                                ' LiDAR Processing mode disabled. Please,' +
                                ' read Batch Hillshader documentation')
            LASTools_label = 'not found'
            FUSION_label = 'not found'
            Proc_label_color = 'color: red'
            LASTools_label_color = 'color: red'
            Fusion_label_color = 'color: red'
        else:
            processing_label = ('The Processing Plugin is avaible,' +
                                ' LiDAR Processing mode enabled')
            Proc_label_color = u'color: black'
            if not LASTools_path:
                LASTools_label = u'not found'
                LASTools_label_color = 'color: red'
            else:
                LASTools_label = LASTools_path
                LASTools_label_color = 'color: black'
            if not Fusion_path:
                FUSION_label = u'not found'
                Fusion_label_color = 'color: red'
            else:
                FUSION_label = Fusion_path
                Fusion_label_color = 'color: black'

        self.LASToolsFolderLabel.setText(u'LASTools folder: {}'.format(
                LASTools_label))
        self.LASToolsFolderLabel.setStyleSheet(LASTools_label_color)
        self.FusionFolderLabel.setText(u'FUSION folder: {}'.format(
                FUSION_label))
        self.FusionFolderLabel.setStyleSheet(Fusion_label_color)
        self.ProcessingModuleLabel.setText(processing_label)
        self.ProcessingModuleLabel.setStyleSheet(Proc_label_color)

    def initLastoolsPathsUi(self):
        processing_funs = self.checkProcessingAvaible()
        LASTools_path, LASTools_exists = self.checkLASToolsPath()
        Fusion_path, Fusion_exists = self.checkFusionPath()
        self._initLastoolsUI(processing_funs,
                             LASTools_path,
                             Fusion_path)
        
    def initLaspyUi(self):
        methods = ['nearest', 'linear', 'cubic']
        self.interpolatingMethodComboBox.addItems(methods)
        laspy_text = 'LasPy Library is {}'
        if not HAS_LASPY:
            surname_label = (u'not installed. Read plugin documentation to' +
                             u' install LasPy Library')
            label_color = 'color: red'

        else:
            surname_label = u'installed'
            label_color = 'color: black'
            
        self.laspyCheckBox.setEnabled(HAS_LASPY)
        self.laspyImportLabel.setText(laspy_text.format(surname_label))
        self.laspyImportLabel.setStyleSheet(label_color)
        
        
    def updateUi(self):
        """Update UI QObjects
        """

        self.lidar_checked = self.LidarProcessCheckBox.isChecked()
        self.laspy_checked = self.laspyCheckBox.isChecked()

        if self.lidar_checked or self.laspy_checked:
            disable_DTM = True
            self.inputDTMLineEdit.clear()
            self.currentDTMPixelSizeLabel.setText(
                'Input DTM pixel size: - x - meters')
        else:
            disable_DTM = False  
            self.inputLidarLineEdit.clear()
            self.runCatalogCheckBox.setChecked(False)
            self.laspyLineEdit.clear()

        self.catalog_checked = self.runCatalogCheckBox.isChecked()

        self.inputLidarLineEdit.setEnabled(self.lidar_checked)
        self.inputLidarToolButton.setEnabled(self.lidar_checked)
        self.LidarFilesGroupBox.setEnabled(self.lidar_checked)
        self.sizeDTMBox.setEnabled(disable_DTM)
        self.sizeDTMLabel.setEnabled(disable_DTM)
        self.runCatalogCheckBox.setEnabled(self.lidar_checked)
        self.inputDTMLineEdit.setEnabled(not disable_DTM)
        self.inputDTMToolButton.setEnabled(not disable_DTM)
        self.currentDTMPixelSizeLabel.setEnabled(not disable_DTM)
        self.inputDTMLabel.setEnabled(not disable_DTM)
        self.catalogGroupBox.setEnabled(self.catalog_checked)
        self.laspyGroupBox.setEnabled(self.laspy_checked)

    def updateDTMPixelSize(self):
        """Set input DTM pixel size when the process starts with an input
            DTM
        """
        dtm_path = self.inputDTMLineEdit.text()
        if dtm_path:
            dtm_ds = gdal.Open(dtm_path)
            try:
                self.dtm_geo_info = dtm_ds.GetGeoTransform()
                pixel_with = self.dtm_geo_info[1]
                pixel_height = self.dtm_geo_info[5]
                pixel_size_label = ('Input DTM pixel size' +
                                    ': {} x {} meters'.format(
                        pixel_with, pixel_height))
                self.currentDTMPixelSizeLabel.setText(pixel_size_label)
                self.hillshadePixelSize()
            except AttributeError:
                self.currentDTMPixelSizeLabel.setText(
                        'Input DTM pixel size: - x - meters')
        else:
            self.dtm_geo_info = None

    def hillshadePixelSize(self):
        """Set the hillshade results pixel size and update the label
        """

        try:
            if self.LidarProcessCheckBox.isChecked():
                dtm_pixel_size = [self.sizeDTMBox.value(),
                                  -(self.sizeDTMBox.value())]
                self.updateHillshadeSizeLabel(dtm_pixel_size[0],
                                                   dtm_pixel_size[-1])
                return
            
            elif self.laspyCheckBox.isChecked():
                dtm_pixel_size = [self.laspyPixelSizeDoubleSpinBox.value(),
                                  -(self.laspyPixelSizeDoubleSpinBox.value())]    
                self.updateHillshadeSizeLabel(dtm_pixel_size[0], 
                                              dtm_pixel_size[-1])
                return
            
        except AttributeError:
            pass

        try:
            if self.dtm_geo_info is None:
                self.updateHillshadeSizeLabel('-','-')
            else:
                self.hillshadePxSize = [self.dtm_geo_info[1],
                                        self.dtm_geo_info[5]]
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

    def lidarProcess(self):
        """Processing with Lidar data. Using Fusion and Lastools Set input file and start output folder
        """
        fileNames = getOpenFileNames(self,
                "Select the input LiDAR file/s",
                self.inputLidarToolButton.text(),
                ("LiDAR files (*.laz *.LAZ *.las *.LAS);;" +
                 " LAZ (*.laz *.LAZ);;LAS (*.las *.LAS);;" +
                 " All files (*)"))
        if fileNames:
            # quoted = ['"{}"'.format(fn) for fn in fileNames]
            self.inputLidarLineEdit.setText(", ".join(fileNames[0]))
            if not self.outputFolderLineEdit.text():
                outPath = os.path.join(
                    os.path.split(os.path.abspath(fileNames[0][0]))[0],
                    'batch_hillshader_output')
                self.outputFolderLineEdit.setText(outPath)
    
    def laspyProcess(self):
        """ Processing with Lidar data. Using laspy library Set input file 
            and start output folder
        """
        fileNames = getOpenFileNames(self,
                "Select the input LiDAR file/s",
                self.inputLidarToolButton.text(),
                ("LiDAR *.las files (*.las *.LAS);;" +
                 " All files (*)"))
        if fileNames:
            # quoted = ['"{}"'.format(fn) for fn in fileNames]
            self.laspyLineEdit.setText(", ".join(fileNames[0]))
            if not self.outputFolderLineEdit.text():
                outPath = os.path.join(
                    os.path.split(os.path.abspath(fileNames[0][0]))[0],
                    'batch_hillshader_output')
                self.outputFolderLineEdit.setText(outPath)
                
    def DTMProcess(self):
        """Processing with DTM data. Set input file and start output folder
        """
        fileNames = getOpenFileNames(self,
                "Select the DTM input file/s",
                self.inputDTMToolButton.text(),
                ("Raster files (*.tif *.tiff *.TIF *.TIFF *.asc *.ASC);;" +
                 "GEOTiff (*.tif *.tiff *.TIF *.TIFF);;" +
                 " ASCII Grid (*.asc *.ASC);; All files (*)"))

        if fileNames:
            # quoted = ['"{}"'.format(fn) for fn in fileNames]
            self.inputDTMLineEdit.setText(", ".join(fileNames[0]))
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
        if self.LidarProcessCheckBox.isChecked():
            filenames = self.inputLidarLineEdit.text()
            self.processMode = 'LidarInput'
        
        elif self.laspyCheckBox.isChecked():
            filenames = self.laspyLineEdit.text()
            self.processMode = 'laspyInput'
        
        else:
            filenames = self.inputDTMLineEdit.text()
            self.processMode = 'DTMInput'

        if not filenames:
            self.showQMessage("Error: Not input file selected!\nPlease," +
                              "select one.")

        outPath = self.outputFolderLineEdit.text()
        if not outPath:
            self.showQMessage("Error: Not output folder selected!\n" +
                              "Please, select one.")

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
        if self.LidarProcessCheckBox.isChecked():
            sizeDTM = self.sizeDTMBox.value()
        elif self.laspyCheckBox.isChecked():
            sizeDTM = self.laspyPixelSizeDoubleSpinBox.value()
            
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
        
        if self.LidarProcessCheckBox.isChecked():

            self.showMessage(u'Starting processing LiDAR data {}'.format(
                                    base_name) +
                             u' with FUSION LDV and LASTools Library', 
                             MESSAGE_LEVEL)

            self.lidar2dtm = hillshader_process.LiDAR2DTM(
                                                     full_filename,
                                                     out_path,
                                                     partialsCreateAndLoad,
                                                     sizeDTM,
                                                     self.catalog_params)

            if self.catalog_params:
                self.showMessage((u'Catalog report for ground LiDAR' +
                                  u' points ready'),MESSAGE_LEVEL)

            dtm_full_path = self.lidar2dtm.paths['dtm']
            self.dtm_array = raster_funs.raster_2_array(
                        dtm_full_path)

            if partialsCreateAndLoad:
                dtm_filename, _ = os.path.splitext(
                        os.path.split(dtm_full_path)[-1])
                raster_funs.load_raster_layer(
                            dtm_full_path,
                            dtm_filename)

            self.showMessage('Processing data... {}'.format(base_name),
                                  MESSAGE_LEVEL)

            self.HillDTM = hillshader_process.HillshaderDTM(
                                                     dtm_full_path,
                                                     self.dtm_array,
                                                     partialsCreateAndLoad,
                                                     sombrasOutResults,
                                                     self.hill_params,
                                                     out_path)

            if partialsCreateAndLoad:
                temp_files_list = os.listdir(
                        self.lidar2dtm.temp_dirs['temp_dir'])
                if len(temp_files_list) != 0:
                    for temp_file in temp_files_list:
                        file_path = os.path.join(
                                self.lidar2dtm.temp_dirs['temp_dir'],
                                temp_file)
                        self.dir_funs.remove_temp_file(file_path)
                temp_files_list = os.listdir(
                        self.lidar2dtm.temp_dirs['temp_dir'])
                if len(temp_files_list) == 0:
                    self.dir_funs.remove_temp_dir(
                            self.lidar2dtm.temp_dirs['temp_dir'])

            self.showMessage('Process finisehd: {} file created'.format(
                    self.HillDTM.file_templates['composed_hillshade'].format(
                            base_name)), MESSAGE_LEVEL)
        
        elif self.laspyCheckBox.isChecked():

            self.showMessage('Starting processing LiDAR data {}'.format(
                                    base_name) +
                             u' with LasPy Library', MESSAGE_LEVEL)
            self.inter_method = self.interpolatingMethodComboBox.currentText()
            self.laspyLidar = laspy_utils.LiDAR(full_filename,
                                                out_path,
                                                partialsCreateAndLoad)
            
            self.lidar_arrays_list, self.las_file_extent, self.density =\
                        self.laspyLidar.process()

            self.lidar_results = [self.lidar_arrays_list, 
                                  self.las_file_extent, 
                                  self.density]

            self.laspyRasterize = laspy_utils.RasterizeLiDAR(
                                                    full_filename,
                                                    self.lidar_results,
                                                    out_path,
                                                    self.inter_method, 
                                                    sizeDTM)
              
            self.interpolated_grid = self.laspyRasterize.interpolate_grid()
              
            dtm_full_path = self.laspyRasterize.array_2_raster(
                                                    self.interpolated_grid)
            
            self.dtm_array = raster_funs.raster_2_array(dtm_full_path)
            
            if partialsCreateAndLoad:
                dtm_filename, _ = os.path.splitext(
                            os.path.split(dtm_full_path)[-1])
                raster_funs.load_raster_layer(
                            dtm_full_path,
                            dtm_filename)

            self.showMessage('Processing data... {}'.format(base_name),
                                  MESSAGE_LEVEL)

            self.HillDTM = hillshader_process.HillshaderDTM(
                                                     dtm_full_path,
                                                     self.dtm_array,
                                                     partialsCreateAndLoad,
                                                     sombrasOutResults,
                                                     self.hill_params,
                                                     out_path)
           
            if not partialsCreateAndLoad:
                self.dir_funs.remove_temp_file(dtm_full_path)
                intermediate_folder = os.path.split(
                        self.laspyRasterize.dirs['dtm'])[0]
                self.dir_funs.remove_temp_dir(self.laspyRasterize.dirs['dtm'])
                self.dir_funs.remove_temp_dir(intermediate_folder)
                
            self.showMessage('Process finisehd: {} file created'.format(
                    self.HillDTM.file_templates['composed_hillshade'].format(
                            base_name)), MESSAGE_LEVEL)

        else:
            self.showMessage('Starting processing DTM data {}'.format(
                                    base_name), MESSAGE_LEVEL)

            self.dtm_array = raster_funs.raster_2_array(full_filename)

            self.HillDTM = hillshader_process.HillshaderDTM(
                                                     full_filename,
                                                     self.dtm_array,
                                                     partialsCreateAndLoad,
                                                     sombrasOutResults,
                                                     self.hill_params,
                                                     out_path)

            self.showMessage('Process finisehd: {} file created'.format(
                    self.HillDTM.file_templates['composed_hillshade'].format(
                            base_name)), MESSAGE_LEVEL)

    def createDictParams(self):
        """This function starts the dictionaries used in process module.
            One dictionary for FUSION catalog report and the other for
            the three light exposures of the hillshades
        """
        if self.runCatalogCheckBox.isChecked():
            self.catalog_params = {
                    'size_density': self.sizeDensityBox.value(),
                    'min_density': self.minDensityBox.value(),
                    'max_density': self.maxDensityBox.value(),
                    'size1_density': self.size1ReturnBox.value(),
                    'min1_density': self.min1ReturnBox.value(),
                    'max1_density': self.max1ReturnBox.value(),
                    'size_intensity': self.sizeIntenBox.value(),
                    'min_intensity': self.minIntenBox.value(),
                    'max_intensity': self.maxIntenBox.value()
                    }

        else:
            self.catalog_params = None

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