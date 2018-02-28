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

from . import hillshade as hill
from . import bandCalc
from .plugin_utils import lidar_process_funs as lidar_funs
from .plugin_utils import raster_funs
from .plugin_utils import files_and_dirs_funs

class LiDAR2DTM(object):

    def __init__(self, input_filename, out_path,
                 partials_create_and_load, size_dtm, catalog_params=None):
        """Function to start class variables and launch the process
        """

        self.input_file_full_path = input_filename
        self.out_path = out_path
        self.catalog_params = catalog_params
        self.partials_create_and_load = partials_create_and_load
        self.size_dtm = size_dtm

        self.init_paths()
        self.process()

    def init_paths(self):
        """Function to init the output directory and the results full paths.
            Also launch the folder creation
        """
        self.path, self.file_name = os.path.split(self.input_file_full_path)

        self.file_funs = files_and_dirs_funs.DirAndPaths()
        self.input_base_name, self.input_ext = \
                self.file_funs.init(self.file_name)

        self.file_templates = self.file_funs.file_templates(
                self.input_base_name)

        self.temp_dirs, self.temp_paths = \
                        self.file_funs.set_temp_dir()

        self.out_dirs, self.out_paths = \
                        self.file_funs.set_output_dir(
                                self.out_path)

        dirs = []

        if self.partials_create_and_load:
            self.paths = {'las': self.out_paths['las'],
                          'dtm': self.out_paths['dtm']}
            dirs.append(self.out_dirs['las'])
            dirs.append(self.out_dirs['dtm'])
        else:
            self.paths = {'las': self.temp_paths['las'],
                          'dtm': self.temp_paths['dtm']}
            dirs.append(self.temp_dirs['temp_dir'])
            dirs.append(self.temp_dirs['temp_dir'])

        if not self.catalog_params is None:
            self.paths['catalog'] = self.out_paths['catalog']
            self.paths['las_ground'] = self.out_paths['las_ground']
            dirs.append(self.out_dirs['catalog'])
            dirs.append(self.out_dirs['las_ground'])

        for v in dirs:
            self.file_funs.create_dir(v)

    def process(self):
        """This function runs the LiDAR processing
        """

        if  self.input_ext.lower() == '.laz':
            self.las_full_path = self.paths['las']
            lidar_funs.laz2las(self.input_file_full_path, self.las_full_path)
        else:
            self.las_full_path = self.input_file_full_path

        if self.catalog_params is not None:
            lidar_funs.filter_las_ground_points(
                self.las_full_path, self.paths['las_ground'])
            lidar_funs.create_catalog(self.paths['las_ground'],
                               self.catalog_params,
                               self.paths['catalog'])

        lidar_funs.create_dtm(
            self.las_full_path, self.paths['dtm'], self.size_dtm)

class HillshaderDTM(object):

    def __init__(self, full_filename, dtm_array,
                 partialsCreateAndLoad, sombrasOutResults, hill_params,
                 out_path):
        """Function to start class variables and launch the process
        """

        self.path, self.file_name = os.path.split(full_filename)

        self.file_funs = files_and_dirs_funs.DirAndPaths()
        self.out_path = out_path
        self.input_base_name, _, = \
                self.file_funs.init(self.file_name)

        if not os.path.exists(self.out_path):
            os.makedirs(self.out_path)

        self.dtm_full_path = full_filename
        self.hill_params = hill_params
        self.partials_create_and_load = partialsCreateAndLoad
        self.sombras_out = sombrasOutResults

        self.init_paths()
        self.process(dtm_array)

    def init_paths(self):
        """Function to init the output directory and the results full paths.
        """
        self.file_templates = self.file_funs.file_templates(
                self.input_base_name)

        self.temp_dirs, self.temp_paths = \
                        self.file_funs.set_temp_dir()

        self.out_dirs, self.out_paths = \
                        self.file_funs.set_output_dir(self.out_path)

        self.paths = {}
        self.dirs = {}
        self.paths['composed_hillshade'] = self.out_paths['composed_hillshade']
        self.dirs['composed_hillshade'] = self.out_dirs['composed_hillshade']
        self.file_funs.create_dir(self.dirs['composed_hillshade'])
        if self.partials_create_and_load:
            self.paths['simple_hillshade'] = self.out_paths['simple_hillshade']
            self.dirs['simple_hillshade'] = self.out_dirs['simple_hillshade']
            self.file_funs.create_dir(self.dirs['simple_hillshade'])

    def process(self, dtm_array):
        """This function works with the partial hillshades and generates the
        composed hillshade
        """
        hillshade_1_array = hill.hillshade(dtm_array,
                                           self.hill_params['azimuth1'],
                                           self.hill_params['angle_altitude1'])
        hillshade_2_array = hill.hillshade(dtm_array,
                                           self.hill_params['azimuth2'],
                                           self.hill_params['angle_altitude2'])
        hillshade_3_array = hill.hillshade(dtm_array,
                                           self.hill_params['azimuth3'],
                                           self.hill_params['angle_altitude3'])

        if self.partials_create_and_load:

            hillshade1, hillshade1_filename = self.save_raster(
                    hillshade_1_array,
                    self.hill_params['azimuth1'],
                    self.hill_params['angle_altitude1'])

            hillshade2, hillshade2_filename = self.save_raster(
                    hillshade_2_array,
                    self.hill_params['azimuth2'],
                    self.hill_params['angle_altitude2'])

            hillshade3, hillshade3_filename = self.save_raster(
                    hillshade_3_array,
                    self.hill_params['azimuth3'],
                    self.hill_params['angle_altitude3'])

            self.partial_hills_dic = {hillshade1_filename: hillshade1,
                                      hillshade2_filename: hillshade2,
                                      hillshade3_filename: hillshade3}

            for k, v in self.partial_hills_dic.items():
                raster_funs.load_raster_layer(v, k)

        three_exp_array = bandCalc.merge_arrays(
                [hillshade_1_array, hillshade_2_array, hillshade_3_array],
                [self.hill_params['transparency1'],
                 self.hill_params['transparency2'],
                 self.hill_params['transparency3']])

        fn_hillshade_filename = \
            self.file_templates['composed_hillshade'].format(
                    self.input_base_name)
        raster_funs.array_2_raster(three_exp_array,
                                   self.dtm_full_path,
                                   self.paths['composed_hillshade'])

        if self.sombras_out:
            raster_funs.load_raster_layer(
                    self.paths['composed_hillshade'], fn_hillshade_filename)

    def save_raster(self, hillshade_array, azimuth, altitude):
        """This function save the arrays of the partial hillshades
        """
        hillshade_filename = self.file_templates['simple_hillshade'].format(
                self.input_base_name, azimuth, altitude)

        hillshade_path = os.path.join(self.dirs['simple_hillshade'],
                                      hillshade_filename)
        raster_funs.array_2_raster(hillshade_array,
                                   self.dtm_full_path,
                                   hillshade_path)

        return hillshade_path, hillshade_filename
