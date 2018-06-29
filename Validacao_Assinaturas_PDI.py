'''
Trabalho Final - Sistema de Validacao de Assinaturas
Caio Abreu de Oliveira Ribeiro 		- nUsp 10262839
Vinicius Torres Dutra Maia da Costa - nUsp 10262781
SCC0251 - Processamento de Imagens
Semestre 01 - 2018 - Professor Moacir Ponti
'''
import numpy as np
import imageio

# Funcao que ajusta a resolucao da imagem para o padrao de 800x400 pixels
def adjust_resolution(img):
	x,y = np.shape(img)
	#casos em que x ou y da imagem eh maior que o padrao, realiza um slice para o tamanho adequado
	if x > 800:
		img = img[0:800, :]
	if y > 400:
		img = img[:, 0:400]

	#Cria-se uma matriz com essas dimensoes e soma-se com matriz menor que
	#representa a imagem, gerando uma nova matriz com 800x400
	img2 = np.zeros((800,400), dtype=np.float32)
	img2[:x, :y] += img

	return img2


#	Funcao para transformar imagem RGB em GRAYSCALE
def RGBtoGrayscale(RGB):

	# divide a imagem nos 3 canais de cores
	R = RGB[:,:,0].astype(np.float32)
	G = RGB[:,:,1].astype(np.float32)
	B = RGB[:,:,2].astype(np.float32)

	# formula para realizar a conversao
	gray = 0.2989 * R + 0.5870 * G + 0.1140 * B
	# retorna a matriz normalizada
	return ((gray/np.max(gray)) * 255).astype(np.uint8);

#Funcao para transformar imagem RGB em uma imagem binaria,
#levando em consideracao os 75% pixels de maior magnitude.
def RGBtoBinary(InputImg):
	# Converte a imagem para gray scale
	GrayImg = RGBtoGrayscale(InputImg)
	# retorna a imagem binaria
	BinImg = np.less(GrayImg, 0.75 * np.max(GrayImg)) * 1
	return BinImg.astype(np.uint8)

#	Funcao que calcula numero de transicoes (0 para 1 ou 1 para 0) entre os pixels vizinhos de um pixel central
def pixel_transitions(neib):
	# cria um array que contem os vizinhos do pixel central em ordem circular horaria
	arr = np.append(np.append(neib[0,:], neib[1,2]), np.append(neib[2,::-1], neib[1,0]))
	sumTrans = 0
	# percorre o array somando em um contador de numero de transicoes
	for i in np.arange(8):
		if(i < 7 and arr[i] != arr[i+1]):
			sumTrans += 1

	if(arr[7] != arr[0]):
		sumTrans += 1

	# retorna metade do numero de transicoes
	return np.ceil(sumTrans/2)

#	Funcao que realiza a esqueletizacao utilizando a tecnica de
#thinning, a partir do processo morfologico de erosao.
def thinning(Img):

	imgPad = np.pad(Img, (1, 1), mode='constant') #zero padding
	x, y = np.shape(Img)
	flag = True

	# realiza o algoritmo enquanto ainda houverem pixels a serem removidos, o que
	# eh indicado pela 'flag'
	while(flag):
		flag = False
		# mascara de booleanos em que os pixels identificados com 'false' serao
		#retirados no fim da iteracao
		mask = np.ones((x + 2, y + 2), dtype=bool)

		for i in np.arange(1, x):
			for j in np.arange(1, y):
				if(imgPad[i, j] == 1):
					neib = imgPad[i-1:i+2, j-1:j+2]
					sumNeib = np.sum(neib) - 1
					# caso nao entre no 'if', nao existem mais pixels a serem processados
					if((sumNeib > 1 and sumNeib < 7) and pixel_transitions(neib)== 1):
						mask[i, j] = False
						flag = True
		imgPad = np.multiply(mask, imgPad)

	# retorna a imagem (com o pad) gerada pelo algoritmo
	return imgPad

# Funcao que extrai caracteristicas de orientacao local, isto eh, em uma janela
# de dimensoes menores que a imagem. Nesse caso, todas as janelas serao de 25x10.
# Para isso, calcula-se a quantidade de pixels em cada uma das 4 direcoes:
# horizontal - x, vertical - y, diagonal - d, diagonal invertida - di
def extract_orientation_local(img):
	x,y = np.shape(img)
	# cria uma lista para cada direcao
	Dx = []
	Dy = []
	Dd = []
	Di = []
	npixels = 0
	# Para cada pixel, Verifica se eh um pixel com valor 1 e em qual direcao
	# ele esta, em relacao ao anterior e adiciona na lista da orientacao
	for i in np.arange(x):
		for j in np.arange(y):
			if img[i, j] == 1:
				npixels += 1
				if i > 0 and img[i - 1, j] == 1: # direcao horizontal
					Dx.append(1)
				else:
					Dx.append(0)

				if j > 0 and img[i, j - 1] == 1: # direcao vertical
					Dy.append(1)
				else:
					Dy.append(0)

				if i > 0 and j < y-1 and img[i - 1, j + 1] == 1: # direcao diagonal
					Dd.append(1)
				else:
					Dd.append(0)

				if i > 0 and j > 0 and img[i - 1, j - 1] == 1: # direcao diagonal invertida
					Di.append(1)
				else:
					Di.append(0)

	# caso o numero de pixels 1 na janela seja maior que zero, calcula-se o desvio padrao
	# para cada orientacao
	if npixels > 0:
		stdX = np.std(Dx)
		stdY = np.std(Dy)
		stdD = np.std(Dd)
		stdI = np.std(Di)

	else:
		stdX = 0
		stdY = 0
		stdD = 0
		stdI = 0

	# realiza o tratamento estatistica, normalizando os valores de cada orientacao
	# utilizando a distribuicao normal
	if stdX == 0:
		zx = 0
	else:
		zx = (npixels - np.mean(Dx))/stdX

	if stdY == 0:
		zy = 0
	else:
		zy = (npixels - np.mean(Dy))/stdY

	if stdD == 0:
		zd = 0
	else:
		zd = (npixels - np.mean(Dd))/stdD

	if stdI == 0:
		zi = 0
	else:
		zi = (npixels - np.mean(Di))/stdI

	# retorna uma lista com o valor calculado em cada direcao
	return [zx, zy, zd, zi]

# Funcao que extrai as caracteristicas de orientacoes da imagem, por meio do modulo
# dos vetores em cada direcao para cada janela, isto eh, vizinhanca local
def extract_orientation(img):
	x,y = img.shape

	# cria vetores para cada uma das 4 orientacoes,
	# com o numero de posicoes igual ao numero de janelas
	Zx = np.zeros(1280, dtype=np.float32)
	Zy = np.zeros(1280, dtype=np.float32)
	Zd = np.zeros(1280, dtype=np.float32)
	Zi = np.zeros(1280, dtype=np.float32)

	# Percorre as janelas, armazenando a caracteristica de orientacao de cada retina
	k = 0
	for i in range(0, x, 25):
		for j in range(0, y, 10):
			local = img[i:i+25, j:j+10]
			r = extract_orientation_local(local)
			Zx[k] = r[0]
			Zy[k] = r[1]
			Zd[k] = r[2]
			Zi[k] = r[3]
			k += 1

	# Calcula o modulo do vetor orientacao
	modZx = np.sqrt(np.sum(np.power(Zx,2)))
	modZy = np.sqrt(np.sum(np.power(Zy,2)))
	modZd = np.sqrt(np.sum(np.power(Zd,2)))
	modZi = np.sqrt(np.sum(np.power(Zi,2)))

	# retorna o vetor Z que representa a estatistica dos vetores de orientacao em todas as janelas
	Z = [modZx, modZy, modZd, modZi]
	return Z

# 	Funcao que calcula a media e o desvio padrao dos dados obtidos de todas as retinas de
# todas as imagens, organizando-as em um vetor que sera retornado para que os dados
# sejam salvos em disco.
def statistical_analysis(Zxi, Zyi, Zdi, Zii):
	#calculo da media para cada um das orientacoes
	meanZx = np.mean(Zxi)
	meanZy = np.mean(Zyi)
	meanZd = np.mean(Zdi)
	meanZi = np.mean(Zii)

	#calculo do desvio padrao para cada uma das orientacoes
	stdZx = np.std(Zxi)
	stdZy = np.std(Zyi)
	stdZd = np.std(Zdi)
	stdZi = np.std(Zii)

	Prob = [meanZx, stdZx, meanZy, stdZy, meanZd, stdZd, meanZi, stdZi]
	return Prob

#	Funcao que realiza a comparacao do vetor Z resultante da extracao de caracteristicas
# da imagem de entrada com os dados armazenados no vetor "escritores.npy". Verifica se
# a variacao entre esses valores eh menor do que 95% do intervalo do desvio padrao em cada uma das orientacoes. Caso
# seja em 4 ou 3 orientacoes, a assinatura e valida. Com apenas 2, considera-se resultado
# inconclusivo (assinatura Indefinida), e menor do que 2 e considerado invalida.
def compare(Z, p):
	flag = 0
	if Z[0] <= p[0] + p[1]*0.95 and Z[0] >= p[0] - p[1]*0.95:
		flag += 1
	if Z[1] <= p[2] + p[3]*0.95 and Z[1] >= p[2] - p[3]*0.95:
		flag += 1
	if Z[2] <= p[4] + p[5]*0.95 and Z[2] >= p[4] - p[5]*0.95:
		flag += 1
	if Z[3] <= p[6] + p[7]*0.95 and Z[3] >= p[6] - p[7]*0.95:
		flag += 1

	if flag > 2:
		print("Assinatura Valida.")
	elif flag < 2:
		print("Assinatura Invalida.")
	else:
		print("Assinatura Indefinida.")

#MAIN
# nome do arquivo, caso seja um caso teste. Nome inicial dos arquivos caso seja caso de treinamento
InputImgName = str(input()).strip("\n\r")
i = int(input())				  # numero de imagens para treinamento ou 0 para teste
name = str(input()).strip("\n\r") # nome do escritor

Zxi = []
Zyi = []
Zdi = []
Zii = []

#caso de treinamento
if i > 0:
	for k in range(i):
		imgName = InputImgName + " (" + str(k) +")" + ".jpeg"
		#pre processamento
		InputImg = imageio.imread(imgName)
		BinImage = RGBtoBinary(InputImg)
		ThinImage = thinning(BinImage)
		ThinImage = adjust_resolution(ThinImage)

		#extracao de caracteristicas
		Z = extract_orientation(ThinImage)
		Zxi.append(Z[0])
		Zyi.append(Z[1])
		Zdi.append(Z[2])
		Zii.append(Z[3])

	#analise estatistica do resultado
	newProb = statistical_analysis(Zxi, Zyi, Zdi, Zii)

	# Escrita em um arquivo
	P = np.load("escritores.npy")
	nameList = np.load("nomeEscritores.npy")

	P = np.append(P, newProb)
	nameList = np.append(nameList, name)

	np.save("escritores.npy", P)
	np.save("nomeEscritores", nameList)

#caso de teste
else:
	# Realiza o pre processamento
	InputImg = imageio.imread(InputImgName)
	BinImage = RGBtoBinary(InputImg)
	ThinImage = thinning(BinImage)
	ThinImage = adjust_resolution(ThinImage)
	Z = extract_orientation(ThinImage)

	# Carrega as caracteristicas do escritor
	p = np.load("escritores.npy")
	nameList = np.load("nomeEscritores.npy")

	tam = np.shape(nameList)[0] - 1
	while(tam > 0 and nameList[tam] != name):
		tam -= 1
	# Se o escritor estava no arquivo, realiza a comparacao
	if(nameList[tam] == name):
		compare(Z, p[tam*8:tam*8+8])
	else:
		print("Escritor nao presente no conjunto de dados.")
