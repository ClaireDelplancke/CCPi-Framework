# -*- coding: utf-8 -*-
#   This work is part of the Core Imaging Library developed by
#   Visual Analytics and Imaging System Group of the Science Technology
#   Facilities Council, STFC

#   Copyright 2018 Edoardo Pasca

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License

from ccpi.framework import DataSetProcessor, DataSet, VolumeData, SinogramData
from ccpi.reconstruction import geoms
import numpy
import h5py
from scipy import ndimage

class Normalizer(DataSetProcessor):
    '''Normalization based on flat and dark
    
    This processor read in a SinogramDataSet and normalises it based on 
    the instrument reading with and without incident photons or neutrons.
    
    Input: SinogramDataSet
    Parameter: 2D projection with flat field (or stack)
               2D projection with dark field (or stack)
    Output: SinogramDataSet
    '''
    
    def __init__(self):
        kwargs = {
                  'flat_field'  :None, 
                  'dark_field'  :None,
                  # very small number. Used when there is a division by zero
                  'tolerance'   : 1e-5
                  }
        
        #DataSetProcessor.__init__(self, **kwargs)
        super(Normalizer, self).__init__(**kwargs)
    
    def checkInput(self, dataset):
        if dataset.number_of_dimensions == 3:
               return True
        else:
            raise ValueError("Expected input dimensions is 2 or 3, got {0}"\
                             .format(dataset.number_of_dimensions))
    
    def setDarkField(self, df):
        if type(df) is numpy.ndarray:
            if len(numpy.shape(df)) == 3:
                raise ValueError('Dark Field should be 2D')
            elif len(numpy.shape(df)) == 2:
                self.dark_field = df
        elif issubclass(type(df), DataSet):
            self.dark_field = self.setDarkField(df.as_array())
    
    def setFlatField(self, df):
        if type(df) is numpy.ndarray:
            if len(numpy.shape(df)) == 3:
                raise ValueError('Flat Field should be 2D')
            elif len(numpy.shape(df)) == 2:
                self.flat_field = df
        elif issubclass(type(df), DataSet):
            self.flat_field = self.setDarkField(df.as_array())
    
    @staticmethod
    def normalizeProjection(projection, flat, dark, tolerance):
        a = (projection - dark)
        b = (flat-dark)
        with numpy.errstate(divide='ignore', invalid='ignore'):
            c = numpy.true_divide( a, b )
            c[ ~ numpy.isfinite( c )] = tolerance # set to not zero if 0/0 
        return c
    
    def process(self):
        
        projections = self.getInput()
        dark = self.dark_field
        flat = self.flat_field
        
        if not (projections.shape[1:] == dark.shape and \
           projections.shape[1:] == flat.shape):
            raise ValueError('Flats/Dark and projections size do not match.')
            
               
        a = numpy.asarray(
                [ Normalizer.normalizeProjection(
                        projection, flat, dark, self.tolerance) \
                 for projection in projections.as_array() ]
                )
        y = type(projections)( a , True, 
                    dimension_labels=projections.dimension_labels,
                    geometry=projections.geometry)
        return y
    

class CenterOfRotationFinder(DataSetProcessor):
    '''Processor to find the center of rotation in a parallel beam experiment
    
    This processor read in a SinogramDataSet and finds the center of rotation 
    based on Nghia Vo's method. https://doi.org/10.1364/OE.22.019078
    
    Input: SinogramDataSet
    
    Output: float. center of rotation in pixel coordinate
    '''
    
    def __init__(self):
        kwargs = {
                  
                  }
        
        #DataSetProcessor.__init__(self, **kwargs)
        super(CenterOfRotationFinder, self).__init__(**kwargs)
    
    def checkInput(self, dataset):
        if dataset.number_of_dimensions == 3:
            if dataset.geometry.geom_type == 'parallel':
                return True
            else:
                raise ValueError('This algorithm is suitable only for parallel beam geometry')
        else:
            raise ValueError("Expected input dimensions is 3, got {0}"\
                             .format(dataset.number_of_dimensions))
        
    
    # #########################################################################
    # Copyright (c) 2015, UChicago Argonne, LLC. All rights reserved.         #
    #                                                                         #
    # Copyright 2015. UChicago Argonne, LLC. This software was produced       #
    # under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
    # Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
    # U.S. Department of Energy. The U.S. Government has rights to use,       #
    # reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
    # UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
    # ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
    # modified to produce derivative works, such modified software should     #
    # be clearly marked, so as not to confuse it with the version available   #
    # from ANL.                                                               #
    #                                                                         #
    # Additionally, redistribution and use in source and binary forms, with   #
    # or without modification, are permitted provided that the following      #
    # conditions are met:                                                     #
    #                                                                         #
    #     * Redistributions of source code must retain the above copyright    #
    #       notice, this list of conditions and the following disclaimer.     #
    #                                                                         #
    #     * Redistributions in binary form must reproduce the above copyright #
    #       notice, this list of conditions and the following disclaimer in   #
    #       the documentation and/or other materials provided with the        #
    #       distribution.                                                     #
    #                                                                         #
    #     * Neither the name of UChicago Argonne, LLC, Argonne National       #
    #       Laboratory, ANL, the U.S. Government, nor the names of its        #
    #       contributors may be used to endorse or promote products derived   #
    #       from this software without specific prior written permission.     #
    #                                                                         #
    # THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
    # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
    # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
    # FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
    # Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
    # INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
    # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
    # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
    # CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
    # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
    # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
    # POSSIBILITY OF SUCH DAMAGE.                                             #
    # #########################################################################
    
    @staticmethod
    def as_ndarray(arr, dtype=None, copy=False):
        if not isinstance(arr, numpy.ndarray):
            arr = numpy.array(arr, dtype=dtype, copy=copy)
        return arr
    
    @staticmethod
    def as_dtype(arr, dtype, copy=False):
        if not arr.dtype == dtype:
            arr = numpy.array(arr, dtype=dtype, copy=copy)
        return arr
    
    @staticmethod
    def as_float32(arr):
        arr = CenterOfRotationFinder.as_ndarray(arr, numpy.float32)
        return CenterOfRotationFinder.as_dtype(arr, numpy.float32)
    
    
    
    
    @staticmethod
    def find_center_vo(tomo, ind=None, smin=-40, smax=40, srad=10, step=0.5,
                       ratio=2., drop=20):
        """
        Find rotation axis location using Nghia Vo's method. :cite:`Vo:14`.
    
        Parameters
        ----------
        tomo : ndarray
            3D tomographic data.
        ind : int, optional
            Index of the slice to be used for reconstruction.
        smin, smax : int, optional
            Reference to the horizontal center of the sinogram.
        srad : float, optional
            Fine search radius.
        step : float, optional
            Step of fine searching.
        ratio : float, optional
            The ratio between the FOV of the camera and the size of object.
            It's used to generate the mask.
        drop : int, optional
            Drop lines around vertical center of the mask.
    
        Returns
        -------
        float
            Rotation axis location.
            
        Notes
        -----
        The function may not yield a correct estimate, if:
        
        - the sample size is bigger than the field of view of the camera. 
          In this case the ``ratio`` argument need to be set larger
          than the default of 2.0.
        
        - there is distortion in the imaging hardware. If there's 
          no correction applied, the center of the projection image may 
          yield a better estimate.
        
        - the sample contrast is weak. Paganin's filter need to be applied 
          to overcome this. 
       
        - the sample was changed during the scan. 
        """
        tomo = CenterOfRotationFinder.as_float32(tomo)
    
        if ind is None:
            ind = tomo.shape[1] // 2
        _tomo = tomo[:, ind, :]
    
        
    
        # Reduce noise by smooth filters. Use different filters for coarse and fine search 
        _tomo_cs = ndimage.filters.gaussian_filter(_tomo, (3, 1))
        _tomo_fs = ndimage.filters.median_filter(_tomo, (2, 2))
    
        # Coarse and fine searches for finding the rotation center.
        if _tomo.shape[0] * _tomo.shape[1] > 4e6:  # If data is large (>2kx2k)
            #_tomo_coarse = downsample(numpy.expand_dims(_tomo_cs,1), level=2)[:, 0, :]
            #init_cen = _search_coarse(_tomo_coarse, smin, smax, ratio, drop)
            #fine_cen = _search_fine(_tomo_fs, srad, step, init_cen*4, ratio, drop)
            init_cen = CenterOfRotationFinder._search_coarse(_tomo_cs, smin, 
                                                             smax, ratio, drop)
            fine_cen = CenterOfRotationFinder._search_fine(_tomo_fs, srad, 
                                                           step, init_cen, 
                                                           ratio, drop)
        else:
            init_cen = CenterOfRotationFinder._search_coarse(_tomo_cs, 
                                                             smin, smax, 
                                                             ratio, drop)
            fine_cen = CenterOfRotationFinder._search_fine(_tomo_fs, srad, 
                                                           step, init_cen, 
                                                           ratio, drop)
    
        #logger.debug('Rotation center search finished: %i', fine_cen)
        return fine_cen


    @staticmethod
    def _search_coarse(sino, smin, smax, ratio, drop):
        """
        Coarse search for finding the rotation center.
        """
        (Nrow, Ncol) = sino.shape
        centerfliplr = (Ncol - 1.0) / 2.0
    
        # Copy the sinogram and flip left right, the purpose is to
        # make a full [0;2Pi] sinogram
        _copy_sino = numpy.fliplr(sino[1:])
    
        # This image is used for compensating the shift of sinogram 2
        temp_img = numpy.zeros((Nrow - 1, Ncol), dtype='float32')
        temp_img[:] = sino[-1]
    
        # Start coarse search in which the shift step is 1
        listshift = numpy.arange(smin, smax + 1)
        listmetric = numpy.zeros(len(listshift), dtype='float32')
        mask = CenterOfRotationFinder._create_mask(2 * Nrow - 1, Ncol, 
                                                   0.5 * ratio * Ncol, drop)
        for i in listshift:
            _sino = numpy.roll(_copy_sino, i, axis=1)
            if i >= 0:
                _sino[:, 0:i] = temp_img[:, 0:i]
            else:
                _sino[:, i:] = temp_img[:, i:]
            listmetric[i - smin] = numpy.sum(numpy.abs(numpy.fft.fftshift(
                #pyfftw.interfaces.numpy_fft.fft2(
                #    numpy.vstack((sino, _sino)))
                numpy.fft.fft2(numpy.vstack((sino, _sino)))
                )) * mask)
        minpos = numpy.argmin(listmetric)
        return centerfliplr + listshift[minpos] / 2.0
    
    @staticmethod
    def _search_fine(sino, srad, step, init_cen, ratio, drop):
        """
        Fine search for finding the rotation center.
        """
        Nrow, Ncol = sino.shape
        centerfliplr = (Ncol + 1.0) / 2.0 - 1.0
        # Use to shift the sinogram 2 to the raw CoR.
        shiftsino = numpy.int16(2 * (init_cen - centerfliplr))
        _copy_sino = numpy.roll(numpy.fliplr(sino[1:]), shiftsino, axis=1)
        if init_cen <= centerfliplr:
            lefttake = numpy.int16(numpy.ceil(srad + 1))
            righttake = numpy.int16(numpy.floor(2 * init_cen - srad - 1))
        else:
            lefttake = numpy.int16(numpy.ceil(
                init_cen - (Ncol - 1 - init_cen) + srad + 1))
            righttake = numpy.int16(numpy.floor(Ncol - 1 - srad - 1))
        Ncol1 = righttake - lefttake + 1
        mask = CenterOfRotationFinder._create_mask(2 * Nrow - 1, Ncol1, 
                                                   0.5 * ratio * Ncol, drop)
        numshift = numpy.int16((2 * srad) / step) + 1
        listshift = numpy.linspace(-srad, srad, num=numshift)
        listmetric = numpy.zeros(len(listshift), dtype='float32')
        factor1 = numpy.mean(sino[-1, lefttake:righttake])
        num1 = 0
        for i in listshift:
            _sino = ndimage.interpolation.shift(
                _copy_sino, (0, i), prefilter=False)
            factor2 = numpy.mean(_sino[0,lefttake:righttake])
            _sino = _sino * factor1 / factor2
            sinojoin = numpy.vstack((sino, _sino))
            listmetric[num1] = numpy.sum(numpy.abs(numpy.fft.fftshift(
                #pyfftw.interfaces.numpy_fft.fft2(
                #    sinojoin[:, lefttake:righttake + 1])
                numpy.fft.fft2(sinojoin[:, lefttake:righttake + 1])
                )) * mask)
            num1 = num1 + 1
        minpos = numpy.argmin(listmetric)
        return init_cen + listshift[minpos] / 2.0
    
    @staticmethod
    def _create_mask(nrow, ncol, radius, drop):
        du = 1.0 / ncol
        dv = (nrow - 1.0) / (nrow * 2.0 * numpy.pi)
        centerrow = numpy.ceil(nrow / 2) - 1
        centercol = numpy.ceil(ncol / 2) - 1
        # added by Edoardo Pasca
        centerrow = int(centerrow)
        centercol = int(centercol)
        mask = numpy.zeros((nrow, ncol), dtype='float32')
        for i in range(nrow):
            num1 = numpy.round(((i - centerrow) * dv / radius) / du)
            (p1, p2) = numpy.int16(numpy.clip(numpy.sort(
                (-num1 + centercol, num1 + centercol)), 0, ncol - 1))
            mask[i, p1:p2 + 1] = numpy.ones(p2 - p1 + 1, dtype='float32')
        if drop < centerrow:
            mask[centerrow - drop:centerrow + drop + 1,
                 :] = numpy.zeros((2 * drop + 1, ncol), dtype='float32')
        mask[:,centercol-1:centercol+2] = numpy.zeros((nrow, 3), dtype='float32')
        return mask
    
    def process(self):
        
        projections = self.getInput()
        
        cor = CenterOfRotationFinder.find_center_vo(projections.as_array())
        
        return cor

def loadNexus(filename):
    '''Load a dataset stored in a NeXuS file (HDF5)'''
    ###########################################################################
    ## Load a dataset
    nx = h5py.File(filename, "r")
    
    data = nx.get('entry1/tomo_entry/data/rotation_angle')
    angles = numpy.zeros(data.shape)
    data.read_direct(angles)
    
    data = nx.get('entry1/tomo_entry/data/data')
    stack = numpy.zeros(data.shape)
    data.read_direct(stack)
    data = nx.get('entry1/tomo_entry/instrument/detector/image_key')
    
    itype = numpy.zeros(data.shape)
    data.read_direct(itype)
    # 2 is dark field
    darks = [stack[i] for i in range(len(itype)) if itype[i] == 2 ]
    dark = darks[0]
    for i in range(1, len(darks)):
        dark += darks[i]
    dark = dark / len(darks)
    #dark[0][0] = dark[0][1]
    
    # 1 is flat field
    flats = [stack[i] for i in range(len(itype)) if itype[i] == 1 ]
    flat = flats[0]
    for i in range(1, len(flats)):
        flat += flats[i]
    flat = flat / len(flats)
    #flat[0][0] = dark[0][1]
    
    
    # 0 is projection data
    proj = [stack[i] for i in range(len(itype)) if itype[i] == 0 ]
    angle_proj = [angles[i] for i in range(len(itype)) if itype[i] == 0 ]
    angle_proj = numpy.asarray (angle_proj)
    angle_proj = angle_proj.astype(numpy.float32)
    
    return angle_proj , numpy.asarray(proj) , dark, flat
    
    
    
if __name__ == '__main__':
    angles, proj, dark, flat = loadNexus('../../../data/24737_fd.nxs')
    
    parallelbeam = geoms.SinogramGeometry('parallel', '3D' , 
                                 angles=angles, 
                                 pixel_num_h=numpy.shape(proj)[2],
                                 pixel_num_v=numpy.shape(proj)[1],
                                 )    
    sino = SinogramData( proj , geometry=parallelbeam)
    
    normalizer = Normalizer()
    normalizer.setInput(sino)
    normalizer.setFlatField(flat)
    normalizer.setDarkField(dark)
    norm = normalizer.getOutput()
    print ("Processor min {0} max {1}".format(norm.as_array().min(), norm.as_array().max()))
    
    norm1 = numpy.asarray(
            [Normalizer.normalizeProjection( p, flat, dark, 1e-5 ) 
            for p in proj]
            )
    
    print ("Numpy min {0} max {1}".format(norm1.min(), norm1.max()))
    
    cor_finder = CenterOfRotationFinder()
    cor_finder.setInput(sino)
    cor = cor_finder.getOutput()
    print ("center of rotation {0} == 86.25?".format(cor))
    
    conebeam = geoms.SinogramGeometry('cone', '3D' , 
                                 angles=angles, 
                                 pixel_num_h=numpy.shape(proj)[2],
                                 pixel_num_v=numpy.shape(proj)[1],
                                 )    
    sino = SinogramData( proj , geometry=conebeam)
    try:
        cor_finder.setInput(sino)
        cor = cor_finder.getOutput()
    except ValueError as err:
        print (err)