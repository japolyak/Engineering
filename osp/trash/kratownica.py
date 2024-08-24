import numpy as np
import openseespy.opensees as ops
from shared import show_results, calculate


ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 2)

# region Liczby losowe
a = 3.0
b = 3.0

E = 30.0e6
A = 0.2

P_x = 5.0
P_y = -10.0
# endregion

# region Węzły
ops.node(1, 0.0, 0.0)
ops.node(2, a, 0.0)
ops.node(3, a * 2.0, 0.0)
ops.node(4, a * 3.0, 0.0)
ops.node(5, a * 4.0, 0.0)
ops.node(6, 0.0, b)
ops.node(7, a, b)
ops.node(8, a * 2.0, b)
ops.node(9, a * 3.0, b)
ops.node(10, a * 4.0, b)
# endregion

# region Podpory
ops.fix(1, 1, 1)
ops.fix(5, 1, 1)
# endregion

# region Elementy
ops.uniaxialMaterial('Elastic', 1, E)

# Belki
ops.element('truss', 1, 1, 2, A, 1)
ops.element('truss', 2, 2, 3, A, 1)
ops.element('truss', 3, 3, 4, A, 1)
ops.element('truss', 4, 4, 5, A, 1)
ops.element('truss', 5, 6, 7, A, 1)
ops.element('truss', 6, 7, 8, A, 1)
ops.element('truss', 7, 8, 9, A, 1)
ops.element('truss', 8, 9, 10, A, 1)

# Słupy
ops.element('truss', 9, 1, 6, A, 1)
ops.element('truss', 10, 2, 7, A, 1)
ops.element('truss', 11, 3, 8, A, 1)
ops.element('truss', 12, 4, 9, A, 1)
ops.element('truss', 13, 5, 10, A, 1)

# Krzyżulce
ops.element('truss', 14, 1, 7, A, 1)
ops.element('truss', 15, 7, 3, A, 1)
ops.element('truss', 16, 3, 9, A, 1)
ops.element('truss', 17, 9, 5, A, 1)
# endregion

# region Siły
# Skupione w górnych węzłach
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(6, P_x, P_y)
ops.load(7, 0, P_y)
ops.load(8, 0, P_y)
ops.load(9, 0, P_y)
ops.load(10, 0, P_y)
# endregion

# region Parametryzacja
cov = 0.1
ops.analysis('Static')

ops.randomVariable(1, 'lognormal', '-mean', P_x, cov * P_x)
ops.randomVariable(2, 'lognormal', '-mean', P_y, cov * P_y)
ops.randomVariable(3, 'lognormal', '-mean', A, cov * A)
ops.randomVariable(4, 'lognormal', '-mean', E, cov * E)

ops.parameter(1, 'loadPattern', 1, 'loadAtNode', 6, 1)
ops.parameter(2, 'loadPattern', 1, 'loadAtNode', 6, 2)
ops.parameter(3, 'element', 1, 'A')
ops.parameter(4, 'element', 1, 'E')

ops.addToParameter(2, 'loadPattern', 1, 'loadAtNode', 7, 2)
ops.addToParameter(2, 'loadPattern', 1, 'loadAtNode', 8, 2)
ops.addToParameter(2, 'loadPattern', 1, 'loadAtNode', 9, 2)
ops.addToParameter(2, 'loadPattern', 1, 'loadAtNode', 10, 2)

for i in range(2, 18):
    ops.addToParameter(3, 'element', i, 'A')

ops.probabilityTransformation('Nataf', '-print', 0)
# endregion

# region Obliczenia i wyniki
nFail = 0
nTrials = 10000
u_sims = np.zeros(nTrials)

calculate(nTrials, 3, 2, u_sims)

show_results(nFail, nTrials, u_sims, 'Ugięcie na środku ramy')
# endregion

exit()
