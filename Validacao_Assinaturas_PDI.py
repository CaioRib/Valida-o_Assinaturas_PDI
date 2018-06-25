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

	return imgPad

def extract_orientation(img):

	x,y = np.shape(img)
	Ix = np.zeros((x, y), dtype=np.uint8)
	Iy = np.zeros((x, y), dtype=np.uint8)
	Id = np.zeros((x, y), dtype=np.uint8)
	Idi = np.zeros((x, y), dtype=np.uint8)
	npixels = 0
	for i in np.arange(1, x-1):
		for j in np.arange(1, y-1):
			if img[i, j] == 1:
				npixels += 1
				if img[i - 1, j] == 1:
					Ix[i, j] = 1
				if img[i, j - 1] == 1:
					Iy[i, j] = 1
				if img[i - 1, j + 1] == 1:
					Id[i, j] = 1
				if img[i - 1, j - 1] == 1:
					Idi[i, j] = 1

	res = np.zeros(4, dtype=np.float32)
	res[0] = np.sum(Ix)/npixels
	res[1] = np.sum(Iy)/npixels
	res[2] = np.sum(Id)/npixels
	res[3] = np.sum(Idi)/npixels

	return res

def statistical_analysis(orientation, j):
	x = np.zeros(j, dtype=np.float32)
	y = np.zeros(j, dtype=np.float32)
	d = np.zeros(j, dtype=np.float32)
	di = np.zeros(j, dtype=np.float32)

	z = np.zeros(8, dtype=np.float32)

	for i in range(j):
		x[i]  = orientation[i][0]
		y[i]  = orientation[i][1]
		d[i]  = orientation[i][2]
		di[i] = orientation[i][3]

	z[0] = np.mean(x)
	z[1] = np.mean(y)
	z[2] = np.mean(d)
	z[3] = np.mean(di)

	z[4] = np.std(x)
	z[5] = np.std(y)
	z[6] = np.std(d)
	z[7] = np.std(di)

	return z

def compare(orientation, z):
	flag = 0
	if orientation[0] <= z[0] + z[4]/2 and orientation[0] >= z[0] - z[4]/2:
		flag += 1
	if orientation[1] <= z[1] + z[5]/2 and orientation[1] >= z[1] - z[5]/2:
		flag += 1
	if orientation[2] <= z[2] + z[6] and orientation[2] >= z[2] - z[6]:
		flag += 1
	if orientation[3] <= z[3] + z[7] and orientation[3] >= z[3] - z[7]:
		flag += 1

	if flag > 2:
		print("Assinatura Valida.")
	elif flag < 2:
		print("Assinatura Invalida.")
	else:
		print("Assinatura Indefinida.")


#MAIN
InputImgName = str(input()).strip("\n\r")
i = int(input())
name = str(input()).strip("\n\r")

if i > 0:
	orientation = []
	for k in range(i):
		imgName = InputImgName + " (" + str(k) +")" + ".jpeg"
		InputImg = imageio.imread(imgName)
		BinImage = RGBtoBinary(InputImg)
		ThinImage = thinning(BinImage)
		orientation.append(extract_orientation(ThinImage))
	newZ = statistical_analysis(orientation, i)

	z = np.load("escritores.npy")
	nameList = np.load("nomeEscritores.npy")

	z = np.append(z, newZ)
	nameList = np.append(nameList, name)

	np.save("escritores.npy", z)
	np.save("nomeEscritores", nameList)

else:
	InputImg = imageio.imread(InputImgName)
	BinImage = RGBtoBinary(InputImg)
	ThinImage = thinning(BinImage)
	orientation = extract_orientation(ThinImage)

	z = np.load("escritores.npy")
	nameList = np.load("nomeEscritores.npy")

	tam = np.shape(nameList)[0] - 1
	while(tam > 0 and nameList[tam] != name):
		tam -= 1

	if(nameList[tam] == name):
		compare(orientation, z[tam*8:tam*8+8])

	else:
		print("Escritor nao presente no conjunto de dados.")
	# 
	# print(z[tam*8:tam*8+8])
	# print(orientation)
