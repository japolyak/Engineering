import numpy as np
import openseespy.opensees as ops
from shared import save_results, calculate


ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

L = 3.0
b = 0.3
d = 2.0 * b
A = b * d
I_z = (b * d ** 3) / 12

E = 30.0e6

P = -10.0
q = -5.0

ops.node(1, 0.0, 0.0)
ops.node(2, L, 0.0)
ops.node(3, L * 2.0, 0.0)
ops.node(4, L * 3.0, 0.0)

ops.fix(1, 1, 1, 0)
ops.fix(2, 1, 1, 0)
ops.fix(3, 0, 1, 0)

ops.geomTransf('Linear', 1)

ops.element('elasticBeamColumn', 1, 1, 2, A, E, I_z, 1)
ops.element('elasticBeamColumn', 2, 2, 3, A, E, I_z, 1)
ops.element('elasticBeamColumn', 3, 3, 4, A, E, I_z, 1)

ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(4, 0, P, 0)

ops.eleLoad('-ele', 1, '-type', '-beamUniform', q)

cov = 0.1
ops.analysis('Static')

ops.randomVariable(1, 'lognormal', '-mean', I_z, cov * I_z)
ops.randomVariable(2, 'lognormal', '-mean', E, cov * E)
ops.randomVariable(3, 'lognormal', '-mean', P, cov * P)
ops.randomVariable(4, 'lognormal', '-mean', q, cov * q)

ops.parameter(1, 'element', 1, 'I')
ops.parameter(2, 'element', 1, 'E')
ops.parameter(3, 'loadPattern', 1, 'loadAtNode', 4, 2)
ops.parameter(4, 'loadPattern', 1, 'elementLoad', 1, 'wy')

ops.addToParameter(1, 'element', 2, 'I')
ops.addToParameter(1, 'element', 3, 'I')
ops.addToParameter(2, 'element', 2, 'E')
ops.addToParameter(2, 'element', 3, 'E')

ops.probabilityTransformation('Nataf', '-print', 0)

n_fail = 0
n_trials = 1000000
u_sims = np.zeros(n_trials)

calculate(n_trials, 4, 2, u_sims)

save_results(n_fail, n_trials, u_sims, 'Belka')
