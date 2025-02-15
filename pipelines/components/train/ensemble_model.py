import mlflow
import numpy as np


class EnsembleModel(mlflow.pyfunc.PythonModel):
    def __init__(self, models):
        self.models = models

    def predict(self, context, model_input, params=None):
        proba = np.zeros((len(model_input), self.models[0].n_classes_))
        for model in self.models:
            proba += model.predict_proba(
                model_input, num_iteration=model.best_iteration_
            )
        return proba / len(self.models)
