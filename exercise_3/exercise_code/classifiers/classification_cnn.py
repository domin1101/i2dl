"""ClassificationCNN"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class ClassificationCNN(nn.Module):
    """
    A PyTorch implementation of a three-layer convolutional network
    with the following architecture:

    conv - relu - 2x2 max pool - fc - dropout - relu - fc

    The network operates on mini-batches of data that have shape (N, C, H, W)
    consisting of N images, each with height H and width W and with C input
    channels.
    """

    def __init__(self, input_dim=(3, 32, 32), num_filters=[32], kernel_size=[7],
                 stride_conv=1, weight_scale=0.001, pool=2, stride_pool=2, hidden_dims=[100], pool_toggle=[True],
                 num_classes=10, dropout=[0.0], mean_image=None, strides=[1]):
        """
        Initialize a new network.

        Inputs:
        - input_dim: Tuple (C, H, W) giving size of input data.
        - num_filters: Number of filters to use in the convolutional layer.
        - kernel_size: Size of filters to use in the convolutional layer.
        - hidden_dim: Number of units to use in the fully-connected hidden layer-
        - num_classes: Number of scores to produce from the final affine layer.
        - stride_conv: Stride for the convolution layer.
        - stride_pool: Stride for the max pooling layer.
        - weight_scale: Scale for the convolution weights initialization
        - pool: The size of the max pooling window.
        - dropout: Probability of an element to be zeroed.
        """
        super(ClassificationCNN, self).__init__()
        channels, height, width = input_dim

        ########################################################################
        # TODO: Initialize the necessary trainable layers to resemble the      #
        # ClassificationCNN architecture  from the class docstring.            #
        #                                                                      #
        # In- and output features should not be hard coded which demands some  #
        # calculations especially for the input of the first fully             #
        # convolutional layer.                                                 #
        #                                                                      #
        # The convolution should use "same" padding which can be derived from  #
        # the kernel size and its weights should be scaled. Layers should have #
        # a bias if possible.                                                  #
        #                                                                      #
        # Note: Avoid using any of PyTorch's random functions or your output   #
        # will not coincide with the Jupyter notebook cell.                    #
        ########################################################################
        self.conv = nn.ModuleList()
        input_filter = channels
        for key, num_filter in enumerate(num_filters):
            self.conv.append(nn.Conv2d(input_filter, num_filter, kernel_size[key], padding=0, stride=strides[key]))
            input_filter = num_filter

            if pool_toggle[key]:
                height //= pool
                width //= pool
        self.pool = pool
        self.stride_pool = stride_pool
        self.dropout = dropout
        self.pool_toggle = pool_toggle
        self.mean_image = mean_image

        # an affine operation: y = Wx + b
        self.fc = nn.ModuleList()
        input_dim = input_filter * height * width
        input_dim = 192
        for hidden_dim in hidden_dims:
            self.fc.append(nn.Linear(input_dim, hidden_dim))
            input_dim = hidden_dim
        self.fc.append(nn.Linear(input_dim, num_classes))
    
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

    def forward(self, x):
        """
        Forward pass of the neural network. Should not be called manually but by
        calling a model instance directly.

        Inputs:
        - x: PyTorch input Variable
        """
        if x.min() < 0:
            x += self.mean_image

        ########################################################################
        # TODO: Chain our previously initialized fully-connected neural        #
        # network layers to resemble the architecture drafted in the class     #
        # docstring. Have a look at the Variable.view function to make the     #
        # transition from the spatial input image to the flat fully connected  #
        # layers.                                                              #
        ########################################################################
        drop_key = 0
        for key, conv in enumerate(self.conv):
            #print(key, x.size())
            x = F.relu(conv(x))
            #print(key, x.size())
            if self.pool_toggle[key]:
                x = F.max_pool2d(x, self.pool, stride=self.stride_pool)
            #x = F.dropout(x, self.dropout[drop_key], training=self.training)
            drop_key += 1

        x = x.view(-1, self.num_flat_features(x))

        for fc in self.fc[:-1]:
            x = F.relu(fc(x))
            x = F.dropout(x, self.dropout[drop_key], training=self.training)
            drop_key += 1
        x = self.fc[-1](x)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return x

    def num_flat_features(self, x):
        """
        Computes the number of features if the spatial input x is transformed
        to a 1D flat input.
        """
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features

    @property
    def is_cuda(self):
        """
        Check if model parameters are allocated on the GPU.
        """
        return next(self.parameters()).is_cuda

    def save(self, path):
        """
        Save model with its parameters to the given path. Conventionally the
        path should end with "*.model".

        Inputs:
        - path: path string
        """
        print('Saving model... %s' % path)
        torch.save(self, path)
