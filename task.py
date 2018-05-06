from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

import model

STEPS = 1000
train_path = "training_data.csv"
test_path = "test_data.csv"
batch_size = 128

def run_experiment():
	"""Run the training and evaluate."""
	tf.logging.set_verbosity(tf.logging.INFO)

	estimator = model.build_estimator()

	# Train the model.
	# By default, the Estimators log output every 100 steps.
	estimator.train(steps=STEPS, input_fn=lambda : model.csv_input_fn(train_path, batch_size) )

	# Evaluate how the model performs on data it has not yet seen.
	eval_result = estimator.evaluate(input_fn=lambda : model.eval_input_fn(test_path, batch_size))

	# The evaluation returns a Python dictionary. The "average_loss" key holds the
	# Mean Squared Error (MSE).
	average_loss = eval_result["average_loss"]

	print("Eval Result: " + str(eval_result))
	print("Mean Square Error = " + str(average_loss))

	# Run the model in prediction mode.
	input_dict = {
		"location_id": np.array([[1, 0, 0]]),
		"hour": np.array([8]),
		"minute": np.array([15]),
		"total_minutes": np.array([495])
	}
	predict_results = estimator.predict(input_fn=lambda : model.pred_input_fn(input_dict, batch_size))

	# Print the prediction results.
	print("\nPrediction results:")
	for i, prediction in enumerate(predict_results):
		print(str(input_dict["location_id"][i]) + " " + str(input_dict["hour"][i]) + ":" + str(input_dict["minute"][i]) + ". Wait time = " + str(prediction["predictions"][0]))

if __name__ == '__main__':
	run_experiment()