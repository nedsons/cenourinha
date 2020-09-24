import numpy as np #biblioteca utilizada para trabalhar com vetores
import pandas as pd #biblioteca para trabalhar com dataframes (planilhas excel)
import seaborn as sns #biblioteca utilizada para criar gráficos mais "bonitos"
import matplotlib.pyplot as plt #biblioteca para criar gráficos "comuns" ao estilo Matlab
import google

# abrir o arquivo csv que contém os dados a serem utilizados durante a prática
data = pd.read_csv('FILE')

#visualizando as 5 primeiras linhas do banco de dados
data.head() #pode colocar customers.head(valor), onde valor = números de x primeiras linhas

#verificando a existência de campos nulos
data.info()

#verificando a existência de campos nulos
data.isnull().sum()

#adicionando valores nulos
data_null=data.copy() #cria cópia
for col in data_null.columns:
    data_null.loc[data_null.sample(frac=0.1).index, col] = np.nan
    
data_null.info() #verificando as colunas nulas

#analisando o dataset
data_null.head(10)

#verificando a existência de campos nulos
data_null.isnull().sum()

#deletando as linhas que possuem algum valor nulo
data_null.dropna()

#preenchendo os valores nan com o valor 0
data_null.fillna(0)

data_null.describe() #encontra as estatísticas do dataset

#preenchendo os valores médios da coluna
data_null.fillna(data_null.mean())

#analisando o banco de dados
data.describe() #função que retorna uma análise superficial dos dados 

boxplot = data.boxplot(column=['column1', 'column2', 'column3'])  #constroi o boxplot para as colunas desejadas (colocar as colunas)

#Z-score
from scipy import stats
z = np.abs(stats.zscore(data['column'].values)) #trocar 'column'
threshold = 2
result=np.where(z > threshold)
outlier=customers.iloc[result[0]]
print(z)

outlier #todos os usuários com salário anual com possível outlier

#analisando a distribuição dos clientes por gênero
sns.countplot(x='Gender', data=data); # cria o gráfico que conta a quantidade de consumidores existente em cada um dos gêneros
plt.title('Distribuição dos clientes quanto ao gênero');  #adiciona o título no gráfico

#analisando a distribuição dos clientes quanto a idade através do histograma
data.hist('Age', bins=35);  #seleciona a coluna idade para realizar o histograma
                                 # os "bins" indicam a quantidade de grupos que se deseja dividir os dados
plt.title('Title');# adiciona o título ao gráfico (histograma)
plt.xlabel('xlabel');

cat_df_data = data.select_dtypes(include=['object']) #copiando as colunas que são do tipo categoricas

cat_df_data.head()

# **trocar as variáveis
replace_map = {'Gender': {'Male': 1, 'Female': 2}}  #define o dicionário a ser utilizado (map) 
labels = cat_df_data['Gender'].astype('category').cat.categories.tolist() #encontra a lista das variáveis categóricas
replace_map_comp = {'Gender' : {k: v for k,v in zip(labels,list(range(1,len(labels)+1)))}} #define o mapeamento
print(replace_map_comp)

cat_df_data_replace =pd.read_csv('FILE')  #realiza a cópia do dataset

cat_df_data_replace.replace(replace_map_comp, inplace=True) #aplica o mapeamento para o dataset
cat_df_data_replace.head()

#cat_df_customers_lc = customers
data = pd.read_csv('FILE')

cat_df_data_lc=data

cat_df_data_lc['Gender']=pd.Categorical(cat_df_data_lc['Gender'])
cat_df_data_lc.dtypes

cat_df_data_lc['Gender'] = cat_df_data_lc['Gender'].cat.codes
cat_df_data_lc.head()

# importando o label encoding
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder() #instanciando o objeto

# aplicando a codificação para as colunas categóricas
data_label=pd.read_csv('FILE')
data_label['Gender'] =  le.fit_transform(data_label['Gender'])
data_label.head(10)

# Get dummies
data_one_hot=pd.read_csv('FILE')
#customers_one_hot['Gender']=pd.Categorical(customers_one_hot['Gender'])
data_one_hot= pd.get_dummies(data_one_hot)
# customers_one_hot head
data_one_hot.head()
data=pd.read_csv('FILE')

# importe OneHotEncoder
data_one_hot=data
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder() #instancia o objeto

# aplica o one hot encoding para a coluna 
data_ohe = ohe.fit_transform(data_one_hot['Gender'].values.reshape(-1,1)).toarray()# It returns an numpy array
data_ohe.shape

print(data_ohe)
