ALGOS = {
    'full': ['ab-8', 'ab-6', 'ab-4', 'ab-2'], # to be filled
    'uct': [], # to be filled
    'uct-lite': [], # to be filled
    'uct-minimax': [], # to be filled
    'uct-minimax-lite': [], # to be filled
    'uct-minimax-tiny': ['uct_minimax-0.1-11'], # to be filled
    
    'lite': ['ab-5', 'ab-4', 'ab-3', 'ab-2', 'ab-1', 'uct-1-512', 'uct-1-128', 'uct-1-32', 'uct-1-8'],
}
# complete 'full' and 'uct' set
c_values = ['0.001', '0.01', '0.1', '1', '10']
num_iterations = [10**5, 10000, 1000, 100, 10]
for c in c_values:
    ALGOS['full'].extend([f'uct-{c}-{iter}' for iter in num_iterations])
    ALGOS['uct'].extend([f'uct-{c}-{iter}' for iter in num_iterations])
    ALGOS['uct-minimax'].extend([f'uct_minimax-{c}-{iter}' for iter in num_iterations])
    ALGOS['uct-lite'].extend([f'uct-{c}-{iter}' for iter in num_iterations[1:]])
    ALGOS['uct-minimax-lite'].extend([f'uct_minimax-{c}-{iter}' for iter in num_iterations[1:]])