from autots import AutoTS
import pandas as pd

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


    forecast_length = kwargs["forecast_length"]
    predictions_file = kwargs["predictions_file"]
    history_file = kwargs["history_file"]
    train_data = data.set_index("time")

    model = AutoTS(
        forecast_length=forecast_length,
        frequency='D',
        prediction_interval=0.9,
        ensemble='auto',
        model_list="fast_parallel",  # "superfast", "default", "fast_parallel"
        transformer_list="fast",  # "superfast",
        drop_most_recent=0,
        max_generations=3,
        num_validations=2,
        validation_method="backwards",
        no_negatives=True,
        verbose=0
    )
    model = model.fit(
        train_data,
    )

    forecast = model.predict().forecast

    train_data.to_csv(history_file)
    forecast.to_csv(predictions_file)

    pd.concat([train_data, forecast], axis=0).plot()