---
name: ml-model-builder
description: "Build ML models for construction predictions. Train and evaluate custom models for cost, duration, and risk prediction."
---

# ML Model Builder

## Business Case

### Problem Statement
Construction prediction challenges:
- Complex relationships between variables
- Limited historical data utilization
- Need for multiple prediction targets
- Model validation and deployment

### Solution
Comprehensive ML model building framework for construction predictions with data preprocessing, model training, evaluation, and export capabilities.

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import math


class PredictionTarget(Enum):
    COST = "cost"
    DURATION = "duration"
    RISK_SCORE = "risk_score"
    PRODUCTIVITY = "productivity"
    QUALITY = "quality"


class AlgorithmType(Enum):
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    KNN = "knn"
    DECISION_TREE = "decision_tree"
    ENSEMBLE = "ensemble"


class FeatureType(Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATE = "date"


@dataclass
class Feature:
    name: str
    feature_type: FeatureType
    importance: float = 0.0
    categories: List[str] = field(default_factory=list)


@dataclass
class ModelMetrics:
    mae: float
    mape: float
    rmse: float
    r_squared: float
    samples: int


@dataclass
class TrainedModel:
    model_id: str
    target: PredictionTarget
    algorithm: AlgorithmType
    features: List[Feature]
    metrics: ModelMetrics
    coefficients: Dict[str, float]
    intercept: float
    trained_at: datetime
    training_samples: int


class MLModelBuilder:
    """Build and train ML models for construction predictions."""

    def __init__(self, project_name: str = "Construction ML"):
        self.project_name = project_name
        self.models: Dict[str, TrainedModel] = {}
        self.feature_stats: Dict[str, Dict[str, float]] = {}
        self.categorical_encodings: Dict[str, Dict[str, int]] = {}

    def prepare_data(self, df: pd.DataFrame,
                     target_column: str,
                     feature_columns: List[str],
                     test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray,
                                                       np.ndarray, np.ndarray]:
        """Prepare and split data for training."""

        # Handle missing values
        df = df.dropna(subset=[target_column] + feature_columns)

        # Encode categorical features
        X_processed = []

        for col in feature_columns:
            if df[col].dtype == 'object':
                # Categorical encoding
                if col not in self.categorical_encodings:
                    unique_vals = df[col].unique()
                    self.categorical_encodings[col] = {v: i for i, v in enumerate(unique_vals)}

                encoded = df[col].map(self.categorical_encodings[col]).fillna(0)
                X_processed.append(encoded.values)
            else:
                # Numeric - normalize
                values = df[col].values
                if col not in self.feature_stats:
                    self.feature_stats[col] = {
                        'mean': np.mean(values),
                        'std': np.std(values) or 1
                    }

                normalized = (values - self.feature_stats[col]['mean']) / self.feature_stats[col]['std']
                X_processed.append(normalized)

        X = np.column_stack(X_processed)
        y = df[target_column].values

        # Train-test split
        n = len(df)
        indices = np.random.permutation(n)
        test_n = int(n * test_size)

        test_indices = indices[:test_n]
        train_indices = indices[test_n:]

        X_train = X[train_indices]
        X_test = X[test_indices]
        y_train = y[train_indices]
        y_test = y[test_indices]

        return X_train, X_test, y_train, y_test

    def train_linear_regression(self, X: np.ndarray, y: np.ndarray,
                                regularization: float = 0.0) -> Tuple[np.ndarray, float]:
        """Train linear regression model."""

        # Add intercept
        X_with_intercept = np.column_stack([np.ones(len(X)), X])

        if regularization > 0:
            # Ridge regression
            n_features = X_with_intercept.shape[1]
            reg_matrix = regularization * np.eye(n_features)
            reg_matrix[0, 0] = 0  # Don't regularize intercept

            XtX = X_with_intercept.T @ X_with_intercept + reg_matrix
        else:
            XtX = X_with_intercept.T @ X_with_intercept

        try:
            XtX_inv = np.linalg.inv(XtX)
            beta = XtX_inv @ X_with_intercept.T @ y
        except np.linalg.LinAlgError:
            # Use pseudoinverse if singular
            beta = np.linalg.pinv(X_with_intercept) @ y

        return beta[1:], beta[0]

    def train_knn_model(self, X_train: np.ndarray, y_train: np.ndarray,
                        k: int = 5) -> Callable:
        """Create k-NN prediction function."""

        def predict(X_new: np.ndarray) -> np.ndarray:
            predictions = []
            for x in X_new:
                distances = np.sqrt(np.sum((X_train - x) ** 2, axis=1))
                nearest_indices = np.argsort(distances)[:k]
                nearest_values = y_train[nearest_indices]
                predictions.append(np.mean(nearest_values))
            return np.array(predictions)

        return predict

    def calculate_metrics(self, y_true: np.ndarray,
                          y_pred: np.ndarray) -> ModelMetrics:
        """Calculate model performance metrics."""

        residuals = y_true - y_pred
        mae = np.mean(np.abs(residuals))
        mape = np.mean(np.abs(residuals / (y_true + 1e-10))) * 100
        rmse = math.sqrt(np.mean(residuals ** 2))

        # R-squared
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r_squared = 1 - (ss_res / (ss_tot + 1e-10))

        return ModelMetrics(
            mae=round(mae, 2),
            mape=round(mape, 2),
            rmse=round(rmse, 2),
            r_squared=round(r_squared, 4),
            samples=len(y_true)
        )

    def build_model(self, df: pd.DataFrame,
                    target_column: str,
                    feature_columns: List[str],
                    target_type: PredictionTarget,
                    algorithm: AlgorithmType = AlgorithmType.LINEAR_REGRESSION,
                    model_id: str = None,
                    **kwargs) -> TrainedModel:
        """Build and train a prediction model."""

        model_id = model_id or f"{target_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(
            df, target_column, feature_columns,
            test_size=kwargs.get('test_size', 0.2)
        )

        # Train model based on algorithm
        if algorithm == AlgorithmType.LINEAR_REGRESSION:
            coefficients, intercept = self.train_linear_regression(X_train, y_train)
            y_pred = X_test @ coefficients + intercept

        elif algorithm == AlgorithmType.RIDGE_REGRESSION:
            coefficients, intercept = self.train_linear_regression(
                X_train, y_train,
                regularization=kwargs.get('alpha', 1.0)
            )
            y_pred = X_test @ coefficients + intercept

        elif algorithm == AlgorithmType.KNN:
            predict_fn = self.train_knn_model(
                X_train, y_train,
                k=kwargs.get('k', 5)
            )
            y_pred = predict_fn(X_test)
            coefficients = np.zeros(len(feature_columns))
            intercept = np.mean(y_train)

        else:
            # Default to linear
            coefficients, intercept = self.train_linear_regression(X_train, y_train)
            y_pred = X_test @ coefficients + intercept

        # Calculate metrics
        metrics = self.calculate_metrics(y_test, y_pred)

        # Calculate feature importance (based on coefficient magnitude)
        coef_abs = np.abs(coefficients)
        importance_sum = np.sum(coef_abs) or 1
        importances = coef_abs / importance_sum

        features = [
            Feature(
                name=col,
                feature_type=FeatureType.CATEGORICAL if col in self.categorical_encodings else FeatureType.NUMERIC,
                importance=round(float(importances[i]), 4),
                categories=list(self.categorical_encodings.get(col, {}).keys())
            )
            for i, col in enumerate(feature_columns)
        ]

        # Create model object
        model = TrainedModel(
            model_id=model_id,
            target=target_type,
            algorithm=algorithm,
            features=features,
            metrics=metrics,
            coefficients={col: float(coefficients[i]) for i, col in enumerate(feature_columns)},
            intercept=float(intercept),
            trained_at=datetime.now(),
            training_samples=len(X_train)
        )

        self.models[model_id] = model
        return model

    def predict(self, model_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using trained model."""

        if model_id not in self.models:
            return {'error': 'Model not found'}

        model = self.models[model_id]

        # Process features
        feature_values = []
        for feat in model.features:
            value = features.get(feat.name)

            if feat.feature_type == FeatureType.CATEGORICAL:
                encoded = self.categorical_encodings.get(feat.name, {}).get(value, 0)
                feature_values.append(encoded)
            else:
                # Normalize
                stats = self.feature_stats.get(feat.name, {'mean': 0, 'std': 1})
                normalized = (value - stats['mean']) / stats['std']
                feature_values.append(normalized)

        # Calculate prediction
        feature_array = np.array(feature_values)
        coef_array = np.array([model.coefficients[f.name] for f in model.features])

        prediction = float(np.dot(feature_array, coef_array) + model.intercept)

        return {
            'model_id': model_id,
            'prediction': round(prediction, 2),
            'model_metrics': {
                'mae': model.metrics.mae,
                'r_squared': model.metrics.r_squared
            },
            'feature_contributions': {
                f.name: round(feature_values[i] * model.coefficients[f.name], 2)
                for i, f in enumerate(model.features)
            }
        }

    def compare_models(self, model_ids: List[str] = None) -> pd.DataFrame:
        """Compare multiple models."""

        models = [self.models[m] for m in (model_ids or self.models.keys())]

        data = [{
            'Model ID': m.model_id,
            'Target': m.target.value,
            'Algorithm': m.algorithm.value,
            'MAE': m.metrics.mae,
            'MAPE %': m.metrics.mape,
            'RMSE': m.metrics.rmse,
            'R²': m.metrics.r_squared,
            'Training Samples': m.training_samples,
            'Features': len(m.features)
        } for m in models]

        return pd.DataFrame(data)

    def get_feature_importance(self, model_id: str) -> pd.DataFrame:
        """Get feature importance for a model."""

        if model_id not in self.models:
            return pd.DataFrame()

        model = self.models[model_id]

        data = [{
            'Feature': f.name,
            'Importance': f.importance,
            'Coefficient': model.coefficients.get(f.name, 0),
            'Type': f.feature_type.value
        } for f in sorted(model.features, key=lambda x: x.importance, reverse=True)]

        return pd.DataFrame(data)

    def export_model(self, model_id: str, output_path: str) -> str:
        """Export model to JSON."""

        if model_id not in self.models:
            return ""

        model = self.models[model_id]

        export_data = {
            'model_id': model.model_id,
            'target': model.target.value,
            'algorithm': model.algorithm.value,
            'trained_at': model.trained_at.isoformat(),
            'training_samples': model.training_samples,
            'metrics': {
                'mae': model.metrics.mae,
                'mape': model.metrics.mape,
                'rmse': model.metrics.rmse,
                'r_squared': model.metrics.r_squared
            },
            'coefficients': model.coefficients,
            'intercept': model.intercept,
            'features': [
                {
                    'name': f.name,
                    'type': f.feature_type.value,
                    'importance': f.importance
                }
                for f in model.features
            ],
            'preprocessing': {
                'feature_stats': self.feature_stats,
                'categorical_encodings': self.categorical_encodings
            }
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        return output_path

    def export_to_excel(self, output_path: str) -> str:
        """Export all models summary to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Model comparison
            comparison = self.compare_models()
            comparison.to_excel(writer, sheet_name='Model Comparison', index=False)

            # Feature importance for each model
            for model_id in self.models:
                importance = self.get_feature_importance(model_id)
                sheet_name = f"Features_{model_id}"[:31]
                importance.to_excel(writer, sheet_name=sheet_name, index=False)

        return output_path
```

## Quick Start

```python
import pandas as pd

# Create builder
builder = MLModelBuilder("Office Projects")

# Sample training data
df = pd.DataFrame([
    {'size_sf': 50000, 'floors': 10, 'complexity': 3, 'project_type': 'Office', 'duration': 365},
    {'size_sf': 75000, 'floors': 15, 'complexity': 4, 'project_type': 'Office', 'duration': 450},
    {'size_sf': 30000, 'floors': 5, 'complexity': 2, 'project_type': 'Office', 'duration': 280},
    {'size_sf': 100000, 'floors': 20, 'complexity': 5, 'project_type': 'Office', 'duration': 520},
    {'size_sf': 45000, 'floors': 8, 'complexity': 3, 'project_type': 'Office', 'duration': 340}
])

# Build model
model = builder.build_model(
    df,
    target_column='duration',
    feature_columns=['size_sf', 'floors', 'complexity'],
    target_type=PredictionTarget.DURATION,
    algorithm=AlgorithmType.LINEAR_REGRESSION,
    model_id='duration_model_v1'
)

print(f"R²: {model.metrics.r_squared}")
print(f"MAE: {model.metrics.mae} days")

# Make prediction
result = builder.predict('duration_model_v1', {
    'size_sf': 60000,
    'floors': 12,
    'complexity': 3
})
print(f"Predicted duration: {result['prediction']} days")
```

## Common Use Cases

### 1. Train Multiple Models
```python
# Linear regression
linear_model = builder.build_model(df, 'cost', features,
    PredictionTarget.COST, AlgorithmType.LINEAR_REGRESSION)

# Ridge regression
ridge_model = builder.build_model(df, 'cost', features,
    PredictionTarget.COST, AlgorithmType.RIDGE_REGRESSION, alpha=1.0)

# k-NN
knn_model = builder.build_model(df, 'cost', features,
    PredictionTarget.COST, AlgorithmType.KNN, k=5)

# Compare
comparison = builder.compare_models()
print(comparison)
```

### 2. Feature Importance
```python
importance = builder.get_feature_importance('duration_model_v1')
print(importance)
```

### 3. Export Model
```python
builder.export_model('duration_model_v1', 'model.json')
builder.export_to_excel('models_summary.xlsx')
```

## Resources
- **DDC Book**: Chapter 4.5 - Future: Predictions and Machine Learning
- **scikit-learn**: https://scikit-learn.org/
- **Website**: https://datadrivenconstruction.io
