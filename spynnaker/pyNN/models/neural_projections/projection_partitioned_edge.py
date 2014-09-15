from pacman.model.partitioned_graph.partitioned_edge import PartitionedEdge
from spynnaker.pyNN.models.abstract_models.abstract_filterable_edge import \
    AbstractFilterableEdge


class ProjectionPartitionedEdge(PartitionedEdge, AbstractFilterableEdge):
    
    def __init__(self, presubvertex, postsubvertex, associated_edge):
        PartitionedEdge.__init__(self, presubvertex, postsubvertex)
        AbstractFilterableEdge.__init__(self)
        self._synapse_sublist = None
        self._associated_edge = associated_edge

    def get_synapse_sublist(self, graph_mapper):
        """
        Gets the synapse list for this subedge
        """
        pre_sub_lo = \
            graph_mapper.get_subvertex_slice(self._pre_subvertex).lo_atom
        pre_sub_hi = \
            graph_mapper.get_subvertex_slice(self._pre_subvertex).hi_atom
        post_sub_lo = \
            graph_mapper.get_subvertex_slice(self._post_subvertex).lo_atom
        post_sub_hi = \
            graph_mapper.get_subvertex_slice(self._post_subvertex).hi_atom
        if self._synapse_sublist is None:
            self._synapse_sublist = \
                self._associated_edge.get_synaptic_data().create_atom_sublist(
                    pre_sub_lo, pre_sub_hi, post_sub_lo, post_sub_hi)
        return self._synapse_sublist
    
    def get_synaptic_data(self, graph_mapper, min_delay):
        """
        Get synaptic data for all connections in this Projection.
        """
        return self._post_subvertex.vertex.get_synaptic_data(
            graph_mapper, self._pre_subvertex, self._pre_subvertex.n_atoms,
            self._post_subvertex, self._associated_edge.synapse_row_io)
    
    def free_sublist(self):
        """
        Indicates that the list will not be needed again
        """
        self._synapse_sublist = None

    def filter_sub_edge(self, subedge, graph_mapper):
        """determines if theres an actual connection in this subedge in temrs of
        synaptic data

        """
        if self._synapse_sublist is None:
            self.get_synapse_sublist(graph_mapper)

        pre_vertex_slice = graph_mapper.get_subvertex_slice(self._pre_subvertex)
        post_vertex_slice = \
            graph_mapper.get_subvertex_slice(self._post_subvertex)

        return self._synapse_sublist.is_connected(pre_vertex_slice,
                                                  post_vertex_slice)