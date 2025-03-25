import SimpleITK as sitk

# Dictionary for interpolator types
interpolatorDict = {
    "nearestneighbor": sitk.sitkNearestNeighbor,
    "linear": sitk.sitkLinear,
    "spline": sitk.sitkBSpline,
    "gaussian": sitk.sitkGaussian,
}

sitkInterpolatorDictEnum = {
    1: "nearestneighbor",
    2: "linear",
    3: "spline",
    4: "gaussian",
}
