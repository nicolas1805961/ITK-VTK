import vtk
import itk
import os

filepath = "C:\\python test\\PythonApplication1\\Data"
input_file = 'BRATS_HG0015_T1C.mha'
itk_output_filename = 'out_itk.mha'

PixelType = itk.ctype('unsigned short')
input_image = itk.imread(os.path.join(filepath, input_file))
dimension = input_image.GetImageDimension()

InputImageType = itk.Image[itk.SS, dimension]
OutputImageType = itk.Image[itk.D, dimension]

castImageFilter = itk.CastImageFilter[InputImageType, OutputImageType].New()
castImageFilter.SetInput(input_image)
castImageFilter.Update()

filter = itk.CurvatureFlowImageFilter.New(Input=castImageFilter.GetOutput(), NumberOfIterations=30, TimeStep=0.2)
#filter = itk.GradientAnisotropicDiffusionImageFilter.New(Input=castImageFilter.GetOutput(), NumberOfIterations=30, TimeStep=0.06, ConductanceParameter=3)
filter.Update()

castImageFilter = itk.CastImageFilter[OutputImageType, InputImageType].New()
castImageFilter.SetInput(filter.GetOutput())
castImageFilter.Update()

filter2 = itk.ConnectedThresholdImageFilter.New(castImageFilter.GetOutput())
filter2.SetReplaceValue(255)
filter2.SetLower(900)
filter2.SetUpper(1600)

index = itk.Index[dimension]()
index[0] = 83
index[1] = 80
index[2] = 109

filter2.SetSeed(index)
filter2.Update()

in_type = itk.output(filter2)
output_type = itk.Image[PixelType, dimension]
rescaler = itk.RescaleIntensityImageFilter[in_type, output_type].New(filter2)
rescaler.SetOutputMinimum(0)
rescaler.SetOutputMaximum(255)
rescaler.Update()

itk.imwrite(filter2, os.path.join(filepath, itk_output_filename))

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

reader = vtk.vtkMetaImageReader()
reader.SetFileName(os.path.join(filepath, itk_output_filename))

opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(0.0, 0.0)
opacityTransferFunction.AddPoint(255.0, 1)

colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(255.0, 1.0, 1.0, 1.0)

volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.ShadeOff()
volumeProperty.SetInterpolationTypeToLinear()

#castFilter = vtk.vtkImageCast()
#castFilter.SetInputConnection(reader.GetOutputPort())
#castFilter.SetOutputScalarTypeToUnsignedShort()
#castFilter.Update()
#
#imdataBrainSeg = castFilter.GetOutputPort()

volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
volumeMapper.SetBlendModeToComposite()
volumeMapper.SetInputConnection(reader.GetOutputPort())

volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

ren.AddVolume(volume)
ren.SetBackground(0, 0, 0)
renWin.SetSize(600, 600)
renWin.Render()

def CheckAbort(obj, event):
    if obj.GetEventPending() != 0:
        obj.SetAbortRender(1)

renWin.AddObserver("AbortCheckEvent", CheckAbort)

iren.Initialize()
renWin.Render()
iren.Start()