#regressão utilizando o otimizador
#Definindo as bibliotecas
import numpy as np  #biblioteca necessária para trabalhar com os vetores e matrizes
import scipy   #biblioteca necessária para obter as funções de treinamento 
import matplotlib.pyplot as plt #biblioteca utilizada para construir os gráficos
from scipy.optimize import curve_fit # biblioteca necessária para realiza a otimização dos MSE

#definindo as variáveis
idade=[18,25,57,45,26,64,37,40,24,33]  # variável independente
salarioAnual=[15000,29000,68000,52000,32000,80000,41000,45000,26000,33000] #variável dependente
xData = np.array(idade)    #transformando a lista em array
yData = np.array(salarioAnual) #transformando a lista em array

#define a função a ser otimizada (regressão simples)
def equacaoLinear(x, a, b): 
    return a * x + b

#gera os parâmetros iniciais para o otimizador
parametrosIniciais = np.array([1.0, 1.0])

#realiza a otimização através do erro médio quadrado (MSE)
parametrosOtimizados, pcov = curve_fit(equacaoLinear, xData, yData, parametrosIniciais)
#parametrosOtimizados - contém os parâmetros de ajuste da curva
#pcov - contém a covariância dos parâmteros encontrados

#realiza a previsão dos dados através do modelo (constroi a equação linear)
pervisaoModelo = equacaoLinear(xData, *parametrosOtimizados) #utiliza a função linear com os parâmetros otimizados

#encontra o erro obsoluto (linhas verticais)
erroAbsoluto = pervisaoModelo - yData #(valor previsto - valor real)

#calcula o erro quadrado entre cada medida
SE = np.square(erroAbsoluto) 
#calcula o MSE
MSE = np.mean(SE) 
print('SE: ', SE)
print('MSE: ', MSE)

#realiza o cálculo do coeficiente de determinação
Rsquared = 1.0 - (np.var(erroAbsoluto) / np.var(yData)) # numpy.var - encontra a variância entre os dados do vetor
print('Coeficiente de Determinação:', Rsquared)

#mostra os parâmetros da regressão
print('Y = {}X {}'.format(parametrosOtimizados[0],parametrosOtimizados[1]))

#realiza o plot da figura
f = plt.figure(figsize=(4, 4), dpi=100) #indica o tamanho da figura
axes = f.add_subplot(111) #cria os objetos para o subplot

# frealiza o plot dos dados (pontos no gráfico)
axes.plot(xData, yData,'ro')

# cria os dados para serem utilizados na construção da linha (equação) 
xModel = np.linspace(min(xData), max(xData)) #encontra os valores maximos e mínimos da "linha"
yModel = equacaoLinear(xModel, *parametrosOtimizados) # acplica a função com os parâmetros obtidos

# realiza o plot da "linha"
axes.plot(xModel, yModel)
plt.xlabel("Idade")
plt.ylabel("Salário Anual (R$)")

#utiliza as funções do sklearn para construir a regressão linear
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

reg= LinearRegression() #objeto para a regressão linear
x_ModeloSklern=xData.reshape((-1, 1)) # na regressão linear é necessário que o X seja 2D
regressao= reg.fit (x_ModeloSklern,yData) # realiza a regressão

previsao=reg.predict(x_ModeloSklern)

MSE= mean_squared_error(yData,previsao) # encontra o MSE através do sklearn
print('MSE: ', MSE)

#parâmetros encontrados
print('Y = {}X {}'.format(reg.coef_,reg.intercept_))

from sklearn.metrics import r2_score #método para o cálculo do R2

R_2 = r2_score(yData, previsao)  #realiza o cálculo do R2

print("Coeficiente de Determinação (R2):", R_2)

# 
#
#
#Agora vamos realizar a construção de uma regressão para um banco de dados real (mais complexo)

#regressão utilizando um BD mais complexo
import pandas as pd

#realiza a leitura do banco de dados
data=pd.read_csv("../input/headbrain/headbrain.csv")
data.head()  #realiza visualização das 5 primeiras linhas do BD

#como o formato dos dados em cada uma das colunas do dataframe são séries é necessário converter array
x=data["Head Size(cm^3)"].values
y=data["Brain Weight(grams)"].values

#Realiza a construção do modelo de regressão
reg= LinearRegression()
x_Reshaped=x.reshape((-1, 1)) #coloca os dados no formato 2D
regressao= reg.fit (x_Reshaped,y) # encontra os coeficientes (realiza a regressão)

#realiza a previsão
previsao=reg.predict(x_Reshaped)

#parâmetros encontrados
print('Y = {}X {}'.format(reg.coef_,reg.intercept_))

R_2 = r2_score(y, previsao)  #realiza o cálculo do R2

print("Coeficiente de Determinação (R2):", R_2)

#realiza o plot dos dados
plt.figure(figsize=(4, 4), dpi=100)
plt.scatter(x, y,  color='gray') #realiza o plot do gráfico de dispersão
plt.plot(x, previsao, color='red', linewidth=2) # realiza o plto da "linha"
plt.xlabel("Head Size(cm^3)")
plt.ylabel("Brain Weight(grams)")
plt.show()