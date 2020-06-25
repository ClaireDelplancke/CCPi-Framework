# -*- coding: utf-8 -*-
#  CCP in Tomographic Imaging (CCPi) Core Imaging Library (CIL).

#   Copyright 2017 UKRI-STFC
#   Copyright 2017 University of Manchester

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ccpi.framework import DataProcessor, AcquisitionData, ImageData
import warnings
import numpy


class TransmissionAbsorptionConverter(DataProcessor):

    def __init__(self,
                 threshold = 1e-3,
                 value = 0
                 ):

        kwargs = {'threshold': threshold,
                  'value': value}

        super(TransmissionAbsorptionConverter, self).__init__(**kwargs)
    
    def check_input(self, data):
        
        if not ((isinstance(data, ImageData)) or 
                (isinstance(data, AcquisitionData))):
            raise Exception('Processor supports only following data types:\n' +
                            ' - ImageData\n - AcquisitionData')
        elif (data.geometry == None):
            raise Exception('Geometry is not defined.')
        else:
            return True 

    def process(self):
        
        data_raw = self.get_input()
        data = data_raw.geometry.allocate(self.value)
        mask = data_raw.as_array() > self.threshold
        data.as_array()[mask] = -1 * numpy.log(data_raw.as_array()[mask])
        
        return data