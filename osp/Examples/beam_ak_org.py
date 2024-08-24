import openseespy.opensees as ops
import opsvis as opsv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

ops.model('basic', '-ndm', 2, '-ndf', 3)

# region Liczby losowe
L = 3.0
b = 0.3
d = 2.0 * b
A = b * d
I_z = (b * d ** 3) / 12

E = 30.0e6

P = -10.0
q = -5.0
# endregion

# Węzły
ops.node(1, 0.0, 0.0)
ops.node(2, L, 0.0)
ops.node(3, L * 2.0, 0.0)
ops.node(4, L * 3.0, 0.0)

# Podpory
ops.fix(1, 1, 1, 0)
ops.fix(2, 1, 1, 0)
ops.fix(3, 0, 1, 0)

ops.geomTransf('Linear', 1)

# Elementy
ops.element('elasticBeamColumn', 1, 1, 2, A, E, I_z, 1)
ops.element('elasticBeamColumn', 2, 2, 3, A, E, I_z, 1)
ops.element('elasticBeamColumn', 3, 3, 4, A, E, I_z, 1)

# Siła skupiona w 4 węźle
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(4, 0, P, 0)

# Obciążenie rozłożone stałe na 1-ym elemencie
ops.eleLoad('-ele', 1, '-type', '-beamUniform', q)

ops.analysis('Static')

cov = 0.1
# ops.randomVariable(1, 'lognormal', '-mean', b, cov * b)
# ops.randomVariable(2, 'lognormal', '-mean', d, cov * d)
ops.randomVariable(2, 'lognormal', '-mean', I_z, cov * I_z)
ops.randomVariable(3, 'lognormal', '-mean', E, cov * E)
ops.randomVariable(4, 'lognormal', '-mean', P, cov * P)
ops.randomVariable(5, 'lognormal', '-mean', q, cov * q)

# ops.parameter(1, 'element', 3, 'P')
ops.parameter(1, 'loadPattern', 1, 'loadAtNode', 4, 2)
ops.parameter(2, 'loadPattern', 1, 'elementLoad', 1, 'wy')
ops.parameter(3, 'element', 1, 'I')
ops.addToParameter(3, 'element', 2, 'I')
ops.addToParameter(3, 'element', 3, 'I')

ops.analyze(1)

ops.printModel()

opsv.plot_model()
opsv.plot_loads_2d()
opsv.plot_defo()

plt.show()
exit()
