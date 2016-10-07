from pacman.executor.injection_decorator import inject_items
from spynnaker.pyNN.models.neural_properties.neural_parameter \
    import NeuronParameter
from spynnaker.pyNN.models.neuron.synapse_types.abstract_synapse_type \
    import AbstractSynapseType

from data_specification.enums.data_type import DataType

import numpy


def get_exponential_decay_and_init(tau, machine_time_step):
    decay = numpy.exp(numpy.divide(-float(machine_time_step),
                                   numpy.multiply(1000.0, tau)))
    init = numpy.multiply(numpy.multiply(tau, numpy.subtract(1.0, decay)),
                          (1000.0 / float(machine_time_step)))
    scale = float(pow(2, 32))
    decay_scaled = numpy.multiply(decay, scale).astype("uint32")
    init_scaled = numpy.multiply(init, scale).astype("uint32")
    return decay_scaled, init_scaled


class SynapseTypeExponential(AbstractSynapseType):

    default_parameters = {'tau_syn_E': 5.0, 'tau_syn_I': 5.0}

    def __init__(self, neuron_cells):
        AbstractSynapseType.__init__(self)
        self._n_neurons = len(neuron_cells)
        self._neuron_cells = neuron_cells

    def get_n_synapse_types(self):
        return 2

    @classmethod
    def get_synapse_id_by_target(cls, target):
        if target == "excitatory":
            return 0
        elif target == "inhibitory":
            return 1
        return None

    def get_synapse_targets(self):
        return "excitatory", "inhibitory"

    def get_n_synapse_type_parameters(self):
        return 4

    @inject_items({"machine_time_step": "MachineTimeStep"})
    def get_synapse_type_parameters(self, neuron_cell, machine_time_step):
        e_decay, e_init = get_exponential_decay_and_init(
            neuron_cell.get("tau_syn_E"), machine_time_step)
        i_decay, i_init = get_exponential_decay_and_init(
            neuron_cell.get("tau_syn_I"), machine_time_step)

        return [
            NeuronParameter(e_decay, DataType.UINT32),
            NeuronParameter(e_init, DataType.UINT32),
            NeuronParameter(i_decay, DataType.UINT32),
            NeuronParameter(i_init, DataType.UINT32)
        ]

    def get_n_cpu_cycles_per_neuron(self):

        # A guess
        return 100
