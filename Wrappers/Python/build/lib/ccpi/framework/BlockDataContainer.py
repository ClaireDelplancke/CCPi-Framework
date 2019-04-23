    # -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 16:04:45 2019

@author: ofn77899
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy
from numbers import Number
import functools
from ccpi.framework import DataContainer
#from ccpi.framework import AcquisitionData, ImageData
#from ccpi.optimisation.operators import Operator, LinearOperator
 
class BlockDataContainer(object):
    '''Class to hold DataContainers as column vector
    
    Provides basic algebra between BlockDataContainer's, DataContainer's and
    subclasses and Numbers

    1) algebra between `BlockDataContainer`s will be element-wise, only if 
       the shape of the 2 `BlockDataContainer`s is the same, otherwise it 
       will fail 
    2) algebra between `BlockDataContainer`s and `list` or `numpy array` will 
       work as long as the number of `rows` and element of the arrays match,
       indipendently on the fact that the `BlockDataContainer` could be nested
    3) algebra between `BlockDataContainer` and one `DataContainer` is possible.
       It will require that all the `DataContainers` in the block to be
       compatible with the `DataContainer` we want to algebra with. Should we 
       require that the `DataContainer` is the same type? Like `ImageData` or `AcquisitionData`?
    4) algebra between `BlockDataContainer` and a `Number` is possible and it
       will be done with each element of the `BlockDataContainer` even if nested

    A = [ [B,C] , D] 
    A * 3 = [ 3 * [B,C] , 3* D] = [ [ 3*B, 3*C]  , 3*D ]
    
    '''
    ADD = 'add'
    SUBTRACT = 'subtract'
    MULTIPLY = 'multiply'
    DIVIDE = 'divide'
    POWER = 'power'
    __array_priority__ = 1
    __container_priority__ = 2
    def __init__(self, *args, **kwargs):
        ''''''
        self.containers = args
        self.index = 0
        shape = kwargs.get('shape', None)
        if shape is None:
           shape = (len(args),1)
#        shape = (len(args),1)
        self.shape = shape

        n_elements = functools.reduce(lambda x,y: x*y, shape, 1)
        if len(args) != n_elements:
            raise ValueError(
                    'Dimension and size do not match: expected {} got {}'
                    .format(n_elements, len(args)))

        
    def __iter__(self):
        '''BlockDataContainer is Iterable'''
        return self
    def next(self):
        '''python2 backwards compatibility'''
        return self.__next__()
    def __next__(self):
        try:
            out = self[self.index]
        except IndexError as ie:
            raise StopIteration()
        self.index+=1
        return out
    
    def is_compatible(self, other):
        '''basic check if the size of the 2 objects fit'''

        if isinstance(other, Number):
            return True   
        elif isinstance(other, (list, numpy.ndarray)) :
            for ot in other:
                if not isinstance(ot, (Number,\
                                 numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64,\
                                 numpy.float, numpy.float16, numpy.float32, numpy.float64, \
                                 numpy.complex)):
                    raise ValueError('List/ numpy array can only contain numbers {}'\
                                     .format(type(ot)))
            return len(self.containers) == len(other)
        elif issubclass(other.__class__, DataContainer):
            ret = True
            for i, el in enumerate(self.containers):
                if isinstance(el, BlockDataContainer):
                    a = el.is_compatible(other)
                else:
                    a = el.shape == other.shape
                ret = ret and a
            return ret
            #return self.get_item(0).shape == other.shape
        return len(self.containers) == len(other.containers)

    def get_item(self, row):
        if row > self.shape[0]:
            raise ValueError('Requested row {} > max {}'.format(row, self.shape[0]))
        return self.containers[row]

    def __getitem__(self, row):
        return self.get_item(row)
                
    def add(self, other, *args, **kwargs):
        '''Algebra: add method of BlockDataContainer with number/DataContainer or BlockDataContainer
        
        :param: other (number, DataContainer or subclasses or BlockDataContainer
        :param: out (optional): provides a placehold for the resul.
        '''
        out = kwargs.get('out', None)
        if out is not None:
            self.binary_operations(BlockDataContainer.ADD, other, *args, **kwargs)
        else:
            return self.binary_operations(BlockDataContainer.ADD, other, *args, **kwargs)
    def subtract(self, other, *args, **kwargs):
        '''Algebra: subtract method of BlockDataContainer with number/DataContainer or BlockDataContainer
        
        :param: other (number, DataContainer or subclasses or BlockDataContainer
        :param: out (optional): provides a placehold for the resul.
        '''
        out = kwargs.get('out', None)
        if out is not None:
            self.binary_operations(BlockDataContainer.SUBTRACT, other, *args, **kwargs)
        else:
            return self.binary_operations(BlockDataContainer.SUBTRACT, other, *args, **kwargs)
    def multiply(self, other, *args, **kwargs):
        '''Algebra: multiply method of BlockDataContainer with number/DataContainer or BlockDataContainer
        
        :param: other (number, DataContainer or subclasses or BlockDataContainer
        :param: out (optional): provides a placehold for the resul.
        '''
        out = kwargs.get('out', None)
        if out is not None:
            self.binary_operations(BlockDataContainer.MULTIPLY, other, *args, **kwargs)
        else:
            return self.binary_operations(BlockDataContainer.MULTIPLY, other, *args, **kwargs)
    def divide(self, other, *args, **kwargs):
        '''Algebra: divide method of BlockDataContainer with number/DataContainer or BlockDataContainer
        
        :param: other (number, DataContainer or subclasses or BlockDataContainer
        :param: out (optional): provides a placehold for the resul.
        '''
        out = kwargs.get('out', None)
        if out is not None:
            self.binary_operations(BlockDataContainer.DIVIDE, other, *args, **kwargs)
        else:
            return self.binary_operations(BlockDataContainer.DIVIDE, other, *args, **kwargs)
    

    def binary_operations(self, operation, other, *args, **kwargs):
        '''Algebra: generic method of algebric operation with BlockDataContainer with number/DataContainer or BlockDataContainer
        
        Provides commutativity with DataContainer and subclasses, i.e. this 
        class's reverse algebric methods take precedence w.r.t. direct algebric
        methods of DataContainer and subclasses.
        
        This method is not to be used directly
        '''
        if not self.is_compatible(other):
            raise ValueError('Incompatible for divide')
        out = kwargs.get('out', None)
        if isinstance(other, Number) or issubclass(other.__class__, DataContainer):
            # try to do algebra with one DataContainer. Will raise error if not compatible
            kw = kwargs.copy()
            res = []
            for i,el in enumerate(self.containers):
                if operation == BlockDataContainer.ADD:
                    op = el.add
                elif operation == BlockDataContainer.SUBTRACT:
                    op = el.subtract
                elif operation == BlockDataContainer.MULTIPLY:
                    op = el.multiply
                elif operation == BlockDataContainer.DIVIDE:
                    op = el.divide
                elif operation == BlockDataContainer.POWER:
                    op = el.power
                else:
                    raise ValueError('Unsupported operation', operation)
                if out is not None:
                    kw['out'] = out.get_item(i)
                    op(other, *args, **kw)
                else:
                    res.append(op(other, *args, **kw))
            if out is not None:
                return
            else:
                return type(self)(*res, shape=self.shape)
        elif isinstance(other, (list, numpy.ndarray, BlockDataContainer)):
            # try to do algebra with one DataContainer. Will raise error if not compatible
            kw = kwargs.copy()
            res = []
            if isinstance(other, BlockDataContainer):
                the_other = other.containers
            else:
                the_other = other
            for i,zel in enumerate(zip ( self.containers, the_other) ):
                el = zel[0]
                ot = zel[1]
                if operation == BlockDataContainer.ADD:
                    op = el.add
                elif operation == BlockDataContainer.SUBTRACT:
                    op = el.subtract
                elif operation == BlockDataContainer.MULTIPLY:
                    op = el.multiply
                elif operation == BlockDataContainer.DIVIDE:
                    op = el.divide
                elif operation == BlockDataContainer.POWER:
                    op = el.power
                else:
                    raise ValueError('Unsupported operation', operation)
                if out is not None:
                    kw['out'] = out.get_item(i)
                    op(ot, *args, **kw)
                else:
                    res.append(op(ot, *args, **kw))
            if out is not None:
                return
            else:
                return type(self)(*res, shape=self.shape)
            return type(self)(*[ operation(ot, *args, **kwargs) for el,ot in zip(self.containers,other)], shape=self.shape)
        else:
            raise ValueError('Incompatible type {}'.format(type(other)))
    

    def power(self, other, *args, **kwargs):
        if not self.is_compatible(other):
            raise ValueError('Incompatible for power')
        out = kwargs.get('out', None)
        if isinstance(other, Number):
            return type(self)(*[ el.power(other, *args, **kwargs) for el in self.containers], shape=self.shape)
        elif isinstance(other, list) or isinstance(other, numpy.ndarray):
            return type(self)(*[ el.power(ot, *args, **kwargs) for el,ot in zip(self.containers,other)], shape=self.shape)
        return type(self)(*[ el.power(ot, *args, **kwargs) for el,ot in zip(self.containers,other.containers)], shape=self.shape)
    
    def maximum(self,other, *args, **kwargs):
        if not self.is_compatible(other):
            raise ValueError('Incompatible for maximum')
        out = kwargs.get('out', None)
        if isinstance(other, Number):
            return type(self)(*[ el.maximum(other, *args, **kwargs) for el in self.containers], shape=self.shape)
        elif isinstance(other, list) or isinstance(other, numpy.ndarray):
            return type(self)(*[ el.maximum(ot, *args, **kwargs) for el,ot in zip(self.containers,other)], shape=self.shape)
        return type(self)(*[ el.maximum(ot, *args, **kwargs) for el,ot in zip(self.containers,other.containers)], shape=self.shape)
    
    ## unary operations    
    def abs(self, *args,  **kwargs):
        return type(self)(*[ el.abs(*args, **kwargs) for el in self.containers], shape=self.shape)
    def sign(self, *args,  **kwargs):
        return type(self)(*[ el.sign(*args, **kwargs) for el in self.containers], shape=self.shape)
    def sqrt(self, *args,  **kwargs):
        return type(self)(*[ el.sqrt(*args, **kwargs) for el in self.containers], shape=self.shape)
    def conjugate(self, out=None):
        return type(self)(*[el.conjugate() for el in self.containers], shape=self.shape)
    
    ## reductions
    
    def sum(self, *args, **kwargs):
        return numpy.sum([ el.sum(*args, **kwargs) for el in self.containers])
    
    def squared_norm(self):
        y = numpy.asarray([el.squared_norm() for el in self.containers])
        return y.sum() 
    
    def norm(self):
        return numpy.sqrt(self.squared_norm())   
    
    def pnorm(self, p=2):
                        
        if p==1:            
            return sum(self.abs())        
        elif p==2:                    
            return sum([el*el for el in self.containers]).sqrt()
        else:
            return ValueError('Not implemented')
                
    def copy(self):
        '''alias of clone'''    
        return self.clone()
    def clone(self):
        return type(self)(*[el.copy() for el in self.containers], shape=self.shape)
    def fill(self, other):
        if isinstance (other, BlockDataContainer):
            if not self.is_compatible(other):
                raise ValueError('Incompatible containers')
            for el,ot in zip(self.containers, other.containers):
                el.fill(ot)
        else:
            return ValueError('Cannot fill with object provided {}'.format(type(other)))
    
    def __add__(self, other):
        return self.add( other )
    # __radd__
    
    def __sub__(self, other):
        return self.subtract( other )
    # __rsub__
    
    def __mul__(self, other):
        return self.multiply(other)
    # __rmul__
    
    def __div__(self, other):
        return self.divide(other)
    # __rdiv__
    def __truediv__(self, other):
        return self.divide(other)
    
    def __pow__(self, other):
        return self.power(other)
    # reverse operand
    def __radd__(self, other):
        '''Reverse addition
        
        to make sure that this method is called rather than the __mul__ of a numpy array
        the class constant __array_priority__ must be set > 0
        https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.classes.html#numpy.class.__array_priority__
        '''
        return self + other
    # __radd__
    
    def __rsub__(self, other):
        '''Reverse subtraction
        
        to make sure that this method is called rather than the __mul__ of a numpy array
        the class constant __array_priority__ must be set > 0
        https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.classes.html#numpy.class.__array_priority__
        '''
        return (-1 * self) + other
    # __rsub__
    
    def __rmul__(self, other):
        '''Reverse multiplication
        
        to make sure that this method is called rather than the __mul__ of a numpy array
        the class constant __array_priority__ must be set > 0
        https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.classes.html#numpy.class.__array_priority__
        '''
        return self * other
    # __rmul__
    
    def __rdiv__(self, other):
        '''Reverse division
        
        to make sure that this method is called rather than the __mul__ of a numpy array
        the class constant __array_priority__ must be set > 0
        https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.classes.html#numpy.class.__array_priority__
        '''
        return pow(self / other, -1)
    # __rdiv__
    def __rtruediv__(self, other):
        '''Reverse truedivision
        
        to make sure that this method is called rather than the __mul__ of a numpy array
        the class constant __array_priority__ must be set > 0
        https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.classes.html#numpy.class.__array_priority__
        '''
        return self.__rdiv__(other)
    
    def __rpow__(self, other):
        '''Reverse power
        
        to make sure that this method is called rather than the __mul__ of a numpy array
        the class constant __array_priority__ must be set > 0
        https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.classes.html#numpy.class.__array_priority__
        '''
        return other.power(self)
    
    def __iadd__(self, other):
        '''Inline addition'''
        if isinstance (other, BlockDataContainer):
            for el,ot in zip(self.containers, other.containers):
                el += ot
        elif isinstance(other, Number):
            for el in self.containers:
                el += other
        elif isinstance(other, list) or isinstance(other, numpy.ndarray):
            if not self.is_compatible(other):
                raise ValueError('Incompatible for __iadd__')
            for el,ot in zip(self.containers, other):
                el += ot
        return self
    # __iadd__
    
    def __isub__(self, other):
        '''Inline subtraction'''
        if isinstance (other, BlockDataContainer):
            for el,ot in zip(self.containers, other.containers):
                el -= ot
        elif isinstance(other, Number):
            for el in self.containers:
                el -= other
        elif isinstance(other, list) or isinstance(other, numpy.ndarray):
            if not self.is_compatible(other):
                raise ValueError('Incompatible for __isub__')
            for el,ot in zip(self.containers, other):
                el -= ot
        return self
    # __isub__
    
    def __imul__(self, other):
        '''Inline multiplication'''
        if isinstance (other, BlockDataContainer):
            for el,ot in zip(self.containers, other.containers):
                el *= ot
        elif isinstance(other, Number):
            for el in self.containers:
                el *= other
        elif isinstance(other, list) or isinstance(other, numpy.ndarray):
            if not self.is_compatible(other):
                raise ValueError('Incompatible for __imul__')
            for el,ot in zip(self.containers, other):
                el *= ot
        return self
    # __imul__
    
    def __idiv__(self, other):
        '''Inline division'''
        if isinstance (other, BlockDataContainer):
            for el,ot in zip(self.containers, other.containers):
                el /= ot
        elif isinstance(other, Number):
            for el in self.containers:
                el /= other
        elif isinstance(other, list) or isinstance(other, numpy.ndarray):
            if not self.is_compatible(other):
                raise ValueError('Incompatible for __idiv__')
            for el,ot in zip(self.containers, other):
                el /= ot
        return self
    # __rdiv__
    def __itruediv__(self, other):
        '''Inline truedivision'''
        return self.__idiv__(other)
    
    

    
    
if __name__ == '__main__':
    
    from ccpi.framework import ImageGeometry, BlockGeometry
    import numpy

    N, M = 2, 3
    ig = ImageGeometry(N, M)    
    BG = BlockGeometry(ig, ig)
    
    U = BG.allocate('random_int')
    
    
    print ("test sum BDC " )
    w = U[0].as_array() + U[1].as_array()    
    w1 = sum(U).as_array()    
    numpy.testing.assert_array_equal(w, w1)
    
    print ("test sum BDC " )
    z = numpy.sqrt(U[0].as_array()**2 + U[1].as_array()**2)
    z1 = sum(U**2).sqrt().as_array()    
    numpy.testing.assert_array_equal(z, z1)   
    
    

    z2 = U.pnorm(2)
    
   



