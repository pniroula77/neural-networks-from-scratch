import numpy as np

from math import sqrt

from .functional import sigmoid, sigmoid_prime


class Function:
    """
    Abstract model of a differentiable function.
    """
    def __init__(self, *args, **kwargs):
        # initializing cache for intermediate results
        # helps with gradient calculation in some cases
        self.cache = {}
        # cache for gradients
        self.grad = {}

    def __call__(self, *args, **kwargs):
        # calculating output
        output = self.forward(*args, **kwargs)
        # calculating and caching local gradients
        self.grad = self.local_grad(*args, **kwargs)
        return output

    def forward(self, *args, **kwargs):
        """
        Forward pass of the function. Calculates the output value and the
        gradient at the input as well.
        """
        pass

    def backward(self, *args, **kwargs):
        """
        Backward pass. Computes the local gradient at the input value
        after forward pass.
        """
        pass

    def local_grad(self, *args, **kwargs):
        """
        Calculates the local gradients of the function at the given input.

        Returns:
            grad: dictionary of local gradients.
        """
        pass

    def global_grad(self, *args, **kwargs):
        """
        Calculates the global gradients during backpropagation.
        """
        pass


class Layer(Function):
    """
    Abstract model of a neural network layer. In addition to Function, a Layer
    also has weights and gradients with respect to the weights.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight = {}
        self.weight_update = {}

    def _init_weights(self, *args, **kwargs):
        pass

    def _update_weights(self, lr):
        """
        Updates the weights using the corresponding _global_ gradients computed during
        backpropagation.

        Args:
             lr: float. Learning rate.
        """
        for weight_key, weight in self.weight.items():
            self.weight[weight_key] = self.weight[weight_key] - lr * self.weight_update[weight_key]
        pass


class Linear(Layer):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self._init_weights(in_dim, out_dim)

    def _init_weights(self, in_dim, out_dim):
        scale = 1 / sqrt(in_dim)
        self.weight['W'] = scale * np.random.randn(in_dim, out_dim)
        self.weight['b'] = scale * np.random.randn(1, out_dim)

    def forward(self, X):
        """
        Forward pass for the Linear layer.

        Args:
            X: numpy.ndarray of shape (n_batch, in_dim) containing
                the input value.

        Returns:
            Y: numpy.ndarray of shape of shape (n_batch, out_dim) containing
                the output value.
        """

        output = np.dot(X, self.weight['W']) + self.weight['b']

        # caching variables for backprop
        self.cache['X'] = X
        self.cache['output'] = output

        return output

    def backward(self, dY):
        """
        Backward pass for the Linear layer.

        Args:
            dY: numpy.ndarray of shape (n_batch, n_out). Global gradient
                backpropagated from the next layer.

        Returns:
            dX: numpy.ndarray of shape (n_batch, n_out). Global gradient
                of the Linear layer.
        """
        # calculating the global gradient, to be propagated backwards
        dX = dY.dot(self.grad['X'].T)
        # calculating the global gradient wrt to weights
        X = self.cache['X']
        dW = self.grad['W'].T.dot(dY)
        db = np.sum(dY, axis=0, keepdims=True)
        # caching the global gradients
        self.weight_update = {'W': dW, 'b': db}

        return dX

    def local_grad(self, X):
        """
        Local gradients of the Linear layer at X.

        Args:
            X: numpy.ndarray of shape (n_batch, in_dim) containing the
                input data.

        Returns:
            grads: dictionary of local gradients with the following items:
                X: numpy.ndarray of shape (n_batch, in_dim).
                W: numpy.ndarray of shape (n_batch, in_dim).
                b: numpy.ndarray of shape (n_batch, 1).
        """
        gradX_local = self.weight['W']
        gradW_local = X
        gradb_local = np.ones_like(self.weight['b'])
        grads = {'X': gradX_local, 'W': gradW_local, 'b': gradb_local}
        return grads


class Sigmoid(Function):
    def forward(self, X):
        return sigmoid(X)

    def backward(self, dY):
        return dY * self.grad['X']

    def local_grad(self, X):
        grads = {'X': sigmoid_prime(X)}
        return grads
