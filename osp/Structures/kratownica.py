import numpy as np
import openseespy.opensees as ops
from shared import save_results, calculate


ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 2)

a = 3.0
b = 4.0
c = 5.0

E_1 = 30.0e6
A_1 = 0.3
E_2 = 40.0e6
A_2 = 0.2
E_3 = 50.0e6
A_3 = 0.1

P_x = 15.0
P_y = - 5.0

ops.node(1, 0.0, 0.0)
ops.node(2, a, 0.0)
ops.node(3, a + b, 0.0)
ops.node(4, a, -c)

ops.fix(1, 1, 1)
ops.fix(2, 1, 1)
ops.fix(3, 1, 1)

ops.uniaxialMaterial('Elastic', 1, E_1)
ops.uniaxialMaterial('Elastic', 2, E_2)
ops.uniaxialMaterial('Elastic', 3, E_3)

ops.element('truss', 1, 1, 4, A_1, 1)
ops.element('truss', 2, 2, 4, A_2, 2)
ops.element('truss', 3, 3, 4, A_3, 3)

ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(4, P_x, P_y)

cov = 0.1
ops.analysis('Static')

ops.randomVariable(1, 'lognormal', '-mean', P_x, cov * P_x)
ops.randomVariable(2, 'lognormal', '-mean', P_y, cov * P_y)
ops.randomVariable(3, 'lognormal', '-mean', A_1, cov * A_1)
ops.randomVariable(4, 'lognormal', '-mean', A_2, cov * A_2)
ops.randomVariable(5, 'lognormal', '-mean', A_3, cov * A_3)

ops.parameter(1, 'loadPattern', 1, 'loadAtNode', 4, 1)
ops.parameter(2, 'loadPattern', 1, 'loadAtNode', 4, 2)
ops.parameter(3, 'element', 1, 'A')
ops.parameter(4, 'element', 2, 'A')
ops.parameter(5, 'element', 3, 'A')

ops.probabilityTransformation('Nataf', '-print', 0)

nFail = 0
nTrials = 1000000
u_sims = np.zeros(nTrials)

calculate(nTrials, 4, 2, u_sims)

save_results(nFail, nTrials, u_sims, 'Kratownica')
