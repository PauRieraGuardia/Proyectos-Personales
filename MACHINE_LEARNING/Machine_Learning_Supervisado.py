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
- ModelOptimizer: Refinamiento de hiperparámetros.

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


#===============================================================================================================================
# 2. DATA LOADER
#===============================================================================================================================

class DataLoader:
    """
    Responsabilidad: Carga de archivos y diagnóstico estructural inicial.
    El archivo debe de ser compacto, es decir, debe de estar tanto el conjunto de train como el de test para luego ser separados.
    """
    def __init__(self, file_path, target_col,sep):
        """
        Constructor: inicialiaz el objeto con la ruta y el objetivo.
        Encapsula los atributos principales del dataset.

        """
        self.file_path = file_path
        self.target_col = target_col
        self.sep = sep
        self.df = None
        self.features = []
        self.num_features =  []
        self.cat_features =  []

    def load_data(self):
        self.df = pd.read_csv(self.file_path, sep=self.sep)
        print(f"Dataset cargado. Dimensiones:{self.df.shape}")
        return self.df.head(5)
    
    def get_initial_view(self):
        if self.df is not None:
            print("Información general:")
            self.df.info()
            print("Tipos de variables:")
            print(self.df.dtypes.value_counts())
            print("Primeras observaciones:")
            display(self.df.head(5)) 
        else:
            print("ERROR: No hay dataset cargado")

    def process_variable_structure(self):
        if self.df is not None:
            self.features = [col for col in self.df.columns if col != self.target_col]
            self.num_features = self.df[self.features].select_dtypes(include=["int64", "float64"]).columns.tolist()
            self.cat_features = self.df[self.features].select_dtypes(include=["object", "category"]).columns.tolist()
            print("Número de variables numéricas:", len(self.num_features))
            print("Número de variables categóricas:", len(self.cat_features))
        else: 
            print("ERROR: No hay dataset cargado")
    
#===============================================================================================================================
# 3. DATA EXPLORER
#===============================================================================================================================

class DataExplorer():
    """
    Responsabilidad: Diagnóstico visual y estadístico del dataset.
    Recibe el trabajo previo del DataLoader para profundizar en los insights.
    """
    def __init__(self,df,target_col,num_features,cat_features):
        """
        Constructor: recibe el DataFrame cargado en DataLoader. 
        Encapsula el estado del dataset para su exploración.
        """
        self.df = df
        self.num_features = num_features
        self.cat_features = cat_features
        self.target_col = target_col

    def get_stats(self):
        if self.df is not None:
            if self.num_features:
                print("Estadísticas Descriptivas Variables Numéricas:")
                print(self.df[self.num_features].describe())
            else: 
                print("No ha variables numéricas")
            if self.cat_features:
                print("Estadísticas Descriptivas Variables Categóricas:")
                print(self.df[self.cat_features].describe())
                print("Distribución de frecuencias para variables categóricas")
                for col in self.cat_features:
                    print(f"Distribución  de {col}:")
                    print(self.df[col].value_counts(normalize=True).head())
            else: 
                print("No hay variables categóricas")
        else:
            print("ERROR: No hay dataset cargado")


    def check_quality(self):
        self.missing_count = self.df.isnull().sum()
        self.missing_pct = (self.missing_count /len(self.df)) * 100
        print("Valores nulos:")
        self.missing_df = pd.DataFrame({
                "missing_count": self.missing_count,
                "missing_pct": self.missing_pct}).sort_values("missing_pct", ascending=False)
        display(self.missing_df) 

        print("Detección duplicados:")
        self.num_duplicated = self.df.duplicated().sum()
        print(self.num_duplicated)

        if self.num_features:
            print("Detección mediante Boxplot de outliers:")
            for col in self.num_features:
                plt.figure(figsize=(6, 3))
                sns.boxplot(x=self.df[col])
                plt.title(f"Distribución y detección visual de outliers en {col}")
                plt.show()

            print("Detección numérica de outliers mediante rango intercuartílico (IQR):")
            self.outliers_report = {}
            for col in self.num_features:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                
                count = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
                self.outliers_report[col] = count

            self.outliers_df = pd.Series(self.outliers_report).to_frame(name="Outliers Count")
            display(self.outliers_df)
        else:
            print("No se pueden calcular outliers: No existen variables numéricas")
    
    def plot_correlations(self):
        if not self.num_features:
            print("No hay variables numéricas para calcular correlaciones.")
            return
        self.corr_matrix = self.df[self.num_features].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(self.corr_matrix, annot=True, cmap="coolwarm", center=0)
        plt.title("Matriz de correlación - Variables numéricas")
        plt.show()

    def plot_distribution_classification(self):
        """ Análisis para problemas de CLASIFICACIÓN (Target categórico) """
        print("Distribución del target (clasificación):")
        print(self.df[self.target_col].value_counts(normalize=True) * 100)
        self.df[self.target_col].value_counts().plot(kind="bar", color="lightblue", edgecolor="black")
        plt.title("Distribución del target")
        plt.xlabel("Clase")
        plt.ylabel("Frecuencia")
        plt.show()
    
    def plot_distribution_regression(self):
        """ Análisis para problemas de REGRESIÓN (Target numérico) """
        print("Estadísticas del target (regresión):")
        display(self.df[self.target_col].describe())

        plt.hist(self.df[self.target_col], bins=30, color="skyblue", edgecolor="black")
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
    def __init__(self, df, target_col, num_features, cat_features):
        self.df = df
        self.num_features = num_features
        self.cat_features = cat_features
        self.target_col = target_col

    def handle_missing(self,num_strategy="median"):
        """
        Imputación lógica: 
        - Categóricas: Siempre usa la moda (procedimiento estándar).
        - Numéricas: Permite elegir entre 'median' o 'mean'.
        """
        # Seguro existencia DF
        if self.df is None:
            print("ERROR: No hay dataset cargado")
            return
        
        # 1. Tratamiento valores nulos numéricos
        if self.num_features:
           for col in self.num_features:
                if num_strategy == "median":
                    valor = self.df[col].median()
                else:
                    valor = self.df[col].mean()
                
                # Filleado directo al DF de la instancia
                self.df[col].fillna(valor, inplace=True)

        # 2. Tratamiento valores nulos categóricos
        if self.cat_features:
          for col in self.cat_features:
                # Solo si hay nulos, para evitar errores de índice en .mode()
                if self.df[col].isnull().any():
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            
        print(f"Dataset actualizado: Nulos imputados (Num: {num_strategy} / Cat: moda)")
    
        
    def handle_outliers(self,threshold=0.01):
        """
        Responsabilidad: Eliminar outliers mediante la técnica de Trimming.
        Elimina el % indicado de los extremos (puntas) de las variables numéricas.
        """
        if self.df is None or not self.num_features:
            print("ERROR: No hay datos o variables numéricas para procesar.")
            return
        initial_rows = len(self.df)
        for col in self.num_features:
            # Calculamos los límites (percentiles)
            lower_limit = self.df[col].quantile(threshold)
            upper_limit = self.df[col].quantile(1 - threshold)
            
            # Filtramos el DataFrame original
            self.df = self.df[(self.df[col] >= lower_limit) & (self.df[col] <= upper_limit)]
        
        rows_removed = initial_rows - len(self.df)
        print(f"Tratamiento de outliers completado ({threshold*100}% en cada extremo).")
        print(f"Filas eliminadas: {rows_removed} | Filas restantes: {len(self.df)}")
        
    def apply_encoding_cat(self, variable, method):
        """
        Aplica técnicas de codificación a una variable categórica específica.
        - Label Encoding
        - One-Hot Encoding
        - Binary Encoding
        - Target Encoding
        - Rare Label Encoding
        - Frequency Encoding
        """
        # 1. Validación de estado inicial
        if self.df is None:
            print("ERROR: No hay datos o variables numéricas para procesar.")
            return
        
        # 2. Validación de existencia de la columna
        if variable not in self.df.columns:
            print(f"ERROR: La columna '{variable}' no existe en el dataset.")
            return
        
        # 3. Normalización del método (evita errores por mayúsculas o espacios)
        method = method.strip().lower()
        
        try:
            # Método 1: Label Encoding (codificación ordinal simple).
            if method =="label encoding":
                encoder = LabelEncoder()
                self.df[variable] = encoder.fit_transform(self.df[variable].astype(str))

                if variable in self.cat_features: self.cat_features.remove(variable)
                if variable not in self.num_features: self.num_features.append(variable)

                print(f"Label Encoding aplicado a {variable}")

            # Método 2: One-Hot Encoding (codificación ordinal simple).
            elif method =="one-hot encoding":

                encoder = OneHotEncoder(drop="first", sparse_output=False)
                encoded = encoder.fit_transform(self.df[variable].astype(str))
                encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out([variable]),index=self.df.index)
                self.df = pd.concat([self.df.drop(columns=[variable]), encoded_df], axis=1)

                if variable in self.cat_features:
                    self.cat_features.remove(variable)
                self.num_features.extend(encoded_df.columns.tolist())
                
                print(f"One-Hot Encoding aplicado a '{variable}'.")

            # Método 3: Binary Encoding (codificación ordinal simple).
            elif method =="binary encoding":
                # Guardamos las columnas antes para informar del cambio
                cols_before = self.df.columns.tolist()
                encoder = ce.BinaryEncoder(cols=[variable])
                self.df = encoder.fit_transform(self.df)

                new_cols = list(set(self.df.columns) - set(cols_before))
                if variable in self.cat_features: self.cat_features.remove(variable)
                self.num_features.extend(new_cols)
                
                print(f"Binary Encoding aplicado a '{variable}'. Creadas {len(new_cols)} columnas.")

            # Método 4: Target(mean) Encoding (codificación ordinal simple).
            elif method =="target encoding":

                if self.target_col not in self.df.columns:
                    print(f"ERROR: Target '{self.target_col}' no encontrado para Target Encoding.")
                    return
                
                # Calcula el promedio del target por categoría
                target_mean = self.df.groupby(variable)[self.target_col].mean()

                # Mapea los valores de la columna al promedio correspondiente
                self.df[variable] = self.df[variable].map(target_mean)

                # Robustez: Si hay categorías nuevas o nulas, llenar con la media global
                self.df[variable].fillna(self.df[self.target_col].mean(), inplace=True)

                if variable in self.cat_features:
                    self.cat_features.remove(variable)
                if variable not in self.num_features:
                    self.num_features.append(variable)

                print(f"Target(mean) Encoding aplicado a '{variable}'.")

            # Método 5: Rare Label Encoding (codificación ordinal simple).
            elif method =="rare label encoding":
                # Calculamos la frecuencia relativa de cada categoría
                freq = self.df[variable].value_counts(normalize=True)

                # Seleccionamos las categorías frecuentes (las que superan el umbral)
                categorias_frecuentes = list(freq[freq > 0.05].index)
                self.df[variable] = np.where(self.df[variable].isin(categorias_frecuentes), self.df[variable], "Rare")

                print(f"Rare Label Encoding aplicado a '{variable}': categorías < 5% agrupadas.")

            # Método 6: Frequency Encoding (Codificación por frecuencia o frecuencia relativa)
            elif method =="frequency encoding":
                self.df[variable] = self.df[variable].map(self.df[variable].value_counts())

                # Robustez: Llenar posibles nulos con 0 (frecuencia no encontrada)
                self.df[variable].fillna(0, inplace=True)

                if variable in self.cat_features:
                    self.cat_features.remove(variable)
                if variable not in self.num_features:
                    self.num_features.append(variable)

                print(f"Frequency Encoding aplicado a '{variable}'.")

            else:
                print(f"MÉTODO NO RECONOCIDO: '{method}'.")

        except Exception as e:
            print(f"FALLO CRÍTICO al aplicar {method} en '{variable}': {e}")


    def final_cleanup(self):
        """
        Responsabilidad: Pulido estético e integridad final.
        Ejecutar antes de finalize_and_split para verificar el DF limpio.
        """
        if self.df is None:
            print("ERROR: No hay datos para limpiar.")
            return

        # 1. Homogeneización de nombres de columnas (minúsculas y sin espacios)
        self.df.columns = self.df.columns.str.lower().str.replace(" ", "_")
        
        # IMPORTANTE: Sincronizar el nombre de la variable target_col con el nuevo formato
        # para que los métodos posteriores (como el split) no den error.
        self.target_col = self.target_col.lower().replace(" ", "_")

        # 2. Comprobación final de integridad
        nulos_totales = self.df.isnull().sum().sum()
        duplicados_totales = self.df.duplicated().sum()

        print(f"Total de valores nulos: {nulos_totales}")
        print(f"Total de filas duplicadas: {duplicados_totales}")
        print(f"Columnas normalizadas: {self.df.columns.tolist()[:5]}... (total {len(self.df.columns)})")
    
    def finalize_and_split(self, problem_type="classification"):
        """
        Responsabilidad: Partición definitiva de los datos para el modelo.
        """
        if self.df is None:
            print("ERROR: No hay datos para particionar.")
            return
        
        self.X = self.df.drop(columns=[self.target_col])
        self.y = self.df[self.target_col]

        stratify_param = self.y if problem_type == "classification" else None

        print(f"Separación completada.")
        print(f"X (Features): {self.X.shape} | y (Target): {self.y.shape}")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2,stratify=stratify_param, random_state=42)
        print("Tamaño del conjunto de entrenamiento:", self.X_train.shape)
        print("Tamaño del conjunto de prueba:", self.X_test.shape)

    
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

        results_df = pd.DataFrame(self.results).T

        print("=" * 80)
        print("RESUMEN FINAL DE RESULTADOS:")
        display(results_df)

        return results_df

