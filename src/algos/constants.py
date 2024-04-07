import itertools
c_values = ['0.001', '0.01', '0.1', '1', '10', '1000000']

ALGOS = {
    # 'uct-minimax': [], # to be filled
    'uct-lite': [f'uct-{c}-10000' for c in c_values], # to be filled
    'uct-minimax-lite': [f'uct_minimax-{c}-10000' for c in c_values],
    'uct-minimax-tiny': ['uct_minimax-1-10'],
}