"""Linear regression using the LinearRegressor Estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import multiprocessing

import six
import numpy as np
import tensorflow as tf

STEPS = 1000

COLUMNS = ["location_id", "hour", "minute", "total_minutes", "wait_time"]
CSV_COLUMNS = ["location_id", "hour", "minute", "total_minutes", "wait_time"]
CSV_COLUMN_DEFAULTS = [[0],[0.0],[0.0],[0.0],[0.0]]
FIELD_DEFAULTS = [[0],[0.0],[0.0],[0.0],[0.0]]

feature_columns = [
    tf.feature_column.numeric_column(key="location_id"),
    tf.feature_column.numeric_column(key="hour"),
    tf.feature_column.numeric_column(key="minute"),
    tf.feature_column.numeric_column(key="total_minutes")
]

INPUT_COLUMNS = [
    tf.feature_column.numeric_column(key="location_id"),
    tf.feature_column.numeric_column(key="hour"),
    tf.feature_column.numeric_column(key="minute"),
    tf.feature_column.numeric_column(key="total_minutes")
]

UNUSED_COLUMNS = set(CSV_COLUMNS) - {col.name for col in feature_columns} - \
    {"wait_time"}

# def parse_label_column(label_string_tensor):
#   """Parses a string tensor into the label tensor
#   Args:
#     label_string_tensor: Tensor of dtype string. Result of parsing the
#     CSV column specified by LABEL_COLUMN
#   Returns:
#     A Tensor of the same shape as label_string_tensor, should return
#     an int64 Tensor representing the label index for classification tasks,
#     and a float32 Tensor representing the value for a regression task.
#   """
#   # Build a Hash Table inside the graph
#   table = tf.contrib.lookup.index_table_from_tensor(tf.constant(LABELS))

#   # Use the hash table to convert string labels to ints and one-hot encode
#   return table.lookup(label_string_tensor)
 
# def _parse_line(line):
#   """Splits a csv line into pair (features, labels)"""
#   fields = tf.decode_csv(line, FIELD_DEFAULTS)
#   features = dict(zip(COLUMNS, fields))
#   try:
#     label = features.pop('wait_time')
#     return features, label
#   except KeyError:
#     return features

#Added from EX code

def csv_serving_input_fn():
  """Build the serving inputs."""
  csv_row = tf.placeholder(
      shape=[None],
      dtype=tf.string
  )
  features = parse_csv(csv_row)
  features.pop(LABEL_COLUMN)
  return tf.estimator.export.ServingInputReceiver(features, {'csv_row': csv_row})


def example_serving_input_fn():
  """Build the serving inputs."""
  example_bytestring = tf.placeholder(
      shape=[None],
      dtype=tf.string,
  )
  feature_scalars = tf.parse_example(
      example_bytestring,
      tf.feature_column.make_parse_example_spec(feature_columns)
  )
  return tf.estimator.export.ServingInputReceiver(
      features,
      {'example_proto': example_bytestring}
  )

# [START serving-function]
def json_serving_input_fn():
  """Build the serving inputs."""
  inputs = {}
  for feat in INPUT_COLUMNS:
    inputs[feat.name] = tf.placeholder(shape=[None], dtype=feat.dtype)
    
  return tf.estimator.export.ServingInputReceiver(inputs, inputs)
# [END serving-function]

SERVING_FUNCTIONS = {
    'JSON': json_serving_input_fn,
    'EXAMPLE': example_serving_input_fn,
    'CSV': csv_serving_input_fn
}

def parse_csv(rows_string_tensor):
  """Takes the string input tensor and returns a dict of rank-2 tensors."""

  # Takes a rank-1 tensor and converts it into rank-2 tensor
  # Example if the data is ['csv,line,1', 'csv,line,2', ..] to
  # [['csv,line,1'], ['csv,line,2']] which after parsing will result in a
  # tuple of tensors: [['csv'], ['csv']], [['line'], ['line']], [[1], [2]]
  row_columns = tf.expand_dims(rows_string_tensor, -1)
  columns = tf.decode_csv(row_columns, record_defaults=CSV_COLUMN_DEFAULTS)
  features = dict(zip(CSV_COLUMNS, columns))

  # Remove unused columns
  for col in UNUSED_COLUMNS:
    features.pop(col)
  return features


def input_fn(filenames,
                      num_epochs=None,
                      shuffle=True,
                      skip_header_lines=1,
                      batch_size=200):
  """Generates features and labels for training or evaluation.
  This uses the input pipeline based approach using file name queue
  to read data so that entire data is not loaded in memory.

  Args:
      filenames: [str] list of CSV files to read data from.
      num_epochs: int how many times through to read the data.
        If None will loop through data indefinitely
      shuffle: bool, whether or not to randomize the order of data.
        Controls randomization of both file order and line order within
        files.
      skip_header_lines: int set to non-zero in order to skip header lines
        in CSV files.
      batch_size: int First dimension size of the Tensors returned by
        input_fn
  Returns:
      A (features, indices) tuple where features is a dictionary of
        Tensors, and indices is a single Tensor of label indices.
  """
  filename_dataset = tf.data.Dataset.from_tensor_slices(filenames)
  if shuffle:
    # Process the files in a random order.
    filename_dataset = filename_dataset.shuffle(len(filenames))
    
  # For each filename, parse it into one element per line, and skip the header
  # if necessary.
  dataset = filename_dataset.flat_map(
      lambda filename: tf.data.TextLineDataset(filename).skip(skip_header_lines))
  
  dataset = dataset.map(parse_csv)
  if shuffle:
    dataset = dataset.shuffle(buffer_size=batch_size * 10)
  dataset = dataset.repeat(num_epochs)
  dataset = dataset.batch(batch_size)
  iterator = dataset.make_one_shot_iterator()
  features = iterator.get_next()
  try:
    label = features.pop('wait_time')
    return features, label
  except KeyError:
    return features
    
#added from EX code

# def csv_input_fn(csv_path, batch_size):
#   """An input function for training"""
#   # Convert csv input into Dataset
#   dataset = tf.data.TextLineDataset(csv_path).skip(1)
#   dataset = dataset.map(_parse_line)

#   # Shuffle, repeat, and batch the examples
#   assert batch_size is not None, "batch_size must not be None"
#   dataset = dataset.shuffle(1000).repeat().batch(batch_size)

#   return dataset

# def eval_input_fn(csv_path, batch_size):
#   """An input function for evaluation"""
#   # Convert csv input into Dataset
#   dataset = tf.data.TextLineDataset(csv_path).skip(1)
#   dataset = dataset.map(_parse_line)

#   # Batch the examples
#   assert batch_size is not None, "batch_size must not be None"
#   dataset = dataset.batch(batch_size)

#   return dataset

# def pred_input_fn(features, batch_size):
#   """An input function for prediction - input is a dict not csv"""
#   # Convert feature inputs into Dataset
#   inputs = dict(features)
#   print(inputs)
#   dataset = tf.data.Dataset.from_tensor_slices(inputs)
#   print(dataset)
#   # Batch the examples
#   assert batch_size is not None, "batch_size must not be None"
#   dataset = dataset.batch(batch_size)
#   return dataset

def build_estimator(config):
  # Build the Estimator.
  return tf.estimator.LinearRegressor(feature_columns=feature_columns, config=config)