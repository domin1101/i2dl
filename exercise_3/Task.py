import sys
sys.path.append('../../')
import TaskPlan
from exercise_code.classifiers.classification_cnn import ClassificationCNN
from exercise_code.solver import Solver
from exercise_code.data_utils import get_CIFAR10_datasets
import torch
from torch.autograd import Variable
from torchvision import transforms
import pickle
import tensorflow as tf

class Task(TaskPlan.Task):

    def __init__(self, preset, preset_pipe, logger, subtask):
        super().__init__(preset, preset_pipe, logger, subtask)

        transform_arr = []
        for i in range(2):
            filter = [
                transforms.ToPILImage()
            ]

            if i == 0:
                filter.append(transforms.RandomAffine(self.preset.get_float('rotate'), (self.preset.get_float('translate'), self.preset.get_float('translate')), (self.preset.get_float('scale_min'), self.preset.get_float('scale_max'))))

            if self.preset.get_bool('flip'):
                filter.append(transforms.RandomHorizontalFlip())

            filter.append(transforms.Resize(size=126))

            filter.append(transforms.ToTensor())

            transform_arr.append(transforms.Compose(filter))

        train_data, val_data, test_data, self.mean_image = get_CIFAR10_datasets(transform_train=transform_arr[0], transform_val=transform_arr[1])
        self.train_loader = torch.utils.data.DataLoader(train_data, batch_size=self.preset.get_int('batch_size'), shuffle=True, num_workers=4)
        self.val_loader = torch.utils.data.DataLoader(val_data, batch_size=self.preset.get_int('batch_size'), shuffle=False, num_workers=4)

        self.model = ClassificationCNN(num_filters=self.preset.get_list("num_filters"), kernel_size=self.preset.get_list("kernel_size"), hidden_dims=self.preset.get_list('hidden_dims'), pool_toggle=self.preset.get_list('pool_toggle'), dropout=self.preset.get_list('dropout'), strides=self.preset.get_list('strides'), mean_image=self.mean_image)
        self.logger.log(str(self.model))
        self.solver = Solver(optim_args={'lr': self.preset.get_float("learning_rate"), 'weight_decay': self.preset.get_float("weight_decay")})
        self.solver.set_model(self.model)
        self.train_iterator = iter(self.train_loader)

    def save(self, path):
        self.model.save(str(path / "classification_cnn.model"))

    def step(self, tensorboard_writer, current_iteration):
        try:
            acc, loss = self.solver.step(self.model, self.train_iterator)
        except StopIteration:
            self.train_iterator = iter(self.train_loader)
            acc, loss = self.solver.step(self.model, self.train_iterator)

        tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="loss/training", simple_value=loss)]), current_iteration)
        tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="accuracy/training", simple_value=acc)]), current_iteration)

        if current_iteration % self.preset.get_int('val_interval') == 0:
            val_acc, val_loss = self.solver.validate(self.model, self.val_loader)
            tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="loss/val", simple_value=val_loss)]), current_iteration)
            tensorboard_writer.add_summary(tf.Summary(value=[tf.Summary.Value(tag="accuracy/val", simple_value=val_acc)]), current_iteration)

    def load(self, path):
        self.model = torch.load(str(path / "classification_cnn.model"))
        self.model.mean_image = self.mean_image
        self.solver.set_model(self.model)
