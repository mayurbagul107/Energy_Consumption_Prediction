"""
data_processing.py
Handles data loading, validation, feature extraction, and preparation for EnergyWise.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any

NUMERIC_FEATURES = ['Temperature', 'Humidity', 'SquareFootage', 'Occupancy', 'RenewableEnergy']
CATEGORICAL_FEATURES = ['HVACUsage', 'LightingUsage', 'DayOfWeek', 'Holiday']
TARGET_COLUMN = 'EnergyConsumption'
ALL_CORE_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DEFAULT_DATASET_PATHS = [
    os.path.join(DATA_DIR, 'Energy_Consumption_Virtual.csv'),
    os.path.join(os.path.dirname(DATA_DIR), 'Energy_Consumption_Virtual.csv'),
    os.path.join(DATA_DIR, 'Energy_Consumption_30000_Augmented.csv'),
]


def find_default_dataset() -> Optional[str]:
    """Finds the path to the primary available dataset."""
    for path in DEFAULT_DATASET_PATHS:
        if os.path.exists(path):
            return path
    return None


def get_available_datasets() -> Dict[str, str]:
    """Returns a dictionary of human-readable dataset names and paths."""
    datasets = {}
    for path in DEFAULT_DATASET_PATHS:
        if os.path.exists(path):
            filename = os.path.basename(path)
            datasets[filename] = path
    return datasets


def load_dataset(file_or_path, is_synthetic_filter: Optional[str] = 'All') -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads dataset from a filepath or file-like buffer (e.g. Streamlit UploadedFile).
    Applies standard type conversions, validates columns, and extracts timestamp features.
    
    Returns:
        df: Loaded and preprocessed DataFrame
        metadata: Dict containing summary metrics and inspection results
    """
    if hasattr(file_or_path, 'read'):
        df = pd.read_csv(file_or_path)
        source_name = getattr(file_or_path, 'name', 'Uploaded File')
    elif isinstance(file_or_path, str) and os.path.exists(file_or_path):
        df = pd.read_csv(file_or_path)
        source_name = os.path.basename(file_or_path)
    else:
        raise FileNotFoundError(f"Dataset path not found: {file_or_path}")

    raw_shape = df.shape
    raw_duplicates = int(df.duplicated().sum())

    # Check for index column or synthetic column
    has_synthetic_col = 'IsSynthetic' in df.columns
    synthetic_counts = df['IsSynthetic'].value_counts().to_dict() if has_synthetic_col else {}

    # If synthetic filter is requested and column is present
    if has_synthetic_col and is_synthetic_filter == 'Real Only':
        df = df[df['IsSynthetic'] == 0].copy()
    elif has_synthetic_col and is_synthetic_filter == 'Synthetic Only':
        df = df[df['IsSynthetic'] == 1].copy()

    # Parse Timestamp if present
    if 'Timestamp' in df.columns:
        try:
            df['Datetime'] = pd.to_datetime(df['Timestamp'], format='mixed', dayfirst=True)
            if 'Hour' not in df.columns:
                df['Hour'] = df['Datetime'].dt.hour
            if 'Month' not in df.columns:
                df['Month'] = df['Datetime'].dt.month
            if 'Day' not in df.columns:
                df['Day'] = df['Datetime'].dt.day
            if 'DayOfWeek' not in df.columns:
                df['DayOfWeek'] = df['Datetime'].dt.day_name()
        except Exception:
            pass

    # Standardize string values in categoricals
    for cat_col in ['HVACUsage', 'LightingUsage', 'Holiday']:
        if cat_col in df.columns:
            df[cat_col] = df[cat_col].astype(str).str.strip().str.capitalize()

    if 'DayOfWeek' in df.columns:
        df['DayOfWeek'] = df['DayOfWeek'].astype(str).str.strip().str.capitalize()

    metadata = {
        'source_name': source_name,
        'raw_rows': raw_shape[0],
        'raw_cols': raw_shape[1],
        'current_rows': len(df),
        'current_cols': df.shape[1],
        'duplicates': raw_duplicates,
        'missing_values': int(df.isnull().sum().sum()),
        'missing_per_col': df.isnull().sum().to_dict(),
        'has_synthetic_col': has_synthetic_col,
        'synthetic_counts': synthetic_counts,
        'columns': list(df.columns),
        'has_target': TARGET_COLUMN in df.columns,
    }

    return df, metadata


def prepare_features_and_target(
    df: pd.DataFrame, 
    include_engineered: bool = False
) -> Tuple[pd.DataFrame, pd.Series, list, list]:
    """
    Extracts numerical and categorical features and target variable.
    
    Returns:
        X: Feature DataFrame
        y: Target Series
        num_features: List of numerical column names
        cat_features: List of categorical column names
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target variable '{TARGET_COLUMN}' is missing from the dataset.")

    num_features = [col for col in NUMERIC_FEATURES if col in df.columns]
    if include_engineered and 'Hour' in df.columns:
        num_features.append('Hour')

    cat_features = [col for col in CATEGORICAL_FEATURES if col in df.columns]

    available_cols = num_features + cat_features
    X = df[available_cols].copy()
    y = df[TARGET_COLUMN].copy()

    # Impute missing values if any
    for col in num_features:
        if X[col].isnull().any():
            X[col] = X[col].fillna(X[col].median())
    for col in cat_features:
        if X[col].isnull().any():
            X[col] = X[col].fillna(X[col].mode()[0])

    return X, y, num_features, cat_features
