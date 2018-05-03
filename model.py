"""Linear regression using the LinearRegressor Estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

STEPS = 1000
PRICE_NORM_FACTOR = 1000

COLUMNS = ["location_id", "hour", "minute", "total_minutes", "wait_time"]
FIELD_DEFAULTS = [[0],[0.0],[0.0],[0.0],[0.0]]

def main(argv):
  """Builds, trains, and evaluates the model."""
  assert len(argv) == 1

  train_path = "training_data.csv"
  test_path = "test_data.csv"
  batch_size = 128
  # train = tf.data.TextLineDataset.__init__("training_data.csv").skip(1)
  #test = tf.data.TextLineDataset.__init__("test_data.csv").skip(1)

  def _parse_line(line):
    """Splits a csv line into pair (features, labels)"""
    fields = tf.decode_csv(line, FIELD_DEFAULTS)
    features = dict(zip(COLUMNS, fields))
    try:
      label = features.pop('wait_time')
      return features, label
    except KeyError:
      return features
    

  def csv_input_fn(csv_path, batch_size):
    """An input function for training"""
    # Convert csv input into Dataset
    dataset = tf.data.TextLineDataset(csv_path).skip(1)
    dataset = dataset.map(_parse_line)

    # Shuffle, repeat, and batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    return dataset

  def eval_input_fn(csv_path, batch_size):
    """An input function for evaluation"""
    # Convert csv input into Dataset
    dataset = tf.data.TextLineDataset(csv_path).skip(1)
    dataset = dataset.map(_parse_line)

    # Batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.batch(batch_size)

    return dataset

  def pred_input_fn(features, batch_size):
    """An input function for prediction - input is a dict not csv"""
    # Convert feature inputs into Dataset
    inputs = dict(features)
    print(inputs)
    dataset = tf.data.Dataset.from_tensor_slices(inputs)
    print(dataset)
    # Batch the examples
    assert batch_size is not None, "batch_size must not be None"
    dataset = dataset.batch(batch_size)
    return dataset

  feature_columns = [
      tf.feature_column.categorical_column_with_identity(key="location_id", num_buckets=3),
      tf.feature_column.numeric_column(key="hour"),
      tf.feature_column.numeric_column(key="minute"),
      tf.feature_column.numeric_column(key="total_minutes")
  ]

  # Build the Estimator.
  model = tf.estimator.LinearRegressor(feature_columns=feature_columns)

  # Train the model.
  # By default, the Estimators log output every 100 steps.
  model.train(steps=STEPS, input_fn=lambda : csv_input_fn(train_path, batch_size) )

  # Evaluate how the model performs on data it has not yet seen.
  eval_result = model.evaluate(input_fn=lambda : eval_input_fn(test_path, batch_size))

  # The evaluation returns a Python dictionary. The "average_loss" key holds the
  # Mean Squared Error (MSE).
  average_loss = eval_result["average_loss"]

  print("Eval Result: " + str(eval_result))
  print("Mean Square Error = " + str(average_loss))
  # Convert MSE to Root Mean Square Error (RMSE).
  # print("\n" + 80 * "*")
  # print("\nRMS error for the test set: ${:.0f}"
  #       .format(PRICE_NORM_FACTOR * average_loss**0.5))

  # Run the model in prediction mode.
  input_dict = {
      "location_id": np.array([[1, 0, 0]]),
      "hour": np.array([8]),
      "minute": np.array([15]),
      "total_minutes": np.array([495])
  }
  predict_results = model.predict(input_fn=lambda : pred_input_fn(input_dict, batch_size))

  # Print the prediction results.
  print("\nPrediction results:")
  for i, prediction in enumerate(predict_results):
    print(str(input_dict["location_id"][i]) + " " + str(input_dict["hour"][i]) + ":" + str(input_dict["minute"][i]) + ". Wait time = " + str(prediction["predictions"][0]))

if __name__ == "__main__":
  # The Estimator periodically generates "INFO" logs; make these logs visible.
  tf.logging.set_verbosity(tf.logging.INFO)
  tf.app.run(main=main)
