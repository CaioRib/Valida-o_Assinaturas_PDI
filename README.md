# Projeto Final: Sistema de Validacao de Assinaturas
ICMC/USP - Processamento de Imagens - SCC0251

Alunos:
- Vinicius Torres Dutra Maia da Costa	- nUSP 10262781
- Caio Abreu de Oliveira Ribeiro	- nUSP 10262839

Área/Tema do projeto: Aprendizado de Características.

# Descrição:
O problema de interesse é a validação de assinaturas manuscritas por meio de um sistema que irá identificar a validade da assinatura de um determinado usuário, a partir de um banco de dados composto por 20 exemplos de assinaturas de pelo menos 10 escritores diferentes, entre eles o próprio usuário em questão. Como entrada do programa, serão utilizadas imagens de assinaturas manuscritas com cor escura em um fundo claro, para facilitar a identificação dos padrões presentes na assinatura. Assim, o usuário após se cadastrar com 20 exemplos de sua assinatura, será capaz de fornecer para o sistema um novo exemplar e testar a validade deste.  

# Objetivo do projeto:
O objetivo desse projeto é desenvolver um programa capaz de realizar o pré-processamento de imagens de assinaturas, criando assim um banco de dados que será utilizado como conjunto de treinamento do sistema. Para o treinamento, será definido um conjunto de características a serem extraídas de cada imagem. Posteriormente, o programa deverá ser capaz de receber uma nova imagem de assinatura e identificar se ela pertence ao usuário ou se é uma falsificação.
	
# Exemplo de imagem de entrada:

<img src="https://imgur.com/a/w3G3XT3" width="250" height="100" title="Signature 1">

<img src="https://imgur.com/ky4IVqr" width="300" height="100" title="Signature 2">

<img src="https://imgur.com/gQGdJAn" width="300" height="100" title="Signature 3">

# Métodos:
- 1 - Mudança de tipo da imagem rgb de entrada para binária, em que os pixels de valor 1 representam a assinatura e de valor 0 representam o fundo. 
- 2 - Pré-processamento da imagem binária utilizando o método da esqueletização para reduzir a representação dos caracteres da assinatura para cadeias simples de largura de um pixel, porém preservando o restante de características relevantes para a classificação. Implementou-se o algoritmo de thinning, o qual utiliza o conceito de erosão morfológica de contornos iterativamente até que a largura dos traços reduza para um pixel.
- 3 - Extração de características por meio da análise da orientação dos traços.
- 4 - Treinamento do sistema por análise estatística.
- 5 - Teste e verificação.

 
