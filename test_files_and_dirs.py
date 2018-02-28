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
 Test lidar mode processing
"""

import unittest
import tempfile
import os

from qgis.core import QgsApplication

from plugin_utils import files_and_dirs_funs as filedirs

out_path = tempfile.mkdtemp()

class FilesAndDirsTestCase(unittest.TestCase):

    def setUp(self):
        self.dir_path_utils = filedirs.DirAndPaths()
        self.base_name, _ =self.dir_path_utils.init('file.las')
        self.templates = self.dir_path_utils.file_templates(self.base_name)

    def test_temp_dirs_creation(self):

        self.dir_path_utils.set_temp_dir()
        self.assertIsNotNone(self.dir_path_utils.temp_dirs)

        for k, v in self.dir_path_utils.temp_dirs.items():
            self.dir_path_utils.create_dir(v)
            self.assertTrue(os.path.exists(v))

    def test_temp_dirs_removing(self):

        self.dir_path_utils.set_temp_dir()
        self.assertIsNotNone(self.dir_path_utils.temp_dirs)

        for k, v in self.dir_path_utils.temp_dirs.items():
            self.dir_path_utils.create_dir(v)
            self.dir_path_utils.remove_temp_dir(v)
            self.assertFalse(os.path.exists(v))

    def test_out_dirs_creation(self):

        self.dir_path_utils.set_output_dir(out_path)
        self.assertIsNotNone(self.dir_path_utils.out_dirs)

        for k, v in self.dir_path_utils.out_dirs.items():
            self.dir_path_utils.create_dir(v)
            self.assertTrue(os.path.exists(v))

        for k, v in self.dir_path_utils.out_full_paths.items():
            self.assertIsNotNone(v)

    def tearDown(self):
        pass


def qgis_app_init():
    from qgis.PyQt import QtWidgets
    import os
    import atexit
    atexit.register(QgsApplication.exitQgis)

    app = QtWidgets.QApplication([])
    qgis_prefix = os.getenv("QGIS_PREFIX_PATH")
    # Initialize qgis libraries
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    return app

app = qgis_app_init()

if __name__ == "__main__":

    unittest.main()
