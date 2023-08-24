import os
import json

from autots import AutoTS
import pandas as pd
import mlflow

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here
    append_path = lambda x: os.path.join(artifacts_path, x)
    get_df_value = lambda df, col: df[col].iloc[0]
    
    def save_json(path, obj):
        with open(path, "w") as f:
            json.dump(obj, f)

    train_data = data

    artifacts_path = kwargs['artifacts_path']
    forecast_length = kwargs["forecast_length"]

    history_file = append_path("history.csv")
    predictions_file = append_path("predictions.csv")
    model_template_file = append_path("model_template.json")
    best_model_params_file = append_path("best_model_params.json")
    transformation_params_file = append_path("transformation_params.json")
    score_per_series_file = append_path("score_per_series.json")
    first_time = False if os.path.exists(model_template_file) else True

    mlflow.set_experiment("Crypto Forecasting")

    with mlflow.start_run() as run:

        mlflow.log_param("first_time", first_time)

        auto_ts_params = {
            "forecast_length": forecast_length,
            "frequency": 'D',
            "prediction_interval": 0.9,
            "ensemble": 'auto',
            "model_list": "superfast",  # "fast", "superfast", "default", "fast_parallel"
            "transformer_list": "superfast",  # "fast", "superfast",
            "drop_most_recent": 0,
            "max_generations": 4,
            "num_validations": 2,
            "validation_method": "backwards",
            "no_negatives": True,
            "constraint": 2.0,
        }

        mlflow.log_params(auto_ts_params)
        mlflow.log_param("coins", list(train_data.columns))

        model = AutoTS(
            **(auto_ts_params | {"verbose":-1})        
        )

        if not first_time:
            model = model.import_template(model_template_file, method='add on')

        model = model.fit(
            train_data,
        )

        if first_time:
            model.export_template(model_template_file, models='best',
                        n=15, max_per_model_class=3)
        
        forecast = model.predict().forecast
        train_data.to_csv(history_file)
        forecast.to_csv(predictions_file)

        sps = model.score_per_series
        best_model = model.best_model
        best_model_params = model.best_model_params

        results = model.initial_results.model_results
        bm_id = get_df_value(best_model, "ID")
        res = results[results.ID == bm_id]

        transformation_params = json.loads(get_df_value(res, "TransformationParameters"))

        mlflow.log_metric("Score", get_df_value(res, "Score"))
        mlflow.log_metric("TotalRuntimeSeconds", get_df_value(res, "TotalRuntimeSeconds"))

        tags = {
            "ID": get_df_value(res, "ID"),
            "Model": get_df_value(res, "Model"),
            "Ensemble": get_df_value(res, "Ensemble"),
        }

        mlflow.set_tags(tags)

        series_models = best_model_params["series"]
        score_per_series = {
            col: sps.loc[id, col]
            for col, id in series_models.items()
        }

        save_json(best_model_params_file, best_model_params)
        save_json(transformation_params_file, transformation_params)
        save_json(score_per_series_file, score_per_series)

        mlflow.log_artifacts(artifacts_path)