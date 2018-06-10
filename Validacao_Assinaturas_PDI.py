import numpy as np
import imageio

#Funcao para transformar imagem RGB em GRAYSCALE
def RGBtoGrayscale(RGB):
	R = RGB[:,:,0].astype(np.float32)
	G = RGB[:,:,1].astype(np.float32)
	B = RGB[:,:,2].astype(np.float32)

	gray = 0.2989 * R + 0.5870 * G + 0.1140 * B
	return ((gray/np.max(gray)) * 255).astype(np.uint8);

#Funcao para transformar imagem RGB em uma imagem binaria,
#levando em consideracao os 75% pixels mais significativos
def RGBtoBinary(OrImg):

	GrayImg = RGBtoGrayscale(OrImg)
	BinImg = np.less(GrayImg, 0.75 * np.max(GrayImg)) * 1
	return BinImg.astype(np.uint8)

#def thinning():




OrImgName = str(input()).strip("\n\r")
OrImg = imageio.imread(OrImgName)

BinImage = RGBtoBinary(OrImg)

print(BinImage)
imageio.imwrite("BinNC.png", BinImage)
BinImage = (np.equal(BinImage, 1) * 255).astype(np.uint8)
imageio.imwrite("Bin.png", BinImage)
