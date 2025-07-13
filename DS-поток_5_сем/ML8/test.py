from typing import Sequence
import unittest

import numpy as np

import torch
from torch.nn.modules.activation import Softplus

RANDOM_SEED = 42


class TestLayers(unittest.TestCase):
    '''
        Класс для тестирования всех модулей.
    '''
    
    def _generate_test_data(
        self, shape, dtype=np.float32, mode='uniform', minval=-10, maxval=10
    ):
        '''
        Генерирует тестовые данные для `forward()` и `backward()`
        '''
        if mode == 'uniform':
            rand_array = np.random.uniform(minval, maxval, shape).astype(dtype)
            # иногда имеет смысл нормализовать
            # rand_array /= rand_array.sum(axis=-1, keepdims=True)
            # rand_array = rand_array.clip(1e-5, 1.)
            # rand_array = 1. / rand_array
            return rand_array
    
    
    def _custom_forward_backward(
        self, 
        layer_input, 
        next_layer_grad,
        custom_layer,
        return_params_grad=False
    ):
        '''
        Вычисляет результат `forward()` и `backward()` в слое `layer`.
        
        Вход:
            `layer_input (np.array)` -- тестовый вход
            `next_layer_grad (np.array)` -- тестовый градиент, 
                пришедший от следующего слоя 
            `layer` -- слой из нашего мини-фреймворка на NumPy
            `return_params_grad` -- если True, то вернуть еще градиенты параметров слоя
        Выход:
            `custom_layer_output (np.array)` -- выход слоя `layer` после `forward()`
            `custom_layer_grad (np.array)` -- градиент слоя `layer` после `backward()`
            [opt] `custom_params_grad (np.array)` -- градиенты параметров слоя `layer`
        '''
        custom_layer_output = custom_layer.forward(layer_input)
        custom_layer_grad = custom_layer.backward(layer_input, next_layer_grad)
        if return_params_grad:
            custom_layer.update_grad_params(layer_input, next_layer_grad)
            custom_params_grad = custom_layer.get_grad_params()
            return custom_layer_output, custom_layer_grad, custom_params_grad
        else:
            return custom_layer_output, custom_layer_grad
    
    
    def _torch_forward_backward(
        self, 
        layer_input, 
        next_layer_grad, 
        torch_layer,
        return_params_grad=False
    ):
        '''
        Вычисляет результат `forward()` и `backward()` в PyTorch-слое `layer`.
        
        Вход:
            `layer_input (np.array)` -- тестовый вход
            `next_layer_grad (np.array)` -- тестовый градиент, 
                пришедший от следующего слоя 
            `torch_layer` -- слой из PyTorch
            `return_params_grad` -- если True, то вернуть еще градиенты параметров слоя
        Выход:
            `torch_layer_output (np.array)` -- выход слоя `layer` после `forward()`
            `torch_layer_grad (np.array)` -- градиент слоя `layer` после `backward()`
            [opt] `torch_params_grad (np.array)` -- градиенты параметров слоя `layer`
        '''
        layer_input_torch = torch.from_numpy(layer_input)
        layer_input_torch.requires_grad = True
        torch_layer_output = torch_layer(layer_input_torch)
        torch_layer_output = torch_layer_output
        next_layer_grad_torch = torch.from_numpy(next_layer_grad)
        torch_layer_output.backward(next_layer_grad_torch)
        torch_layer_grad = layer_input_torch.grad
        if return_params_grad:
            torch_params_grad = torch_layer.parameters()
            return torch_layer_output.data.numpy(), torch_layer_grad.data.numpy(), torch_params_grad
        else:
            return torch_layer_output.data.numpy(), torch_layer_grad.data.numpy()
    
    
    def test_Linear(self):
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in, n_out = 2, 3, 4
        for _ in range(100):
            # инициализируем слои
            torch_layer = torch.nn.Linear(n_in, n_out)
            custom_layer = Linear(n_in, n_out)
            custom_layer.W = torch_layer.weight.data.numpy().T
            custom_layer.b = torch_layer.bias.data.numpy()
            # формируем тестовые входные тензоры
            layer_input = self._generate_test_data((batch_size, n_in))
            next_layer_grad = self._generate_test_data((batch_size, n_out))
            # тестируем наш слой
            result = self._custom_forward_backward(
                layer_input,
                next_layer_grad,
                custom_layer,
                return_params_grad=True
            )
            custom_layer_output, custom_layer_grad, custom_params_grad = result
            # тестируем слой на PyTorch
            result = self._torch_forward_backward(
                layer_input,
                next_layer_grad,
                torch_layer,
                return_params_grad=True
            )
            torch_layer_output, torch_layer_grad, torch_params_grad = result
            # сравниваем выходы с точностью atol
            self.assertTrue(np.allclose(torch_layer_output, custom_layer_output, atol=1e-6))
            self.assertTrue(np.allclose(torch_layer_grad, custom_layer_grad, atol=1e-6))
            weight_grad, bias_grad = custom_params_grad
            torch_weight_grad = torch_layer.weight.grad.data.numpy()
            torch_bias_grad = torch_layer.bias.grad.data.numpy()
            self.assertTrue(np.allclose(torch_weight_grad.T, weight_grad, atol=1e-6))
            self.assertTrue(np.allclose(torch_bias_grad, bias_grad, atol=1e-6))
            
    
    def test_SoftMax(self):
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in = 2, 4
        for _ in range(100):
            # инициализируем слои
            custom_layer = SoftMax()
            torch_layer = torch.nn.Softmax(dim=1)
            # формируем тестовые входные тензоры
            layer_input = self._generate_test_data((batch_size, n_in))
            next_layer_grad = self._generate_test_data((batch_size, n_in))
            # тестируем наш слой
            custom_layer_output, custom_layer_grad = self._custom_forward_backward(
                layer_input,
                next_layer_grad,
                custom_layer
            )
            # тестируем слой на PyTorch
            torch_layer_output, torch_layer_grad = self._torch_forward_backward(
                layer_input,
                next_layer_grad,
                torch_layer
            )
            # сравниваем выходы с точностью atol
            self.assertTrue(np.allclose(custom_layer_output, torch_layer_output, atol=1e-5))
            self.assertTrue(np.allclose(custom_layer_grad, torch_layer_grad, atol=1e-5))
            
            
    def test_LogSoftMax(self):
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in = 2, 4
        for _ in range(100):
            # инициализируем слои
            custom_layer = LogSoftMax()
            torch_layer = torch.nn.LogSoftmax(dim=1)
            # формируем тестовые входные тензоры
            layer_input = self._generate_test_data((batch_size, n_in))
            next_layer_grad = self._generate_test_data((batch_size, n_in))
            # тестируем наш слой
            custom_layer_output, custom_layer_grad = self._custom_forward_backward(
                layer_input,
                next_layer_grad,
                custom_layer
            )
            # тестируем слой на PyTorch
            torch_layer_output, torch_layer_grad = self._torch_forward_backward(
                layer_input,
                next_layer_grad,
                torch_layer
            )
            # сравниваем выходы с точностью atol
            self.assertTrue(np.allclose(custom_layer_output, torch_layer_output, atol=1e-5))
            self.assertTrue(np.allclose(custom_layer_grad, torch_layer_grad, atol=1e-5))
            
            
    def test_Sequential(self):
        # тестируем `Sequential = [Linear, SoftMax]`
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in, n_out = 2, 3, 4

        for _ in range(100):
            # слои торча
            torch_lin1 = torch.nn.Linear(n_in, n_in)
            torch_lin2 = torch.nn.Linear(n_in, n_out)
            torch_layers = torch.nn.Sequential(
                torch_lin1, 
                torch.nn.ReLU(),
                torch_lin2, 
                torch.nn.Softmax()
            )

            # собственные слои
            custom_lin1 = Linear(n_in, n_in)
            custom_lin1.W = torch_lin1.weight.data.numpy().T
            custom_lin1.b = torch_lin1.bias.data.numpy()

            custom_lin2 = Linear(n_in, n_out)
            custom_lin2.W = torch_lin2.weight.data.numpy().T
            custom_lin2.b = torch_lin2.bias.data.numpy()

            custom_layers = Sequential()
            custom_layers.add(custom_lin1)
            custom_layers.add(ReLU())
            custom_layers.add(custom_lin2)
            custom_layers.add(SoftMax())

            # формируем тестовые входные тензоры
            layer_input = self._generate_test_data((batch_size, n_in))
            next_layer_grad = self._generate_test_data((batch_size, n_out))

            # тестируем наш слой
            result = self._custom_forward_backward(
                layer_input,
                next_layer_grad,
                custom_layers,
                return_params_grad=True
            )
            custom_layers_output, custom_layers_grad, custom_params_list_grad = result

            # тестируем слой на PyTorch
            result = self._torch_forward_backward(
                layer_input,
                next_layer_grad,
                torch_layers,
                return_params_grad=True
            )
            torch_layers_output, torch_layers_grad, torch_params_gen_grad = result

            # сравниваем выходы с точностью atol
            self.assertTrue(np.allclose(torch_layers_output, custom_layers_output, atol=1e-6))
            self.assertTrue(np.allclose(torch_layers_grad, custom_layers_grad, atol=1e-6))

            # сравниваем градиенты для параметров
            for custom_params_grad, torch_layer in zip(custom_params_list_grad, torch_layers):
                if not custom_params_grad:
                    continue
                weight_grad, bias_grad = custom_params_grad
                torch_weight_grad = torch_layer.weight.grad.data.numpy()
                torch_bias_grad = torch_layer.bias.grad.data.numpy()
                self.assertTrue(np.allclose(torch_weight_grad.T, weight_grad, atol=1e-4))
                self.assertTrue(np.allclose(torch_bias_grad, bias_grad, atol=1e-4))

    
    def test_ReLU(self):
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in = 2, 4
        for _ in range(100):
            # инициализируем слои
            custom_layer = ReLU()
            torch_layer = torch.nn.ReLU()
            # формируем тестовые входные тензоры
            layer_input = self._generate_test_data((batch_size, n_in))
            next_layer_grad = self._generate_test_data((batch_size, n_in))
            # тестируем наш слой
            custom_layer_output, custom_layer_grad = self._custom_forward_backward(
                layer_input,
                next_layer_grad,
                custom_layer
            )
            # тестируем слой на PyTorch
            torch_layer_output, torch_layer_grad = self._torch_forward_backward(
                layer_input,
                next_layer_grad,
                torch_layer
            )
            # сравниваем выходы с точностью atol
            self.assertTrue(np.allclose(custom_layer_output, torch_layer_output, atol=1e-6))
            self.assertTrue(np.allclose(custom_layer_grad, torch_layer_grad, atol=1e-6))
            
            
    def test_LeakyReLU(self):
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in = 2, 4
        for _ in range(100):
            # инициализируем слои
            slope = np.random.uniform(0.01, 0.05)
            torch_layer = torch.nn.LeakyReLU(slope)
            custom_layer = LeakyReLU(slope)
            # формируем тестовые входные тензоры
            layer_input = self._generate_test_data((batch_size, n_in))
            next_layer_grad = self._generate_test_data((batch_size, n_in))
            # тестируем наш слой
            custom_layer_output, custom_layer_grad = self._custom_forward_backward(
                layer_input,
                next_layer_grad,
                custom_layer
            )
            # тестируем слой на PyTorch
            torch_layer_output, torch_layer_grad = self._torch_forward_backward(
                layer_input,
                next_layer_grad,
                torch_layer
            )
            # сравниваем выходы с точностью atol
            self.assertTrue(np.allclose(custom_layer_output, torch_layer_output, atol=1e-6))
            self.assertTrue(np.allclose(custom_layer_grad, torch_layer_grad, atol=1e-6))


    def test_NLLCriterion(self):
        np.random.seed(RANDOM_SEED)
        torch.manual_seed(RANDOM_SEED)
        batch_size, n_in = 2, 4
        for _ in range(100):
            # инициализируем слои
            torch_layer = torch.nn.NLLLoss()
            custom_layer = NLLCriterion()
            # формируем тестовые данные
            layer_input = np.random.uniform(-5, 5, (batch_size, n_in)).astype(np.float32)
            layer_input = torch.nn.LogSoftmax(dim=1)(torch.from_numpy(layer_input)).data.numpy()
            target_labels = np.random.choice(n_in, batch_size)
            target = np.zeros((batch_size, n_in), np.float32)
            target[np.arange(batch_size), target_labels] = 1  # one-hot encoding
            # тестируем `update_output()`
            custom_layer_output = custom_layer.update_output(layer_input, target)
            layer_input_var = torch.from_numpy(layer_input)
            layer_input_var.requires_grad = True 
            torch_layer_output_var = torch_layer(layer_input_var, torch.from_numpy(target_labels).long())
            self.assertTrue(np.allclose(
                torch_layer_output_var.data.numpy(), custom_layer_output, atol=1e-6
            ))
            # тестируем `update_grad_input()`
            custom_layer_grad = custom_layer.update_grad_input(layer_input, target)
            torch_layer_output_var.backward()
            torch_layer_grad_var = layer_input_var.grad
            self.assertTrue(np.allclose(torch_layer_grad_var.data.numpy(), custom_layer_grad, atol=1e-6))
            

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLayers)
    unittest.TextTestRunner(verbosity=2).run(suite)
