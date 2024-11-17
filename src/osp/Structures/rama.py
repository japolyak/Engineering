import numpy as np
import openseespy.opensees as ops
from shared import save_results, calculate


ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

L = 3.0
H = 4.0

b = 0.3
d = 2.0 * b
A = b * d
I_z = (b * d ** 3) / 12
E = 30.0e6

P_1 = 25
P_2 = -500

ops.node(1, 0.0, 0.0)
ops.node(2, 0, H)
ops.node(3, L, H)
ops.node(4, L, 0.0)

ops.fix(1, 1, 1, 0)
ops.fix(4, 1, 1, 1)

ops.geomTransf('Linear', 1)

ops.element('elasticBeamColumn', 1, 1, 2, A, E, I_z, 1)
ops.element('elasticBeamColumn', 2, 2, 3, A, E, I_z, 1)
ops.element('elasticBeamColumn', 3, 3, 4, A, E, I_z, 1)

ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, P_1, P_2, 0)

cov = 0.1
ops.analysis('Static')

ops.randomVariable(1, 'lognormal', '-mean', P_1, cov * P_1)
ops.randomVariable(2, 'lognormal', '-mean', P_2, cov * P_2)
ops.randomVariable(3, 'lognormal', '-mean', I_z, cov * I_z)
ops.randomVariable(4, 'lognormal', '-mean', E, cov * E)

ops.parameter(1, 'loadPattern', 1, 'loadAtNode', 2, 1)
ops.parameter(2, 'loadPattern', 1, 'loadAtNode', 2, 2)

ops.parameter(3, 'element', 1, 'I')
ops.parameter(4, 'element', 1, 'E')

ops.parameter(5, 'element', 2, 'I')
ops.parameter(6, 'element', 2, 'E')

ops.parameter(7, 'element', 3, 'I')
ops.parameter(8, 'element', 3, 'E')

ops.probabilityTransformation('Nataf', '-print', 0)

n_fail = 0
n_trials = 1000000
u_sims = np.zeros(n_trials)

calculate(n_trials, 2, 1, u_sims)

save_results(n_fail, n_trials, u_sims, 'Rama', 'mm', 0.001)
