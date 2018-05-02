from torch import nn

class Sequential(nn.Sequential):
    def __init__(self, *nodes, input_shape):
        from .nodes import Node, Lambda
        from inspect import isfunction

        self._shape_sequence = [input_shape]
        nodes = list(nodes)
        for i, node in enumerate(nodes):
            if isfunction(node): 
                nodes[i] = Lambda(node)
                node = nodes[i]

            if isinstance(node, Node):
                node.build(input_shape)
                input_shape = node.get_output_shape(input_shape)

            self._shape_sequence.append(input_shape)

        super().__init__(*nodes)

    def summary(self, parameters='trainable', arguments=False, max_width=120):
        from beautifultable import BeautifulTable
        from ._utils import num_params

        def _handle_parameter_output(mode, node=None):
            str_dict = {'trainable': 'Trainable', 'non-trainable': 'NON-Trainable', 'all': '', True: '(Trainable, NON-Trainable)'}
            if mode == 'col': return str_dict[parameters] + ' Parameters'

            def _get_num_params(module):
                n = num_params(module) if module is not None else (0, 0)
                n_dict = {'trainable': n[0], 'non-trainable': n[1], 'all': sum(n), True: n}
                n = n_dict[parameters]
                return ', '.join(['{:,}'] * len(n)).format(*n) if type(n) is tuple else '{:,}'.format(n)
            
            if mode == 'row': return _get_num_params(node)

            print('Total' + str_dict[parameters] + 'Parameters:', _get_num_params(self))

        shape_sequence = [', '.join(str(i) for i in s) for s in self._shape_sequence]


        table = BeautifulTable(max_width=max_width)
        column_headers = ['Node', 'Shape']
        if parameters is not False: column_headers.append(_handle_parameter_output('col'))

        if arguments: column_headers.append('Arguments')
        table.column_headers = column_headers
        
        row = ['input', shape_sequence[0]]
        if parameters is not False: row.append(_handle_parameter_output('row'))

        if arguments: row.append('')
        table.append_row(row)
        for node, shape in zip(self.children(), shape_sequence[1:]):
            name = str(node).split('(')[0]
            row = [name, shape]
            if parameters is not False: row.append(_handle_parameter_output('row', node))

            if arguments: row.append(node.get_args())
            table.append_row(row)
            
        print(table)

        if parameters is not False: _handle_parameter_output('total')