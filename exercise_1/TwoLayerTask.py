import sys
sys.path.append('../../')
import TaskPlan
from exercise_code.data_utils import load_CIFAR10
import numpy as np
from exercise_code.classifiers.neural_net import TwoLayerNet
import tensorflow as tf
import pickle

class TwoLayerTask(TaskPlan.Task):

    def __init__(self, preset, preset_pipe, logger, subtask):
        super().__init__(preset, preset_pipe, logger, subtask)
        input_size = 32 * 32 * 3
        hidden_size = self.preset.get_int('hidden_size')
        num_classes = 10
        self.net = TwoLayerNet(input_size, hidden_size, num_classes)

        X, y = load_CIFAR10('datasets/')
        # Split the data into train, val, and test sets. In addition we will
        # create a small development set as a subset of the data set;
        # we can use this for development so our code runs faster.
        num_training = 48000
        num_validation = 1000
        num_test = 1000

        assert (num_training + num_validation + num_test) == 50000, 'You have not provided a valid data split.'

        # Our training set will be the first num_train points from the original
        # training set.
        mask = range(num_training)
        self.X_train = X[mask]
        self.y_train = y[mask]

        # Our validation set will be num_validation points from the original
        # training set.
        mask = range(num_training, num_training + num_validation)
        self.X_val = X[mask]
        self.y_val = y[mask]

        # We use a small subset of the training set as our test set.
        mask = range(num_training + num_validation, num_training + num_validation + num_test)
        self.X_test = X[mask]
        self.y_test = y[mask]

        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], -1))
        self.X_val = np.reshape(self.X_val, (self.X_val.shape[0], -1))
        self.X_test = np.reshape(self.X_test, (self.X_test.shape[0], -1))

        mean_image = np.mean(self.X_train, axis=0)

        self.X_train -= mean_image
        self.X_val -= mean_image
        self.X_test -= mean_image

    def save(self, path):
        pickle.dump({'two_layer_net': self.net}, open(str(path / 'two_layer_net.p'), 'wb'))

    def step(self, tensorboard_writer, current_iteration):
        loss, acc = self.net.step(self.X_train, self.y_train, learning_rate=self.preset.get_float('learning_rate'), reg=self.preset.get_float('reg'), momentum=self.preset.get_float('momentum'), dropout=self.preset.get_float('dropout'), batch_size=self.preset.get_int('batch_size'))
        tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="loss/training", simple_value=loss)]), current_iteration)
        tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="accuracy/training", simple_value=acc)]),
                                       current_iteration)

        y_val_pred = self.net.predict(self.X_val)
        tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="accuracy/val", simple_value=np.mean(self.y_val == y_val_pred))]), current_iteration)

    def load(self, path):
        self.net = pickle.load(open(str(path / 'two_layer_net.p'), 'rb'))['two_layer_net']
