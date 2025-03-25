# -----------------------------------------------------
# fileConverter.py
#
# Created by:   Michael Kuczynski
# Created on:   21-01-2020
#
# Description: Converts between 3D image file formats.
#              Currently supported conversions:
#                   1.  DICOM to NIfTI
#                   2.  DICOM to MHA
#                   3.  DICOM to NRRD
#                   4.  DICOM to TIFF
#                   5.  NIfTI to MHA
#                   6.  NIfTI to NRRD
#                   7.  NIfTI to DICOM
#                   8.  NIfTI to TIFF
#                   9.  MHA to NIfTI
#                   10. MHA to NRRD
#                   11. MHA to DICOM
#                   12. MHA to TIFF
#                   13. AIM to NIfTI
#                   14. AIM to MHA
#                   15. AIM to DICOM
#                   16. AIM to NRRD
#                   17. AIM to TIFF
#                   18. NRRD to NIfTI
#                   19. NRRD to MHA
#                   20. NRRD to DICOM
#                   21. NRRD to TIFF
#
# Notes:
# 1. File format conversion can be done using several different software libraries/packages.
#    However, when reading in images, VTK does not store the image orientation, direction, or origin.
#    This causes problems when trying to overlay images after conversion. ITK based libraries/packages
#    (like SimpleITK) are able to maintain the original image orientation, direction, and origin.
#    Reading AIM images is only supported in ITK.
#
# 2. Some useful links that explain image orientation, direction, and origin:
#    -https://www.slicer.org/wiki/Coordinate_systems
#    -https://discourse.vtk.org/t/proposal-to-add-orientation-to-vtkimagedata-feedback-wanted/120
#    -http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.DirectionMatrices
#    -https://fromosia.wordpress.com/2017/03/10/image-orientation-vtk-itk/
#
# 3. Be careful when converting to a DICOM series! This script can currently do this conversion, however,
#    not all of the header information is copied over!
# 4. Be careful when converting from TIFF! Writing to TIFF currently works, but slice thickness is lost
#    when writing TIFF images. Thus, when you try to convert back (or use a TIFF image from somewhere else),
#    the image may look stretched as the slice thickness will be assumed to be 1.0
# -----------------------------------------------------
# USAGE:
# 1. conda activate manskelab
# 2. python fileConverter.py <inputImage.ext> <outputImage.ext>
#
# -----------------------------------------------------

import os
import sys
import glob
import argparse

from util.sitk_itk import sitk_itk, itk_sitk
from util.img2dicom import img2dicom

import itk

import SimpleITK as sitk


def fileConverter(inputImage, outputImage):
    print("******************************************************")
    print(f"CONVERTING: {inputImage} to {outputImage}")

    # Extract directory, filename, basename, and extensions from the output
    # image
    outDirectory, outFilename = os.path.split(outputImage)
    outBasename, outExtension = os.path.splitext(outFilename)

    outFilename = os.path.basename(outFilename)
    ext_idx = outFilename.find('.')

    outBasename = outFilename[:ext_idx]
    outExtension = outFilename[ext_idx:]

    # Check the output file format
    if outExtension.lower() == ".mha":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".mha")
    elif outExtension.lower() == ".mhd" or outExtension.lower() == ".raw":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".mhd")
        outputImageFileNameRAW = os.path.join(outDirectory, outBasename + ".raw")
    elif outExtension.lower() == ".nii":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".nii")
    elif outExtension.lower() == ".nii.gz":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".nii.gz")
    elif outExtension.lower() == ".nrrd":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".nrrd")
    elif outExtension.lower() == ".dcm":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".dcm")
    elif outExtension.lower() == ".tif":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".tif")
    elif outExtension.lower() == ".isq":
        outputImageFileName = os.path.join(outDirectory, outBasename + ".ISQ")
    else:
        print()
        print("Error: output file extension must be MHD, MHA, RAW, NRRD, TIFF or NII.")
        sys.exit(1)

    # Check if the input is a DICOM series directory
    if os.path.isdir(inputImage):
        # Check if the directory exists
        if not os.path.exists(inputImage):
            print()
            print("Error: DICOM directory does not exist!")
            sys.exit(1)
        elif len(glob.glob(os.path.join(inputImage, "*.tif"))) > 0:
            # TIF series
            reader = sitk.ImageSeriesReader()
            reader.SetFileNames(glob.glob(os.path.join(inputImage, "*.tif")))
            reader.SetOutputPixelType(sitk.sitkInt16)
            outputImage = reader.Execute()
        elif len(glob.glob(os.path.join(inputImage, "*.tiff"))) > 0:
            # TIF series
            reader = sitk.ImageSeriesReader()
            reader.SetFileNames(glob.glob(os.path.join(inputImage, "*.tiff")))
            reader.SetOutputPixelType(sitk.sitkInt16)
            outputImage = reader.Execute()
        else:
            # DICOM series
            reader = sitk.ImageSeriesReader()

            # Convert to 16-bit Int to ensure compatibility with ITK-Python functions
            # Needed for writing TIFF images
            if outExtension.lower() == ".tif":
                reader.SetOutputPixelType(sitk.sitkInt16)

            dicom_names = reader.GetGDCMSeriesFileNames(inputImage)
            reader.SetFileNames(dicom_names)
            reader.SetOutputPixelType(sitk.sitkFloat32)

            outputImage = reader.Execute()
    else:
        # Extract directory, filename, basename, and extensions from the input
        # image
        inDirectory, inFilename = os.path.split(inputImage)
        inBasename, inExtension = os.path.splitext(inFilename)

        inFilename = os.path.basename(inFilename)
        ext_idx = inFilename.find('.')

        inBasename = inFilename[:ext_idx]
        inExtension = inFilename[ext_idx:]

        # AIM image file
        if ".aim" in inExtension.lower():
            # If the input AIM contains a version number, remove it and rename
            # the file
            if ";" in inExtension.lower():
                inputImageNew = inputImage.rsplit(";", 1)[0]
                os.rename(inputImage, inputImageNew)
                inputImage = inputImageNew

            # Read in the AIM using ITK
            # Only support short images for now
            ImageType = itk.Image[itk.ctype("signed short"), 3]
            reader = itk.ImageFileReader[ImageType].New()
            imageio = itk.ScancoImageIO.New()
            reader.SetImageIO(imageio)
            reader.SetFileName(inputImage)
            reader.Update()

            outputImage = itk_sitk(reader.GetOutput())

        # ISQ image file
        elif ".isq" in inExtension.lower():
            # If the input ISQ contains a version number, remove it and rename
            # the file
            if ";" in inExtension.lower():
                inputImageNew = inputImage.rsplit(";", 1)[0]
                os.rename(inputImage, inputImageNew)
                inputImage = inputImageNew

            # Read in the ISQ using ITK
            ImageType = itk.Image[itk.ctype("signed short"), 3]
            reader = itk.ImageFileReader[ImageType].New()
            imageio = itk.ScancoImageIO.New()
            reader.SetImageIO(imageio)
            reader.SetFileName(inputImage)
            reader.Update()

            outputImage = itk_sitk(reader.GetOutput())

        # Other image file (e.g., MHA, NII, NRRD)
        elif os.path.isfile(inputImage) and (
            ".nii" or ".nii.gz" or ".mha" or ".mhd" or ".raw" or ".nrrd" in inExtension.lower()
        ):
            # Convert to 16-bit Int to ensure compatibility with ITK-Python
            # functions for writing TIFFs
            if outExtension.lower() == ".tif":
                outputImage = sitk.ReadImage(inputImage, sitk.sitkInt16)
            else:
                # Use unkown pixel type (may cause errors if the pixel type is
                # not supported by ITK-Python)
                outputImage = sitk.ReadImage(inputImage, sitk.sitkInt16)

        else:
            print()
            print("Error: Input image is an incorrect type!")
            sys.exit(1)

    # Setup the correct writer based on the output image extension
    if outExtension.lower() == ".mha":
        print("WRITING IMAGE: " + str(outputImageFileName))
        sitk.WriteImage(outputImage, str(outputImageFileName))

    elif outExtension.lower() == ".mhd" or outExtension.lower() == ".raw":
        print("WRITING IMAGE: " + str(outputImageFileName))
        sitk.WriteImage(outputImage, str(outputImageFileName))

    elif outExtension.lower() == ".nii" or outExtension.lower() == ".nii.gz":
        print("WRITING IMAGE: " + str(outputImageFileName))
        sitk.WriteImage(outputImage, str(outputImageFileName))

    elif outExtension.lower() == ".nrrd":
        print("WRITING IMAGE: " + str(outputImageFileName))
        sitk.WriteImage(outputImage, str(outputImageFileName))

    elif outExtension.lower() == ".tif":
        # SimpleITK TIFFImageIO is a bit buggy (sometimes writes out binary images...)
        # Use ITK instead. Need to force the use of a supported ITK-Python
        # pixel type. Signed short is used as default
        imageType = itk.Image[itk.SS, 3]

        # Need to convert to ITK image
        # Should be read in as signed short by default so we shouldn't need to
        # cast
        image = sitk_itk(outputImage)

        # Image values need to rescaled
        rescaler = itk.RescaleIntensityImageFilter[imageType, imageType].New()
        rescaler.SetInput(image)
        rescaler.SetOutputMinimum(0)
        pixelTypeMaximum = itk.NumericTraits[itk.SS].max()
        rescaler.SetOutputMaximum(pixelTypeMaximum)

        print("WRITING IMAGE: " + str(outputImageFileName))
        writer = itk.ImageFileWriter[imageType].New()
        writer.SetFileName(str(outputImageFileName))
        writer.SetInput(rescaler.GetOutput())
        writer.Update()

    elif outExtension.lower() == ".dcm":
        print("WRITING IMAGE: " + str(outputImageFileName))
        img2dicom(outputImage, outDirectory)

    elif outExtension.lower() == ".isq":
        outputImageISQ = sitk_itk(outputImage)
        print("WRITING IMAGE: " + str(outputImageFileName))

        ImageType = itk.Image[itk.ctype("signed short"), 3]
        writer = itk.ImageFileWriter[ImageType].New()
        imageio = itk.ScancoImageIO.New()
        writer.SetImageIO(imageio)
        writer.SetInput(outputImageISQ)
        writer.SetFileName(outputImageFileName)
        writer.Update()

        # Set header information
        imageio.SetEnergy(68)
        imageio.SetIntensity(1.47)
        imageio.SetReconstructionAlg(3)
        imageio.SetSite(4)
        imageio.SetScannerID(3401)
        imageio.SetPatientIndex(2567)
        imageio.SetMeasurementIndex(12778)
        imageio.SetSampleTime(100)
        imageio.SetScannerType(9)
        imageio.SetMuScaling(8192)
        imageio.SetNumberOfProjections(900)
        imageio.SetSliceIncrement(0.0609)
        imageio.SetSliceThickness(0.0609)
        # imageio.SetScanDistance(139852)
        # imageio.SetReferenceLine(109737)
        # imageio.SetNumberOfSamples(2304)
        # imageio.SetStartPosition()

        writer.Write()

    print("DONE")
    print("******************************************************")
    print()


if __name__ == "__main__":
    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "inputImage", type=str, help="The input image (path + filename)"
    )
    parser.add_argument(
        "outputImage", type=str, help="The output image (path + filename)"
    )
    args = parser.parse_args()

    inputImage = args.inputImage
    outputImage = args.outputImage

    fileConverter(inputImage, outputImage)
