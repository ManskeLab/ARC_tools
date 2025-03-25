import SimpleITK as sitk

# Dictionary for interpolator types
dataTypeDict = {
    "uint8": sitk.sitkUInt8,
    "uint16": sitk.sitkUInt16,
    "uint32": sitk.sitkUInt32,
    "uint64": sitk.sitkUInt64,
    "int8": sitk.sitkInt8,
    "int16": sitk.sitkInt16,
    "int32": sitk.sitkInt32,
    "int64": sitk.sitkInt64,
    "float32": sitk.sitkFloat32,
    "float64": sitk.sitkFloat64,
    "unknown": sitk.sitkUnknown,
}

sitkPixelIDEnum = {
    0: "uint8",
    2: "uint16",
    4: "uint32",
    6: "uint34",
    1: "int8",
    3: "int16",
    5: "int32",
    7: "int64",
    8: "float32",
    9: "float64",
    -1: "unknown",
}
