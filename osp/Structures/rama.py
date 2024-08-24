import numpy as np
import openseespy.opensees as ops
from shared import save_results, calculate


ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# region Liczby losowe
L = 3.0
H = 4.0

b = 0.3
d = 2.0 * b
A = b * d
I_z = (b * d ** 3) / 12
E = 30.0e6

P_1 = 150
P_2 = -50
# endregion

# region Węzły
ops.node(1, 0.0, 0.0)
ops.node(2, L, 0.0)
ops.node(3, 0, H)
ops.node(4, L / 2, H)
ops.node(5, L, H)
# endregion

# region Podpory
ops.fix(1, 1, 1, 0)
ops.fix(2, 1, 1, 1)
# endregion

# region Elementy
ops.geomTransf('Linear', 1)

ops.element('elasticBeamColumn', 1, 1, 3, A, E, I_z, 1)
ops.element('elasticBeamColumn', 2, 3, 4, A, E, I_z, 1)
ops.element('elasticBeamColumn', 3, 4, 5, A, E, I_z, 1)
ops.element('elasticBeamColumn', 4, 5, 2, A, E, I_z, 1)
# endregion

# region Siły
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(3, P_1, 0, 0)
ops.load(4, 0, P_2, 0)
# endregion

# region Parametryzacja
cov = 0.1
ops.analysis('Static')

ops.randomVariable(1, 'lognormal', '-mean', P_1, cov * P_1)
ops.randomVariable(2, 'lognormal', '-mean', P_2, cov * P_2)
ops.randomVariable(3, 'lognormal', '-mean', I_z, cov * I_z)
ops.randomVariable(4, 'lognormal', '-mean', E, cov * E)

ops.parameter(1, 'loadPattern', 1, 'loadAtNode', 3, 1)
ops.parameter(2, 'loadPattern', 1, 'loadAtNode', 4, 2)
ops.parameter(3, 'element', 1, 'I')
ops.parameter(4, 'element', 1, 'E')

ops.addToParameter(3, 'element', 2, 'I')
ops.addToParameter(3, 'element', 3, 'I')
ops.addToParameter(4, 'element', 2, 'E')
ops.addToParameter(4, 'element', 3, 'E')

ops.probabilityTransformation('Nataf', '-print', 0)
# endregion

# region Obliczenia i wyniki
nFail = 0
nTrials = 10000
u_sims = np.zeros(nTrials)

calculate(nTrials, 4, 2, u_sims)

save_results(nFail, nTrials, u_sims, 'Ugięcie środka belki', 'Rama')
# endregion

exit()
