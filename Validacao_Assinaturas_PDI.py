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
#levando em consideracao os 75% pixels de maior magnitude.
def RGBtoBinary(InputImg):

	GrayImg = RGBtoGrayscale(InputImg)
	BinImg = np.less(GrayImg, 0.75 * np.max(GrayImg)) * 1
	return BinImg.astype(np.uint8)

#Funcao que calcula numero de transicoes (0 para 1 ou 1 para 0) entre os pixels vizinhos de um pixel central
def pixel_transitions(neib):
	#cria um array que contem os vizinhos do pixel central em ordem circular horaria
	arr = np.append(np.append(neib[0,:], neib[1,2]), np.append(neib[2,::-1], neib[1,0]))
	sumTrans = 0

	for i in np.arange(8):
		if(i < 7 and arr[i] != arr[i+1]):
			sumTrans += 1

	if(arr[7] != arr[0]):
		sumTrans += 1

	return np.ceil(sumTrans/2)

#Funcao que realiza a esqueletizacao a partir da tecnica de
#thinning
def thinning(Img):
	imgPad = np.pad(Img, (1, 1), mode='constant') #zero padding
	x, y = np.shape(Img)
	flag = True

	#realiza o algoritmo enquanto ainda houverem pixels a serem removidos
	while(flag):	
		flag = False
		mask = np.ones((x + 2, y + 2), dtype=bool)

		for i in np.arange(1, x):
			for j in np.arange(1, y):
				if(imgPad[i, j] == 1):
					neib = imgPad[i-1:i+2, j-1:j+2]
					sumNeib = np.sum(neib) - 1

					if((sumNeib > 1 and sumNeib < 7) and pixel_transitions(neib)== 1):
						mask[i, j] = False
						flag = True
		imgPad = np.multiply(mask, imgPad)

	Img = imgPad[1:x, 1:y]
	return Img

InputImgName = str(input()).strip("\n\r")
InputImg = imageio.imread(InputImgName)

BinImage = RGBtoBinary(InputImg)

BinImage = thinning(BinImage)

BinImage = (np.equal(BinImage, 1) * 255).astype(np.uint8)
imageio.imwrite("Bin.png", BinImage)
