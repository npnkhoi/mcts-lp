ALGOS = {
    'full': ['ab-8', 'ab-6', 'ab-4', 'ab-2'], # to be filled
    'uct': [], # to be filled
    'uct-lite': [], # to be filled
    'ab-sm': ['ab-8', 'ab-6', 'ab-4', 'ab-2'],
    'b6': ['ab-6', 'ab-4', 'ab-2', 'uct-0.01', 'uct-0.5', 'uct-0.99'], 
    'lite': ['ab-5', 'ab-4', 'ab-3', 'ab-2', 'ab-1', 'uct-1-512', 'uct-1-128', 'uct-1-32', 'uct-1-8'],
    'deep': ['ab-8', 'uct-0.001-10000', 'uct-0.01-10000', 'uct-0.1-10000', 'uct-1-10000', 'uct-10-10000'],
    'dirty': ['uct-0.001-100000', 'uct-0.001-10']
}
# complete 'full' and 'uct' set
c_values = ['0.001', '0.01', '0.1', '1', '10']
num_iterations = [10**5, 10000, 1000, 100, 10]
for c in c_values:
    ALGOS['full'].extend([f'uct-{c}-{iter}' for iter in num_iterations])
    ALGOS['uct'].extend([f'uct-{c}-{iter}' for iter in num_iterations])
    ALGOS['uct-lite'].extend([f'uct-{c}-{iter}' for iter in num_iterations[1:]])