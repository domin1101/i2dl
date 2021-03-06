"""Two Layer Network."""
# pylint: disable=invalid-name
import numpy as np
import matplotlib.pyplot as plt

class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network. The net has an input dimension
    of N, a hidden layer dimension of H, and performs classification over C
    classes. We train the network with a softmax loss function and L2
    regularization on the weight matrices. The network uses a ReLU nonlinearity
    after the first fully connected layer.

    In other words, the network has the following architecture:

    input - fully connected layer - ReLU - fully connected layer - softmax

    The outputs of the second fully-connected layer are the scores for each
    class.
    """

    def __init__(self, input_size, hidden_size, output_size, std=1e-4):
        """
        Initialize the model. Weights are initialized to small random values and
        biases are initialized to zero. Weights and biases are stored in the
        variable self.params, which is a dictionary with the following keys:

        W1: First layer weights; has shape (D, H)
        b1: First layer biases; has shape (H,)
        W2: Second layer weights; has shape (H, C)
        b2: Second layer biases; has shape (C,)

        Inputs:
        - input_size: The dimension D of the input data.
        - hidden_size: The number of neurons H in the hidden layer.
        - output_size: The number of classes C.
        """
        self.params = {}
        self.params['W1'] = std * np.random.randn(input_size, hidden_size)
        self.params['b1'] = np.zeros(hidden_size)
        self.params['W2'] = std * np.random.randn(hidden_size, output_size)
        self.params['b2'] = np.zeros(output_size)
        self.last_grads = None

    def loss(self, X, y=None, reg=0.0, dropout=1.0):
        """
        Compute the loss and gradients for a two layer fully connected neural
        network.

        Inputs:
        - X: Input data of shape (N, D). Each X[i] is a training sample.
        - y: Vector of training labels. y[i] is the label for X[i], and each
          y[i] is an integer in the range 0 <= y[i] < C. This parameter is
          optional; if it is not passed then we only return scores, and if it is
          passed then we instead return the loss and gradients.
        - reg: Regularization strength.

        Returns:
        If y is None, return a matrix scores of shape (N, C) where scores[i, c]
        is the score for class c on input X[i].

        If y is not None, instead return a tuple of:
        - loss: Loss (data loss and regularization loss) for this batch of
          training samples.
        - grads: Dictionary mapping parameter names to gradients of those
          parameters  with respect to the loss function; has the same keys as
          self.params.
        """
        # pylint: disable=too-many-locals
        # Unpack variables from the params dictionary
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        N, _ = X.shape

        # Compute the forward pass
        scores = None
        ########################################################################
        # TODO: Perform the forward pass, computing the class scores for the   #
        # input. Store the result in the scores variable, which should be an   #
        # array of shape (N, C).                                               #         
        ########################################################################
        h1 = np.matmul(X, W1) + b1
        h1 = h1 * (h1 > 0)

        if dropout < 1:
            h1[np.random.rand(h1.shape[0], h1.shape[1]) < dropout] = 0
            h1 = h1 / dropout

        h2 = np.matmul(h1, W2) + b2
        scores = h2
        ########################################################################
        #                              END OF YOUR CODE                        #
        ########################################################################

        # If the targets are not given then jump out, we're done
        if y is None:
            return scores

        acc = (np.argmax(scores, -1) == y).mean()
        # Compute the loss
        loss = None
        ########################################################################
        # TODO: Finish the forward pass, and compute the loss. This should     #
        # include both the data loss and L2 regularization for W1 and W2. Store#
        # the result in the variable loss, which should be a scalar. Use the   #
        # Softmax classifier loss. So that your results match ours, multiply   #
        # the regularization loss by 0.5                                       #
        ########################################################################
        y_exp = np.exp(scores - np.expand_dims(np.max(scores, -1), -1))
        y_exp_sum = np.expand_dims(np.sum(y_exp, -1), -1)
        softmax = y_exp / y_exp_sum

        loss = -np.sum(np.log(softmax) * np.eye(softmax.shape[1])[y]) / softmax.shape[0]
        loss += reg * 0.5 * (np.sum(W1 ** 2) + np.sum(W2 ** 2))# / (W1.shape[0] * W1.shape[1] + W2.shape[0] * W2.shape[1])
        ########################################################################
        #                              END OF YOUR CODE                        #
        ########################################################################

        # Backward pass: compute gradients
        grads = {}
        ########################################################################
        # TODO: Compute the backward pass, computing the derivatives of the    #
        # weights and biases. Store the results in the grads dictionary. For   #
        # example, grads['W1'] should store the gradient on W1, and be a matrix#
        # of same size                                                         #
        ########################################################################
        loss_grad = -1 / softmax * np.eye(softmax.shape[1])[y] / softmax.shape[0]

        softmax_grad = y_exp * (1 / y_exp_sum * loss_grad + np.expand_dims(np.sum(-1 / (y_exp_sum ** 2) * y_exp * loss_grad, -1), -1))
        grads['W2'] = np.matmul(np.transpose(h1), softmax_grad) + reg * W2
        grads['b2'] = np.sum(softmax_grad, 0)
        h1_grad = np.matmul(softmax_grad, np.transpose(W2))
        relu_grad = (h1 > 0) * h1_grad
        grads['W1'] = np.matmul(np.transpose(X), relu_grad) + reg * W1
        grads['b1'] = np.sum(relu_grad, 0)
        ########################################################################
        #                              END OF YOUR CODE                        #
        ########################################################################

        return loss, acc, grads

    def train(self, X, y, X_val, y_val,
              learning_rate=1e-3, learning_rate_decay=0.95,
              reg=1e-5, num_iters=100,
              batch_size=200, verbose=False):
        """
        Train this neural network using stochastic gradient descent.

        Inputs:
        - X: A numpy array of shape (N, D) giving training data.
        - y: A numpy array f shape (N,) giving training labels; y[i] = c means
          that X[i] has label c, where 0 <= c < C.
        - X_val: A numpy array of shape (N_val, D) giving validation data.
        - y_val: A numpy array of shape (N_val,) giving validation labels.
        - learning_rate: Scalar giving learning rate for optimization.
        - learning_rate_decay: Scalar giving factor used to decay the learning
          rate after each epoch.
        - reg: Scalar giving regularization strength.
        - num_iters: Number of steps to take when optimizing.
        - batch_size: Number of training examples to use per step.
        - verbose: boolean; if true print progress during optimization.
        """
        # pylint: disable=too-many-arguments, too-many-locals
        num_train = X.shape[0]
        iterations_per_epoch = max(num_train // batch_size, 1)

        # Use SGD to optimize the parameters in self.model
        loss_history = []
        train_acc_history = []
        val_acc_history = []

        for it in range(num_iters):
            loss, acc = self.step(X, y, learning_rate, reg, batch_size)
            loss_history.append(loss)

            if verbose and it % 100 == 0:
                print('iteration %d / %d: loss %f' % (it, num_iters, loss))

            # Every epoch, check train and val accuracy and decay learning rate.
            if it % iterations_per_epoch == 0:
                # Check accuracy
                train_acc = acc
                val_acc = (self.predict(X_val) == y_val).mean()
                train_acc_history.append(train_acc)
                val_acc_history.append(val_acc)

                # Decay learning rate
                learning_rate *= learning_rate_decay

        return {
            'loss_history': loss_history,
            'train_acc_history': train_acc_history,
            'val_acc_history': val_acc_history,
        }

    def step(self, X, y,
              learning_rate=1e-3,
              reg=1e-5,
              batch_size=200,
             momentum=0,
             dropout=1):
        X_batch = None
        y_batch = None

        ####################################################################
        # TODO: Create a random minibatch of training data and labels,     #
        # storing hem in X_batch and y_batch respectively.                 #
        ####################################################################
        indx = np.random.choice(X.shape[0], batch_size)
        X_batch = X[indx]
        y_batch = y[indx]
        ####################################################################
        #                             END OF YOUR CODE                     #
        ####################################################################

        # Compute loss and gradients using the current minibatch
        loss, acc, grads = self.loss(X_batch, y=y_batch, reg=reg, dropout=dropout)

        ####################################################################
        # TODO: Use the gradients in the grads dictionary to update the    #
        # parameters of the network (stored in the dictionary self.params) #
        # using stochastic gradient descent. You'll need to use the        #
        # gradients stored in the grads dictionary defined above.          #
        ####################################################################
        if momentum > 0:
            if self.last_grads is not None:
                for param in self.params.keys():
                    grads[param] += self.last_grads[param] * momentum
            self.last_grads = grads

        for param in self.params.keys():
            self.params[param] -= grads[param] * learning_rate
        ####################################################################
        #                             END OF YOUR CODE                     #
        ####################################################################

        return loss, acc

    def predict(self, X):
        """
        Use the trained weights of this two-layer network to predict labels for
        data points. For each data point we predict scores for each of the C
        classes, and assign each data point to the class with the highest score.

        Inputs:
        - X: A numpy array of shape (N, D) giving N D-dimensional data points to
          classify.

        Returns:
        - y_pred: A numpy array of shape (N,) giving predicted labels for each
          of the elements of X. For all i, y_pred[i] = c means that X[i] is
          predicted to have class c, where 0 <= c < C.
        """
        y_pred = None

        ########################################################################
        # TODO: Implement this function; it should be VERY simple!             #
        ########################################################################
        y_pred = np.argmax(self.loss(X), -1)
        #############################:###########################################
        #                              END OF YOUR CODE                        #
        ########################################################################

        return y_pred


def neuralnetwork_hyperparameter_tuning(X_train, y_train, X_val, y_val):
    best_net = None # store the best model into this
    best_acc = 0
    ############################################################################
    # TODO: Tune hyperparameters using the validation set. Store your best     #
    # trained model in best_net.                                               #
    #                                                                          #
    # To help debug your network, it may help to use visualizations similar to #
    # the  ones we used above; these visualizations will have significant      #
    # qualitative differences from the ones we saw above for the poorly tuned  #
    # network.                                                                 #
    #                                                                          #
    # Tweaking hyperparameters by hand can be fun, but you might find it useful#
    # to  write code to sweep through possible combinations of hyperparameters #
    # automatically like we did on the previous exercises.                     #
    ############################################################################

    f, (ax1, ax2) = plt.subplots(2, 1)

    batch_size = 200
    num_iters = 40000
    learning_rate = 1e-3
    hidden_size = 512
    learning_rate_decay = 1
    for learning_rate in [1e-2]:
    #for batch_size in [32,64,128,256]:
        param = learning_rate
        input_size = X_train.shape[1]#32 * 32 * 3
        num_classes = 10
        net = TwoLayerNet(input_size, hidden_size, num_classes)

        # Train the network
        stats = net.train(X_train, y_train, X_val, y_val,
                          num_iters=int(num_iters * 200 / batch_size), batch_size=batch_size,
                          learning_rate=learning_rate, learning_rate_decay=learning_rate_decay,
                          reg=0.0, verbose=False)

        ax1.plot(stats['val_acc_history'], label=str(param))
        ax2.plot(stats['train_acc_history'], label=str(param))
        # Predict on the validation set
        val_acc = (net.predict(X_val) == y_val).mean()
        print(str(param), val_acc)
        if best_net is None or val_acc > best_acc:
            best_net = net
    ax1.set_title('Classification accuracy history')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Validation accuracy')
    ax1.legend()

    ax2.set_title('Classification accuracy history')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Training accuracy')
    ax2.legend()

    ############################################################################
    #                               END OF YOUR CODE                           #
    ############################################################################
    return best_net
