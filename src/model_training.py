"""
model_training.py
Handles training, evaluation, comparison, and persistence of machine learning models for EnergyWise.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
BEST_MODEL_PATH = os.path.join(MODELS_DIR, 'best_energy_model.joblib')
ALL_MODELS_PATH = os.path.join(MODELS_DIR, 'all_models_summary.joblib')


def build_preprocessor(num_cols: list, cat_cols: list) -> ColumnTransformer:
    """Builds a scikit-learn ColumnTransformer for scaling and one-hot encoding."""
    return ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False), cat_cols)
        ]
    )


def train_and_evaluate_all_models(
    X: pd.DataFrame,
    y: pd.Series,
    num_cols: list,
    cat_cols: list,
    test_size: float = 0.2,
    random_state: int = 42,
    quick_svr: bool = True
) -> Dict[str, Any]:
    """
    Splits data into train and test sets, fits four models (LR, RF, GBR, SVR),
    computes genuine evaluation metrics (R2, MAE, MSE, RMSE), extracts feature importances,
    and identifies the best performing model.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    models_config = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=random_state, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=random_state),
        'Linear Regression': LinearRegression(),
        'Support Vector Regressor': SVR(kernel='rbf', C=10.0)
    }

    results = {}
    best_model_name = None
    best_r2 = -float('inf')

    # Fit preprocessor on X_train to avoid data leakage
    preprocessor = build_preprocessor(num_cols, cat_cols)
    preprocessor.fit(X_train)

    # Extract transformed feature names
    cat_encoder = preprocessor.named_transformers_['cat']
    encoded_cat_names = cat_encoder.get_feature_names_out(cat_cols).tolist()
    all_feature_names = num_cols + encoded_cat_names

    for name, regressor in models_config.items():
        pipe = Pipeline([
            ('prep', preprocessor),
            ('model', regressor)
        ])

        # Train model
        if name == 'Support Vector Regressor' and quick_svr and len(X_train) > 6000:
            # SVR has O(n^3) complexity; fit on representative 6,000 samples for high performance
            sample_idx = np.random.RandomState(random_state).choice(len(X_train), size=6000, replace=False)
            pipe.fit(X_train.iloc[sample_idx], y_train.iloc[sample_idx])
        else:
            pipe.fit(X_train, y_train)

        # Predict on test set
        y_pred = pipe.predict(X_test)

        # Evaluation metrics
        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))
        mse = float(mean_squared_error(y_test, y_pred))
        rmse = float(np.sqrt(mse))

        # Residuals
        residuals = y_test.values - y_pred

        # Feature importances if available
        feature_importances = {}
        if hasattr(regressor, 'feature_importances_'):
            fi = regressor.feature_importances_
            if len(fi) == len(all_feature_names):
                for f_name, imp in zip(all_feature_names, fi):
                    feature_importances[f_name] = float(imp)
        elif hasattr(regressor, 'coef_'):
            coefs = np.abs(regressor.coef_)
            if len(coefs) == len(all_feature_names):
                for f_name, imp in zip(all_feature_names, coefs):
                    feature_importances[f_name] = float(imp)

        # Sort feature importances
        sorted_fi = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

        results[name] = {
            'model_pipeline': pipe,
            'r2': r2,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'y_test_sample': y_test.values[:1000].tolist(),
            'y_pred_sample': y_pred[:1000].tolist(),
            'residuals_sample': residuals[:1000].tolist(),
            'feature_importances': sorted_fi
        }

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name

    summary = {
        'results': results,
        'best_model_name': best_model_name,
        'best_r2': best_r2,
        'feature_names': all_feature_names,
        'num_cols': num_cols,
        'cat_cols': cat_cols,
        'train_samples': len(X_train),
        'test_samples': len(X_test)
    }

    return summary


def save_models(summary: Dict[str, Any], dir_path: Optional[str] = None):
    """Saves best model and full model summary to disk."""
    target_dir = dir_path or MODELS_DIR
    os.makedirs(target_dir, exist_ok=True)

    best_name = summary['best_model_name']
    best_pipe = summary['results'][best_name]['model_pipeline']

    best_path = os.path.join(target_dir, 'best_energy_model.joblib')
    joblib.dump(best_pipe, best_path)

    all_path = os.path.join(target_dir, 'all_models_summary.joblib')
    joblib.dump(summary, all_path)
    return best_path, all_path


def load_saved_summary(dir_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Loads previously saved models summary if it exists."""
    target_dir = dir_path or MODELS_DIR
    all_path = os.path.join(target_dir, 'all_models_summary.joblib')
    if os.path.exists(all_path):
        try:
            return joblib.load(all_path)
        except Exception:
            return None
    return None


def load_best_model(dir_path: Optional[str] = None) -> Optional[Pipeline]:
    """Loads previously saved best model pipeline."""
    target_dir = dir_path or MODELS_DIR
    best_path = os.path.join(target_dir, 'best_energy_model.joblib')
    if os.path.exists(best_path):
        try:
            return joblib.load(best_path)
        except Exception:
            return None
    return None
