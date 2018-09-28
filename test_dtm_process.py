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
import unittest
import tempfile
import os

from qgis.core import QgsApplication

import hillshader_process
import hillshade
import bandCalc

from plugin_utils import raster_funs

class DEMProcessTestCase(unittest.TestCase):

    def setUp(self):
        """Initializing input data and dictionaries
        """
        self.input_dem_file = '.\\test_data\\dem_input'
        ext = '.tif'
        # ext = '.asc'
        self.input_dem = self.input_dem_file + ext

        hillshade_params = {}
        hillshade_params['azimuth1'] = 350
        hillshade_params['azimuth2'] = 15
        hillshade_params['azimuth3'] = 270
        hillshade_params['angle_altitude1'] = 70
        hillshade_params['angle_altitude2'] = 60
        hillshade_params['angle_altitude3'] = 55
        hillshade_params['transparency1'] = 50
        hillshade_params['transparency2'] = 65
        hillshade_params['transparency3'] = 70
        self.hill_params = hillshade_params

    def test_input(self):
        """Test for input data
        """
        self.assertTrue(os.path.exists(self.input_dem))

    def test_generating_hillshades_array(self):
        """test generating partial hillshades arrays from dem
        """
        dem_array = raster_funs.raster_2_array(self.input_dem)
        hillshade_1 = hillshade.hillshade(dem_array,
                                          self.hill_params['azimuth1'],
                                          self.hill_params['angle_altitude1'])
        hillshade_2 = hillshade.hillshade(dem_array,
                                          self.hill_params['azimuth2'],
                                          self.hill_params['angle_altitude2'])
        hillshade_3 = hillshade.hillshade(dem_array,
                                          self.hill_params['azimuth3'],
                                          self.hill_params['angle_altitude3'])

        self.assertIsNotNone(hillshade_1)
        self.assertIsNotNone(hillshade_2)
        self.assertIsNotNone(hillshade_3)

    def test_generating_hillshades_raster(self):
        """test generating partial hillshades rasters from dem
        """
        temp_dir = tempfile.mkdtemp()

        output_folder = os.path.join(temp_dir,'hillshader_results')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        array = raster_funs.raster_2_array(self.input_dem)

        raster_funs.array_2_raster(array,
                                   self.input_dem,
                                   os.path.join(output_folder, 'file.tif'))

        self.assertTrue(os.path.exists(
                os.path.join(output_folder, 'file.tif')))

    def test_combinig_hillshades_arrays(self):
        """test combining arrays (band calculator)
        """
        dem_array = raster_funs.raster_2_array(self.input_dem)
        hillshade_1_array = hillshade.hillshade(dem_array,
                                          self.hill_params['azimuth1'],
                                          self.hill_params['angle_altitude1'])
        hillshade_2_array = hillshade.hillshade(dem_array,
                                          self.hill_params['azimuth2'],
                                          self.hill_params['angle_altitude2'])
        hillshade_3_array = hillshade.hillshade(dem_array,
                                          self.hill_params['azimuth3'],
                                          self.hill_params['angle_altitude3'])

        combined_array = bandCalc.merge_arrays(
                [hillshade_1_array, hillshade_2_array, hillshade_3_array],
                [self.hill_params['transparency1'],
                 self.hill_params['transparency2'],
                 self.hill_params['transparency3']])

        output_folder = os.path.join(tempfile.mkdtemp(),
                                          'hillshader_results')
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        out_put = os.path.join(output_folder, 'combined_hillshade.tif')
        raster_funs.array_2_raster(combined_array, self.input_dem, out_put)

        self.assertTrue(os.path.exists(out_put))

        self.assertNotAlmostEquals(0, combined_array.any())
        self.assertEqual(combined_array.shape, (100, 100))
        self.assertAlmostEqual(int(combined_array.max()), 255)
        self.assertAlmostEqual(int(combined_array.min()), 0)
        self.assertAlmostEqual(int(combined_array.mean()), 255/2)

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
