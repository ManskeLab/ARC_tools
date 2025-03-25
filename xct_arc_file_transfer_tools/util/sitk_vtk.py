"""
sitk_vtk.py

Created by:   Michael Kuczynski
Created on:   21-01-2020

Description: Converts between SimpleITK and VTK image types
"""

import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk, get_vtk_array_type

import SimpleITK as sitk


def sitk_to_vtk(sitk_image):
    """
    Convert a SimpleITK image to a VTK image.

    Parameters
    ----------
    sitk_image : SimpleITK.Image

    Returns
    -------
    vtk_image : VTK.Image
    """
    origin = list(sitk_image.GetOrigin())
    spacing = list(sitk_image.GetSpacing())

    # Cconvert the SimpleITK image to a numpy array
    raw_data = sitk.GetArrayFromImage(sitk_image)

    data_type = get_vtk_array_type(raw_data.dtype)
    shape = raw_data.shape

    flat_data_array = raw_data.flatten()
    vtk_data = numpy_to_vtk(num_array=flat_data_array, deep=True, array_type=data_type)
    
    vtk_image = vtk.vtkImageData()
    vtk_image.GetPointData().SetScalars(vtk_data)
    vtk_image.SetDimensions(shape[0], shape[1], shape[2])
    vtk_image.SetSpacing(spacing)
    vtk_image.SetOrigin(origin)
    
    return vtk_image

def vtk_to_sitk(vtk_image):
    """
    Convert a VTK image to a SimpleITK image.

    Parameters
    ----------
    vtk_image : VTK.Image

    Returns
    -------
    sitk_image : SimpleITK.Image
    """
    vtk_data = vtk_image.GetPointData().GetScalars()
    numpy_data = vtk_to_numpy(vtk_data)
    dims = vtk_image.GetDimensions()
    numpy_data = numpy_data.reshape(dims[2], dims[1], dims[0])
    numpy_data = numpy_data.transpose(2, 1, 0)

    sitk_image = sitk.GetImageFromArray(numpy_data)

    return sitk_image
