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
from __future__ import unicode_literals
import tempfile
import os

class DirAndPaths(object):
    
    def init(self, file_name):
        """Get the base name and the extnesion os a given filename
        """
        self.base_name, extension = os.path.splitext(file_name)
        
        return self.base_name, extension
    
    def file_templates(self, base_name):
        """Init and create the file templates
        """
        self.templates = {'las': '{}_las.las',
                          'catalog': '{}_ground_catalog.csv',
                          'dem': '{}_dem.tif',
                          'simple_hillshade': '{}_{}_{}_SimpleHillshade.tif',
                          'composed_hillshade': '{}_ComposedHillshade.tif'}
        
        return self.templates
        
    def set_temp_dir(self):
        """Set the temporal directories and full paths of intermediate files
        """
        self.temp_dirs = {}
        self.temp_full_paths = {}
        
        self.temp_dirs['temp_dir'] = tempfile.mkdtemp()
        
        self.temp_full_paths['las'] = os.path.join(
                self.temp_dirs['temp_dir'], 
                self.templates['las'].format(self.base_name))
        
        self.temp_full_paths['dem'] = os.path.join(
                self.temp_dirs['temp_dir'], 
                self.templates['dem'].format(self.base_name))
        
        return self.temp_dirs, self.temp_full_paths
    
    def create_dir(self, directory):
        """Create the specified folder
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def remove_temp_file(self, full_path):
        """Remove the specified file
        """
        if os.path.exists(full_path):
            os.remove(full_path)
            
    def remove_temp_dir(self, directory):
        """Remove the specified folder
        """
        if os.path.exists(directory):
            os.rmdir(directory)
            
    def set_output_dir(self, out_path):
        """ Set and create the output dirs
        """
        
        self.out_dirs = {}
        self.out_full_paths = {}
        
        intermediate_folder = os.path.join(out_path, 'intermediate_results')
        
        self.out_dirs['las'] = os.path.join(intermediate_folder, 'las')
        self.out_dirs['catalog'] = os.path.join(out_path, 'catalog-report')
        self.out_dirs['las_ground'] = os.path.join(self.out_dirs['catalog'],
                     'ground_points')
        self.out_dirs['dem'] = os.path.join(intermediate_folder, 'dem')
        self.out_dirs['simple_hillshade'] = os.path.join(
                        intermediate_folder, 'simple_hillshades')
        self.out_dirs['composed_hillshade'] = out_path

        self.out_full_paths['las'] = \
            os.path.join(self.out_dirs['las'], 
                         self.templates['las'].format(self.base_name)) 
            
        self.out_full_paths['las_ground'] = os.path.join(
                self.out_dirs['las_ground'], 
                         self.templates['las'].format(self.base_name)) 
        
        self.out_full_paths['catalog'] = \
            os.path.join(self.out_dirs['catalog'], 
                         self.templates['catalog'].format(self.base_name))   
            
        self.out_full_paths['dem'] = os.path.join(self.out_dirs['dem'], 
                           self.templates['dem'].format(self.base_name))
        
        self.out_full_paths['simple_hillshade'] = os.path.join(
                self.out_dirs['simple_hillshade'], 
                self.templates['simple_hillshade'])
        
        self.out_full_paths['composed_hillshade'] = os.path.join(
                self.out_dirs['composed_hillshade'], 
                self.templates['composed_hillshade'].format(self.base_name))
    
        return self.out_dirs, self.out_full_paths