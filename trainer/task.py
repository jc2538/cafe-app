# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function

# import argparse
# import os

# import numpy as np
# import tensorflow as tf

# import trainer.model as model

# from tensorflow.contrib.learn.python.learn.utils import (
#     saved_model_export_utils)
# from tensorflow.contrib.training.python.training import hparam

# STEPS = 1000
# # train_path = "training_data.csv"
# # test_path = "test_data.csv"
# batch_size = 128

# def run_experiment(hparams):
# 	"""Run the training and evaluate."""
# 	tf.logging.set_verbosity(tf.logging.INFO)

# 	estimator = model.build_estimator()

# 	train_input = lambda: model.input_fn(
# 	  hparams.train_files,
# 	  num_epochs=hparams.num_epochs,
# 	  batch_size=hparams.train_batch_size
# 	)

# 	# Don't shuffle evaluation data
# 	eval_input = lambda: model.input_fn(
# 	  hparams.eval_files,
# 	  batch_size=hparams.eval_batch_size,
# 	  shuffle=False
# 	)

# 	# Train the model.
# 	# By default, the Estimators log output every 100 steps.
# 	estimator.train(input_fn=train_input, max_steps=hparams.train_steps )

# 	# Evaluate how the model performs on data it has not yet seen.
# 	eval_result = estimator.evaluate(input_fn=eval_input, steps=hparams.eval_steps,)

# 	# The evaluation returns a Python dictionary. The "average_loss" key holds the
# 	# Mean Squared Error (MSE).
# 	average_loss = eval_result["average_loss"]

# 	print("Eval Result: " + str(eval_result))
# 	print("Mean Square Error = " + str(average_loss))

# 	# Run the model in prediction mode.
# 	input_dict = {
# 		"location_id": np.array([[1, 0, 0]]),
# 		"hour": np.array([8]),
# 		"minute": np.array([15]),
# 		"total_minutes": np.array([495])
# 	}
# 	predict_results = estimator.predict(input_fn=lambda : model.pred_input_fn(input_dict, batch_size))

# 	# Print the prediction results.
# 	print("\nPrediction results:")
# 	for i, prediction in enumerate(predict_results):
# 		print(str(input_dict["location_id"][i]) + " " + str(input_dict["hour"][i]) + ":" + str(input_dict["minute"][i]) + ". Wait time = " + str(prediction["predictions"][0]))

# if __name__ == '__main__':
# 	# run_experiment()
# 	parser = argparse.ArgumentParser()
# 	# Input Arguments
# 	parser.add_argument(
# 	  '--train-files',
# 	  help='GCS or local paths to training data',
# 	  nargs='+',
# 	  required=True
# 	)
# 	parser.add_argument(
# 	  '--num-epochs',
# 	  help="""\
# 	  Maximum number of training data epochs on which to train.
# 	  If both --max-steps and --num-epochs are specified,
# 	  the training job will run for --max-steps or --num-epochs,
# 	  whichever occurs first. If unspecified will run for --max-steps.\
# 	  """,
# 	  type=int,
# 	)
# 	parser.add_argument(
# 	  '--train-batch-size',
# 	  help='Batch size for training steps',
# 	  type=int,
# 	  default=40
# 	)
# 	parser.add_argument(
# 	  '--eval-batch-size',
# 	  help='Batch size for evaluation steps',
# 	  type=int,
# 	  default=40
# 	)
# 	parser.add_argument(
# 	  '--eval-files',
# 	  help='GCS or local paths to evaluation data',
# 	  nargs='+',
# 	  required=True
# 	)
# 	# Training arguments
# 	parser.add_argument(
# 	  '--embedding-size',
# 	  help='Number of embedding dimensions for categorical columns',
# 	  default=8,
# 	  type=int
# 	)
# 	parser.add_argument(
# 	  '--first-layer-size',
# 	  help='Number of nodes in the first layer of the DNN',
# 	  default=100,
# 	  type=int
# 	)
# 	parser.add_argument(
# 	  '--num-layers',
# 	  help='Number of layers in the DNN',
# 	  default=4,
# 	  type=int
# 	)
# 	parser.add_argument(
# 	  '--scale-factor',
# 	  help='How quickly should the size of the layers in the DNN decay',
# 	  default=0.7,
# 	  type=float
# 	)
# 	parser.add_argument(
# 	  '--job-dir',
# 	  help='GCS location to write checkpoints and export models',
# 	  required=True
# 	)

# 	# Argument to turn on all logging
# 	parser.add_argument(
# 	  '--verbosity',
# 	  choices=[
# 	      'DEBUG',
# 	      'ERROR',
# 	      'FATAL',
# 	      'INFO',
# 	      'WARN'
# 	  ],
# 	  default='INFO',
# 	)
# 	# Experiment arguments
# 	parser.add_argument(
# 	  '--train-steps',
# 	  help="""\
# 	  Steps to run the training job for. If --num-epochs is not specified,
# 	  this must be. Otherwise the training job will run indefinitely.\
# 	  """,
# 	  type=int
# 	)
# 	parser.add_argument(
# 	  '--eval-steps',
# 	  help='Number of steps to run evalution for at each checkpoint',
# 	  default=100,
# 	  type=int
# 	)
# 	parser.add_argument(
# 	  '--export-format',
# 	  help='The input format of the exported SavedModel binary',
# 	  choices=['JSON', 'CSV', 'EXAMPLE'],
# 	  default='JSON'
# 	)

# 	args = parser.parse_args()

# 	# Set python level verbosity
# 	tf.logging.set_verbosity(args.verbosity)
# 	# Set C++ Graph Execution level verbosity
# 	os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(
# 	  tf.logging.__dict__[args.verbosity] / 10)

# 	# Run the training job
# 	hparams=hparam.HParams(**args.__dict__)
# 	run_experiment(hparams)
import argparse
import os

import trainer.model as model

import tensorflow as tf
from tensorflow.contrib.learn.python.learn.utils import (
    saved_model_export_utils)
from tensorflow.contrib.training.python.training import hparam


def run_experiment(hparams):
  """Run the training and evaluate using the high level API"""

  train_input = lambda: model.input_fn(
      hparams.train_files,
      num_epochs=hparams.num_epochs,
      batch_size=hparams.train_batch_size
  )

  # Don't shuffle evaluation data
  eval_input = lambda: model.input_fn(
      hparams.eval_files,
      batch_size=hparams.eval_batch_size,
      shuffle=False
  )

  train_spec = tf.estimator.TrainSpec(train_input,
                                      max_steps=hparams.train_steps
                                      )

  exporter = tf.estimator.FinalExporter('cafe-app',
          model.SERVING_FUNCTIONS[hparams.export_format])
  eval_spec = tf.estimator.EvalSpec(eval_input,
                                    steps=hparams.eval_steps,
                                    exporters=[exporter],
                                    name='cafe-app-eval'
                                    )

  run_config = tf.estimator.RunConfig()
  run_config = run_config.replace(model_dir=hparams.job_dir)
  print('model dir {}'.format(run_config.model_dir))
  estimator = model.build_estimator(config=run_config)

  tf.estimator.train_and_evaluate(estimator,
                                  train_spec,
                                  eval_spec)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  # Input Arguments
  parser.add_argument(
      '--train-files',
      help='GCS or local paths to training data',
      nargs='+',
      required=True
  )
  parser.add_argument(
      '--num-epochs',
      help="""\
      Maximum number of training data epochs on which to train.
      If both --max-steps and --num-epochs are specified,
      the training job will run for --max-steps or --num-epochs,
      whichever occurs first. If unspecified will run for --max-steps.\
      """,
      type=int,
  )
  parser.add_argument(
      '--train-batch-size',
      help='Batch size for training steps',
      type=int,
      default=40
  )
  parser.add_argument(
      '--eval-batch-size',
      help='Batch size for evaluation steps',
      type=int,
      default=40
  )
  parser.add_argument(
      '--eval-files',
      help='GCS or local paths to evaluation data',
      nargs='+',
      required=True
  )
  # Training arguments
  parser.add_argument(
      '--embedding-size',
      help='Number of embedding dimensions for categorical columns',
      default=8,
      type=int
  )
  parser.add_argument(
      '--first-layer-size',
      help='Number of nodes in the first layer of the DNN',
      default=100,
      type=int
  )
  parser.add_argument(
      '--num-layers',
      help='Number of layers in the DNN',
      default=4,
      type=int
  )
  parser.add_argument(
      '--scale-factor',
      help='How quickly should the size of the layers in the DNN decay',
      default=0.7,
      type=float
  )
  parser.add_argument(
      '--job-dir',
      help='GCS location to write checkpoints and export models',
      required=True
  )

  # Argument to turn on all logging
  parser.add_argument(
      '--verbosity',
      choices=[
          'DEBUG',
          'ERROR',
          'FATAL',
          'INFO',
          'WARN'
      ],
      default='INFO',
  )
  # Experiment arguments
  parser.add_argument(
      '--train-steps',
      help="""\
      Steps to run the training job for. If --num-epochs is not specified,
      this must be. Otherwise the training job will run indefinitely.\
      """,
      type=int
  )
  parser.add_argument(
      '--eval-steps',
      help='Number of steps to run evalution for at each checkpoint',
      default=100,
      type=int
  )
  parser.add_argument(
      '--export-format',
      help='The input format of the exported SavedModel binary',
      choices=['JSON', 'CSV', 'EXAMPLE'],
      default='JSON'
  )

  args = parser.parse_args()

  # Set python level verbosity
  tf.logging.set_verbosity(args.verbosity)
  # Set C++ Graph Execution level verbosity
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(
      tf.logging.__dict__[args.verbosity] / 10)

  # Run the training job
  hparams=hparam.HParams(**args.__dict__)
  run_experiment(hparams)
