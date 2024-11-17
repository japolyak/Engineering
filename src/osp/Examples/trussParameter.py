import openseespy.opensees as ops
import ops_utils as opsu
import opsvisu as opsv
import numpy as np

# 2 element truss bar with roller support and horizontal force P
# Goal: calculate the bar with specified parameters then update parameters and recalculate
#       'static' 'disp'lacement. Compare the results before and after update
#
# /|1 EA  2  EA  3
# /|======+======+ --> P=25N
# /|  10m o  10m o

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 2)
# ops.reliability()

L = 20.0
E = 30000.0
A = 5.0
P = 25.0

ops.node(1, 0.0, 0.0)
ops.node(2, 0.5*L, 0.0)
ops.node(3, L, 0.0)

ops.fix(1, 1, 1)
ops.fix(2, 0, 1)
ops.fix(3, 0, 1)

ops.uniaxialMaterial('Elastic', 1, E)

ops.element('truss', 1, 1, 2, A, 1)
ops.element('truss', 2, 2, 3, A, 1)

ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(3, P, 0.0)

# - define parameters
# Material property of an element
ops.parameter(1, 'element', 1, 'E', 'Area', 'One')
ops.addToParameter(1, 'element', 2, 'E')

# Element property
ops.parameter(2, 'element', 2, 'A')
ops.addToParameter(2, 'element', 1, 'A')

# Nodal load
ops.parameter(3, 'loadPattern', 1, 'loadAtNode', 3, 1)

# Nodal coordinate
ops.parameter(4, 'node', 3, 'coord', 1)


ops.analysis('Static')

ops.analyze(1)

U = ops.nodeDisp(3, 1)
print(f'\nTruss deflection before update: {U}')

# Perturb parameters relative to their original values
ops.updateParameter(1, 0.95*E)
ops.updateParameter(2, 1.05*A)
ops.updateParameter(3, 1.05*P)
ops.updateParameter(4, 0.95*L)

ops.analyze(1)

U = ops.nodeDisp(3, 1)
print(f'Truss deflection after update: {U}')

exit()
