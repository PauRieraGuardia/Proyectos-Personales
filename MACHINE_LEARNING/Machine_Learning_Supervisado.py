"""
PROYECTO: Framework modular de Machine Learning Supervisado (POO)
---------------------------------------------------------------------------------------------------------------------------------

OBJETIVO:
Este script automatiza el flujo complejo de un proyecto de Machine Learning Supervisado, desde la ingesta de datos hasta la
evaluación de modelos, utilizando el paradigma de Programación Orientada a Objetos para garantizaar escalabilidad y mantenimiento.

ORIENTACIÓN Y ALCANCE:
1- Análisis Exploratior (EDA): Automatización de diagnósticos de calidad, detección de nulos y relaciones estadísticas.

2- Preprocesamiento Robusto: Implementación de pipelines de limpieza y experimientación con múltiples técnicas de codificación 
(Encoding)

3- Modelado Comparativo: Entrenamiento simultáneo de modelos basados en regresiones, árboles de decisión y métodos de ensamble

4- Evaluación Multimétrica: Validación cruzada y métricas de error (MSE, R2, Accuracy, etc.) para una selección de modelo basada en
evidencia

ESTRUCTURA DE CLASES:
- DataLoader: Se encarga de la carga y visión general inicial
- DataExplorer: Diagnóstico visual y estadístico.
- DataPreprocessor: Transformación de features y manejo de nulos.
- ModelManager: orquestador de entrenamiento y validación
- ModelOptimizer: Refinamiento de hiperparámetros. (FALTA DESARROLLO)

---------------------------------------------------------------------------------------------------------------------------------

"""

#===============================================================================================================================
# 1. LIBRERIAS Y DEPENDENCIAS
#===============================================================================================================================

# Manipulación de datos
import pandas as pd
import numpy as np

# Visualización
import matplotlib.pyplot as plt
import seaborn as sns

# Preprocesamiento y modelado
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, mean_squared_error, r2_score
import category_encoders as ce

# Modelos de Machine Learning
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# Control de warnings
import warnings
warnings.filterwarnings('ignore')

# Función display, facilita visualizar los DF mejor que el print
from IPython.display import display

# Displey todas las filas y columnas de cada dataframe
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


#===============================================================================================================================
# 2. DATA LOADER
#===============================================================================================================================

class DataLoader:
    """
    Responsabilidad: Carga de archivos y diagnóstico estructural inicial.
    El archivo debe de ser compacto, es decir, debe de estar tanto el conjunto de train como el de test para luego ser separados.
    """
    def __init__(self, train_path, target_col , sep, test_path = None):
        """
        Constructor: inicialiaz el objeto con la ruta y el objetivo.
        Encapsula los atributos principales del dataset.

        """
        self.train_path = train_path
        self.test_path = test_path
        self.target_col = target_col
        self.sep = sep

        self.df = None
        self.train_df = None
        self.test_df = None

        self.features = []
        self.num_features =  []
        self.cat_features =  []

    def load_data(self):

        if self.test_path is None:
            self.df = pd.read_csv(self.train_path, sep=self.sep)
            print(f"Dataset único cargado. Dimensiones:{self.df.shape}")
            display(self.df.head())

            return self.df
        
        else:
            self.train_df = pd.read_csv(self.train_path, sep=self.sep)
            self.test_df = pd.read_csv(self.test_path, sep=self.sep)

            print(f"Train cargado. Dimensiones: {self.train_df.shape}")
            print(f"Test cargado. Dimensiones: {self.test_df.shape}") 

            print("\nPrimeras filas de train:")
            display(self.train_df.head())

            print("\nPrimeras filas de test:")
            display(self.test_df.head())

    
    def get_initial_view(self):
        if self.test_path is None:
            if self.df is None:
                print("ERROR: No hay dataset cargado.")
                return

            print("Información general del dataset único:")
            self.df.info()

            print("\nTipos de variables:")
            print(self.df.dtypes.value_counts())

            print("\nPrimeras observaciones:")
            display(self.df.head())

        else: 
            
            if self.train_df is None or self.test_df is None:
                print("ERROR: No hay datasets cargados.")
                return

            print("Información general de TRAIN:")
            self.train_df.info()

            print("\nInformación general de TEST:")
            self.test_df.info()

            print("Tipos de variables de TRAIN:")
            print(self.train_df.dtypes.value_counts())

            print("\nTipos de variables de TEST:")
            print(self.test_df.dtypes.value_counts())

            print("\nPrimeras observaciones de TRAIN:")
            display(self.train_df.head())

            print("\nPrimeras observaciones de TEST:")
            display(self.test_df.head())

    def process_variable_structure(self):

        base_df = self.df if self.test_path is None else self.train_df

        if base_df is None:
            print("ERROR: No hay datos cargados.")
            return
          
        self.features = [col for col in base_df.columns if col != self.target_col]

        self.num_features = base_df[self.features].select_dtypes(include=["int64", "float64"]).columns.tolist()

        self.cat_features = base_df[self.features].select_dtypes(include=["object", "category", "bool"]).columns.tolist()

        print("Número de variables numéricas:", len(self.num_features))
        print("Número de variables categóricas:", len(self.cat_features))

        print("\nVariables numéricas:")
        print(self.num_features)

        print("\nVariables categóricas:")
        print(self.cat_features)
    
#===============================================================================================================================
# 3. DATA EXPLORER
#===============================================================================================================================

class DataExplorer():
    """
    Responsabilidad: Diagnóstico visual y estadístico del dataset.
    Recibe el trabajo previo del DataLoader para profundizar en los insights.
    """
    def __init__(self,target_col,num_features,cat_features,df=None, train_df = None, test_df=None):
        """
        Constructor: recibe el DataFrame cargado en DataLoader. 
        Encapsula el estado del dataset para su exploración.
        """
        self.df = df
        self.train_df = train_df
        self.test_df = test_df

        self.num_features = num_features
        self.cat_features = cat_features
        self.target_col = target_col


    def _get_main_df(self):
        """
        Devuelve el dataset principal para EDA.
        """
        if self.df is not None:
            return self.df

        if self.train_df is not None:
            return self.train_df

        return None
    

    def get_stats(self):
        """
        Estadísticas descriptivas.
        """

        data = self._get_main_df()

        if data is None:
            print("ERROR: No hay datos para explorar.")
            return

        print("Estadísticas calculadas sobre:")
        print("Dataset único" if self.df is not None else "Train")

        
        if self.num_features:
            print("Estadísticas Descriptivas Variables Numéricas:")
            print(data[self.num_features].describe())
        else: 
            print("No ha variables numéricas")
            
        if self.cat_features:
            print("Estadísticas Descriptivas Variables Categóricas:")
            print(data[self.cat_features].describe())
            print("Distribución de frecuencias para variables categóricas")
            for col in self.cat_features:
                print(f"Distribución  de {col}:")
                print(data[col].value_counts(normalize=True).head())
        else: 
            print("No hay variables categóricas")



    def check_quality(self):

        data = self._get_main_df()

        if data is None:
            print("ERROR: No hay datos para analizar calidad.")
            return
        
        print("Calidad calculada sobre:")
        print("Dataset único" if self.df is not None else "Train")

        self.missing_count = data.isnull().sum()
        self.missing_pct = (self.missing_count / len(data)) * 100
        print("Valores nulos:")
        self.missing_df = pd.DataFrame({
                "missing_count": self.missing_count,
                "missing_pct": self.missing_pct}).sort_values("missing_pct", ascending=False)
        display(self.missing_df) 

        print("Detección duplicados:")
        self.num_duplicated = data.duplicated().sum()
        print(self.num_duplicated)

        if self.num_features:
            print("Detección mediante Boxplot de outliers:")
            for col in self.num_features:
                plt.figure(figsize=(6, 3))
                sns.boxplot(x=data[col])
                plt.title(f"Distribución y detección visual de outliers en {col}")
                plt.show()

            print("Detección numérica de outliers mediante rango intercuartílico (IQR):")
            self.outliers_report = {}
            for col in self.num_features:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                
                count = ((data[col] < lower) | (data[col] > upper)).sum()
                self.outliers_report[col] = count

            self.outliers_df = pd.Series(self.outliers_report).to_frame(name="Outliers Count")
            display(self.outliers_df)
        else:
            print("No se pueden calcular outliers: No existen variables numéricas")
    
    def plot_correlations(self):
         
        data = self._get_main_df()

        if data is None:
            print("ERROR: No hay datos para analizar calidad.")
            return
    
        if not self.num_features:
            print("No hay variables numéricas para calcular correlaciones.")
            return
        
        self.corr_matrix = data[self.num_features].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(self.corr_matrix, annot=False, cmap="coolwarm", center=0)
        plt.title("Matriz de correlación - Variables numéricas")
        plt.show()

    def plot_distribution_classification(self):

        data = self._get_main_df()

        if data is None:
            print("ERROR: No hay datos para analizar calidad.")
            return
        
        """ Análisis para problemas de CLASIFICACIÓN (Target categórico) """
        print("Distribución del target (clasificación):")
        print(data[self.target_col].value_counts(normalize=True) * 100)
        data[self.target_col].value_counts().plot(kind="bar", color="lightblue", edgecolor="black",legend=False)
        plt.title("Distribución del target")
        plt.xlabel("Clase")
        plt.ylabel("Frecuencia")
        plt.show()
    
    def plot_distribution_regression(self):
        
        data = self._get_main_df()

        if data is None:
            print("ERROR: No hay datos para analizar calidad.")
            return
    
        """ Análisis para problemas de REGRESIÓN (Target numérico) """
        print("Estadísticas del target (regresión):")
        display(data[self.target_col].describe())

        plt.hist(data[self.target_col], bins=30, color="skyblue", edgecolor="black")
        plt.title("Distribución del target")
        plt.xlabel(self.target_col)
        plt.ylabel("Frecuencia")
        plt.show()
        

#===============================================================================================================================
# 4. DATA PREPROCESSOR
#===============================================================================================================================

class DataPreprocessor():
    """
    Responsabilidad: Transformación y preparación de datos.
    Permite elegir técnicas de imputación, tratamiento de outliers y encoding
    según los insights obtenidos en la fase de exploración.
    """
    def __init__(self, target_col, num_features, cat_features,df = None, train_df = None, test_df = None ):
        self.df = df
        self.train_df = train_df
        self.test_df = test_df

        self.num_features = num_features
        self.cat_features = cat_features
        self.target_col = target_col

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

        self.numeric_impute_values = {}
        self.categorical_impute_values = {}
        self.encoders = {}

    def finalize_and_split(self, problem_type="classification", test_size=0.2):
        """
        Responsabilidad: preparar X_train, X_test, y_train, y_test.
        - Si hay df único, se hace train_test_split.
        - Si hay train_df y test_df separados, se usan directamente.
        """

        if self.df is not None:

            self.X = self.df.drop(columns=[self.target_col])
            self.y = self.df[self.target_col]

            stratify_param = self.y if problem_type == "classification" else None

            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.X,
                self.y,
                test_size=test_size,
                stratify=stratify_param,
                random_state=42
            )

            print("Dataset único separado en train y test.")
            print("Tamaño del conjunto de entrenamiento:", self.X_train.shape)
            print("Tamaño del conjunto de prueba:", self.X_test.shape)

        elif self.train_df is not None and self.test_df is not None:

            self.X_train = self.train_df.drop(columns=[self.target_col])
            self.y_train = self.train_df[self.target_col]

            if self.target_col in self.test_df.columns:
                self.X_test = self.test_df.drop(columns=[self.target_col])
                self.y_test = self.test_df[self.target_col]
                print("Train/test separados cargados. El test contiene target.")
            else:
                self.X_test = self.test_df.copy()
                self.y_test = None
                print("Train/test separados cargados. El test NO contiene target.")

            print("Tamaño del conjunto de entrenamiento:", self.X_train.shape)
            print("Tamaño del conjunto de prueba:", self.X_test.shape)

        else:
            print("ERROR: No hay datos suficientes para particionar.")
            return


    def drop_features(self, variables):
        """
        Elimina variables seleccionadas manualmente del conjunto de entrenamiento y test.

        Uso típico:
        - Variables con demasiados nulos.
        - Variables con demasiadas categorías.
        - Variables irrelevantes tras el EDA.
        - IDs que no quieres usar como predictoras.
        """

        if self.X_train is None or self.X_test is None:
            print("ERROR: Primero ejecuta finalize_and_split().")
            return

        if isinstance(variables, str):
            variables = [variables]

        variables_existentes_train = [col for col in variables if col in self.X_train.columns]
        variables_existentes_test = [col for col in variables if col in self.X_test.columns]

        self.X_train = self.X_train.drop(columns=variables_existentes_train)

        if variables_existentes_test:
            self.X_test = self.X_test.drop(columns=variables_existentes_test)

        self.num_features = [col for col in self.num_features if col not in variables]
        self.cat_features = [col for col in self.cat_features if col not in variables]

        print("Variables eliminadas:")
        print(variables)

        print("X_train actualizado:", self.X_train.shape)
        print("X_test actualizado:", self.X_test.shape)


    def handle_missing(self, num_strategy="median"):
        """
        Imputación lógica.
        - Los valores se calculan usando solo X_train.
        - Luego se aplican a X_train y X_test.
        """

        if self.X_train is None or self.X_test is None:
            print("ERROR: Primero ejecuta finalize_and_split().")
            return

        # 1. Tratamiento valores nulos numéricos
        if self.num_features:
            for col in self.num_features:

                if num_strategy == "median":
                    valor = self.X_train[col].median()
                else:
                    valor = self.X_train[col].mean()

                self.numeric_impute_values[col] = valor

                self.X_train[col].fillna(valor, inplace=True)

                if col in self.X_test.columns:
                    self.X_test[col].fillna(valor, inplace=True)

          # 2. Tratamiento valores nulos categóricos
        if self.cat_features:
            for col in self.cat_features:

                valor = self.X_train[col].mode()[0]

                self.categorical_impute_values[col] = valor

                self.X_train[col].fillna(valor, inplace=True)

                if col in self.X_test.columns:
                    self.X_test[col].fillna(valor, inplace=True)

        print(f"Nulos imputados usando TRAIN. Num: {num_strategy} / Cat: moda")
    
        
    def handle_outliers(self, threshold=0.01):
        """
        Tratamiento de outliers mediante clipping (winsorización).

        - NO elimina filas
        - Sustituye valores extremos por límites percentiles
        - Los límites se calculan usando solo X_train
        - Se aplican tanto a X_train como a X_test
        """
        if self.X_train is None or self.X_test is None:
            print("ERROR: Primero ejecuta finalize_and_split().")
            return

        if not self.num_features:
            print("ERROR: No hay variables numéricas para procesar.")
            return

        for col in self.num_features:

            if col not in self.X_train.columns:
                continue

            # Calcular límites usando SOLO train
            lower_limit = self.X_train[col].quantile(threshold)
            upper_limit = self.X_train[col].quantile(1 - threshold)

            # Aplicar clipping en TRAIN
            self.X_train[col] = self.X_train[col].clip(
                lower=lower_limit,
                upper=upper_limit
            )

            # Aplicar mismos límites en TEST
            if col in self.X_test.columns:
                self.X_test[col] = self.X_test[col].clip(
                    lower=lower_limit,
                    upper=upper_limit
                )

        print("Outliers tratados mediante clipping.")
        print(f"Threshold aplicado: {threshold}")
        print(f"Filas en X_train: {len(self.X_train)}")
        print(f"Filas en X_test: {len(self.X_test)}")

        
    def apply_encoding_cat(self, variable, method):
        """
        Aplica técnicas de codificación.
        - El encoder se aprende con X_train.
        - Luego se aplica a X_test.
        """

        if self.X_train is None or self.X_test is None:
            print("ERROR: Primero ejecuta finalize_and_split().")
            return

        if variable not in self.X_train.columns:
            print(f"ERROR: La columna '{variable}' no existe en X_train.")
            return

        method = method.strip().lower()
        
        try:

            # MÉTODO 1: LABEL ENCODING
            if method == "label encoding":

                encoder = LabelEncoder()

                # Ajustar solo con TRAIN
                encoder.fit(self.X_train[variable].astype(str))

                # Transformar TRAIN
                self.X_train[variable] = encoder.transform(
                    self.X_train[variable].astype(str)
                )

                # Transformar TEST si existe la variable
                if variable in self.X_test.columns:

                    # Categorías conocidas por el encoder
                    known_classes = set(encoder.classes_)

                    # Si en TEST aparece una categoría nueva, se sustituye por la primera clase conocida
                    self.X_test[variable] = self.X_test[variable].astype(str).apply(
                        lambda x: x if x in known_classes else encoder.classes_[0]
                    )

                    self.X_test[variable] = encoder.transform(
                        self.X_test[variable].astype(str)
                    )

                self.encoders[variable] = encoder

                if variable in self.cat_features:
                    self.cat_features.remove(variable)

                if variable not in self.num_features:
                    self.num_features.append(variable)

                print(f"Label Encoding aplicado a '{variable}' usando TRAIN.")

            # MÉTODO 2: ONE-HOT Encoding 
            elif method == "one-hot encoding":

                encoder = OneHotEncoder(
                    drop="first",
                    sparse_output=False,
                    handle_unknown="ignore"
                )

                encoded_train = encoder.fit_transform(
                    self.X_train[[variable]].astype(str)
                )

                encoded_test = encoder.transform(
                    self.X_test[[variable]].astype(str)
                )

                encoded_cols = encoder.get_feature_names_out([variable])

                encoded_train_df = pd.DataFrame(
                    encoded_train,
                    columns=encoded_cols,
                    index=self.X_train.index
                )

                encoded_test_df = pd.DataFrame(
                    encoded_test,
                    columns=encoded_cols,
                    index=self.X_test.index
                )

                self.X_train = pd.concat(
                    [self.X_train.drop(columns=[variable]), encoded_train_df],
                    axis=1
                )

                self.X_test = pd.concat(
                    [self.X_test.drop(columns=[variable]), encoded_test_df],
                    axis=1
                )

                self.encoders[variable] = encoder

                if variable in self.cat_features:
                    self.cat_features.remove(variable)

                self.num_features.extend(encoded_cols.tolist())

                print(f"One-Hot Encoding aplicado a '{variable}' usando TRAIN.")

            # MÉTODO 3: BINARY ENCODING
            elif method == "binary encoding":

                encoder = ce.BinaryEncoder(cols=[variable])

                self.X_train = encoder.fit_transform(self.X_train)

                if variable in self.X_test.columns:
                    self.X_test = encoder.transform(self.X_test)

                self.encoders[variable] = encoder

                if variable in self.cat_features:
                    self.cat_features.remove(variable)

                self.num_features = self.X_train.select_dtypes(
                    include=["int64", "float64"]
                ).columns.tolist()

                print(f"Binary Encoding aplicado a '{variable}' usando TRAIN.")

            # MÉTODO 4: TARGET ENCODING 
            elif method == "target encoding":

                encoder = ce.TargetEncoder(cols=[variable])

                self.X_train = encoder.fit_transform(
                    self.X_train,
                    self.y_train
                )

                if variable in self.X_test.columns:
                    self.X_test = encoder.transform(self.X_test)

                self.encoders[variable] = encoder

                if variable in self.cat_features:
                    self.cat_features.remove(variable)

                if variable not in self.num_features:
                    self.num_features.append(variable)

                print(f"Target Encoding aplicado a '{variable}' usando TRAIN.")


            # MÉTODO 5. RARE LABEL ENCODING
            elif method == "rare label encoding":

                freq = self.X_train[variable].value_counts(normalize=True)

                categorias_frecuentes = list(freq[freq > 0.05].index)

                self.X_train[variable] = np.where(
                    self.X_train[variable].isin(categorias_frecuentes),
                    self.X_train[variable],
                    "Rare"
                )

                if variable in self.X_test.columns:
                    self.X_test[variable] = np.where(
                        self.X_test[variable].isin(categorias_frecuentes),
                        self.X_test[variable],
                        "Rare"
                    )

                self.encoders[variable] = categorias_frecuentes

                print(f"Rare Label Encoding aplicado a '{variable}' usando TRAIN.")

            # MÉTODO 6: FREQUENCY ENCODING
            elif method == "frequency encoding":

                freq_map = self.X_train[variable].value_counts()

                self.X_train[variable] = self.X_train[variable].map(freq_map)

                if variable in self.X_test.columns:
                    self.X_test[variable] = self.X_test[variable].map(freq_map)
                    self.X_test[variable].fillna(0, inplace=True)

                self.encoders[variable] = freq_map

                if variable in self.cat_features:
                    self.cat_features.remove(variable)

                if variable not in self.num_features:
                    self.num_features.append(variable)

                print(f"Frequency Encoding aplicado a '{variable}' usando TRAIN.")

            else:
                print(f"MÉTODO NO RECONOCIDO: '{method}'.")

        except Exception as e:
            print(f"FALLO CRÍTICO al aplicar {method} en '{variable}': {e}")

        
    def final_cleanup(self):
        """
        Responsabilidad: Pulido estético e integridad final.
        Ejecutar antes de finalize_and_split para verificar el DF limpio.
        """

        if self.X_train is None or self.X_test is None:
            print("ERROR: Primero ejecuta finalize_and_split().")
            return

        nulos_train = self.X_train.isnull().sum().sum()
        nulos_test = self.X_test.isnull().sum().sum()

        print(f"Total de valores nulos en X_train: {nulos_train}")
        print(f"Total de valores nulos en X_test: {nulos_test}")

        train_cols = set(self.X_train.columns)
        test_cols = set(self.X_test.columns)

        missing_in_test = train_cols - test_cols
        missing_in_train = test_cols - train_cols

        if missing_in_test:
            print("Columnas presentes en train pero no en test:")
            print(missing_in_test)

        if missing_in_train:
            print("Columnas presentes en test pero no en train:")
            print(missing_in_train)

        common_cols = list(train_cols.intersection(test_cols))

        self.X_train = self.X_train[common_cols]
        self.X_test = self.X_test[common_cols]

        print("Limpieza final completada.")
        print("Columnas finales:", len(common_cols))

    def get_processed_data(self):
        """
        Devuelve los datos procesados.
        """

        return self.X_train, self.X_test, self.y_train, self.y_test
    

    
#===============================================================================================================================
# 5. MODEL MANAGER
#===============================================================================================================================

class ModelManager():
    """
    Responsabilidad:
    Entrenar y evaluar distintos modelos según el tipo de problema:
    - classification
    - regression
    """
    def __init__(self,X_train, X_test, y_train, y_test, problem_type):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.problem_type = problem_type.lower()

        self.models = {}
        self.results = {}
        self.predictions= {}

    def define_models(self):
        """
        Define los modelos según el tipo de problema.
        """
        if self.problem_type == "classification":
            self.models = {
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),

                "Decision Tree Classifier": DecisionTreeClassifier(
                    criterion="gini",
                    max_depth=5,
                    min_samples_split=10,
                    random_state=42
                ),

                "Random Forest Classifier": RandomForestClassifier(
                    n_estimators=200,
                    max_depth=5,
                    min_samples_leaf=5,
                    random_state=42,
                    n_jobs=-1
                )
            }

        elif self.problem_type == "regression":
            self.models = {
                "Linear Regression": LinearRegression(),

                "Decision Tree Regressor": DecisionTreeRegressor(
                    max_depth=5,
                    min_samples_split=10,
                    random_state=42
                ),

                "Random Forest Regressor": RandomForestRegressor(
                    n_estimators=200,
                    max_depth=5,
                    min_samples_leaf=5,
                    random_state=42,
                    n_jobs=-1
                )
            }

        else:
            print("ERROR: problem_type debe ser 'classification' o 'regression'.")

        
    def train_and_evaluate(self):
        """
        Entrena todos los modelos definidos y calcula métricas.
        """
        if not self.models:
            self.define_models()

        for name, model in self.models.items():
            
            print(f"Modelo: {name}")

            # 1. Entrenar
            model.fit(self.X_train, self.y_train)

            # Predecir
            y_pred = model.predict(self.X_test)

            self.predictions[name] = y_pred

            if self.y_test is None:
                print("No hay y_test. Solo se generan predicciones para este modelo.")
                continue

            # 3. Evaluar según el tipo de problema

            if self.problem_type == "classification":
                accuracy = accuracy_score(self.y_test, y_pred)

                self.results[name] = {
                    "Accuracy": accuracy
                }

                print(f"Accuracy: {accuracy:.4f}")

                if hasattr(model, "predict_proba"):
                    try:
                        y_proba = model.predict_proba(self.X_test)[:, 1]
                        roc_auc = roc_auc_score(self.y_test, y_proba)

                        self.results[name]["ROC-AUC"] = roc_auc

                        print(f"ROC-AUC: {roc_auc:.4f}")

                    except:
                        print("ROC-AUC no calculable para este modelo.")

                print("Classification Report:")
                print(classification_report(self.y_test, y_pred))

            elif self.problem_type == "regression":

                mse = mean_squared_error(self.y_test, y_pred)
                r2 = r2_score(self.y_test, y_pred)

                self.results[name] = {
                    "MSE": mse,
                    "R2": r2
                }

                print(f"MSE: {mse:.4f}")
                print(f"R2: {r2:.4f}")

       # Si hay y_test, devuelve resultados y predicciones.
        if self.y_test is not None:
            results_df = pd.DataFrame(self.results).T

            print("=" * 80)
            print("RESUMEN FINAL DE RESULTADOS:")
            display(results_df)

            return results_df, self.predictions

        # Si no hay y_test, devuelve solo predicciones.
        else:
            print("=" * 80)
            print("Predicciones generadas. No hay métricas porque y_test no existe.")

            return self.predictions

#===============================================================================================================================
# 6. MODEL OPTIMIZIER
#===============================================================================================================================

class ModelOptimizer():
    """
    Responsabilidad: Optimización de hiperparámetros.
    Aplica técnicas como GridSearchCV para encontrar la mejor configuración 
    del modelo seleccionado.
    """
    def __init__(self):
        pass