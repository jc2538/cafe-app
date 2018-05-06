"""Linear regression using the LinearRegressor Estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

STEPS = 1000

COLUMNS = ["location_id", "hour", "minute", "total_minutes", "wait_time"]
FIELD_DEFAULTS = [[0],[0.0],[0.0],[0.0],[0.0]]

feature_columns = [
    tf.feature_column.categorical_column_with_identity(key="location_id", num_buckets=3),
    tf.feature_column.numeric_column(key="hour"),
    tf.feature_column.numeric_column(key="minute"),
    tf.feature_column.numeric_column(key="total_minutes")
]
 
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

def build_estimator():
  # Build the Estimator.
  return tf.estimator.LinearRegressor(feature_columns=feature_columns)