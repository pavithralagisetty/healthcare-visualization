import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def load_data(file_path):
    """Load the dataset from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

def preprocess_data(data):
    """Preprocess the data with enhanced steps."""
    if data is None:
        return None, None

    try:
        X = data.iloc[:, :-1]  # Features
        y = data.iloc[:, -1]   # Target variable

        # Create preprocessing pipeline
        preprocessing_pipeline = Pipeline([
            # Handle missing values with median for numerical data
            ('imputer', SimpleImputer(strategy='median')),
            
            # Remove outliers using IQR method
            ('outlier_handler', RobustScaler()),
            
            # Standard scaling of features
            ('scaler', StandardScaler())
        ])

        # Handle outliers using IQR method
        def remove_outliers(df):
            Q1 = df.quantile(0.25)
            Q3 = df.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return df[~((df < lower_bound) | (df > upper_bound)).any(axis=1)]

        # Remove outliers from features
        X_clean = remove_outliers(X)
        y_clean = y[X_clean.index]

        # Apply preprocessing pipeline
        X_processed = preprocessing_pipeline.fit_transform(X_clean)

        # Convert to DataFrame to maintain feature names
        X_processed = pd.DataFrame(X_processed, columns=X.columns, index=X_clean.index)

        # Add feature interactions
        X_processed['recency_frequency'] = X_processed['Recency (months)'] * X_processed['Frequency (times)']
        X_processed['monetary_time'] = X_processed['Monetary (c.c. blood)'] * X_processed['Time (months)']

        # Log transform highly skewed features
        skewed_features = ['Monetary (c.c. blood)', 'Time (months)']
        for feature in skewed_features:
            X_processed[f'{feature}_log'] = np.log1p(X_processed[feature])

        return X_processed, y_clean

    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return None, None

def train_model(X_train, y_train):
    """Train an enhanced logistic regression model."""
    if X_train is None or y_train is None:
        return None

    try:
        # Create model with balanced class weights and L2 regularization
        model = LogisticRegression(
            class_weight='balanced',
            C=1.0,
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
        
        model.fit(X_train, y_train)
        return model

    except Exception as e:
        print(f"Error in model training: {str(e)}")
        return None

def evaluate_model(model, X_test, y_test):
    """Evaluate the model with detailed metrics."""
    if model is None or X_test is None or y_test is None:
        return

    try:
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        print("\nModel Evaluation Metrics:")
        print("-" * 50)
        print(f'Accuracy: {accuracy_score(y_test, y_pred):.3f}')
        print("\nDetailed Classification Report:")
        print(classification_report(y_test, y_pred))

        # Feature importance
        if hasattr(model, 'coef_'):
            feature_importance = pd.DataFrame({
                'Feature': X_test.columns,
                'Importance': abs(model.coef_[0])
            })
            print("\nFeature Importance:")
            print(feature_importance.sort_values('Importance', ascending=False))

    except Exception as e:
        print(f"Error in model evaluation: {str(e)}")

def main():
    # Load the data
    data = load_data('transfusion.csv')
    if data is None:
        return

    # Preprocess the data
    X, y = preprocess_data(data)
    if X is None or y is None:
        return

    # Split the data with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )

    # Train the model
    model = train_model(X_train, y_train)
    if model is None:
        return

    # Evaluate the model
    evaluate_model(model, X_test, y_test)

if __name__ == "__main__":
    main()
