import openseespy.opensees as ops
from scipy.stats import norm
import opsvis as opsv
import matplotlib.pyplot as plt

meanR = 2000
sigR = 135  # Resistance
meanS = 1700
sigS = 200  # Load

ops.randomVariable(1, 'normal', '-mean', meanR, '-stdv', sigR)
ops.randomVariable(2, 'normal', '-mean', meanS, '-stdv', sigS)

# pf ~ 0.04 or ~ 0.1 if commented (uncorrelated RVs)
ops.correlate(1, 2, 0.5)
ops.probabilityTransformation('Nataf')

ops.wipe()
ops.model('basic', '-ndm', 1)

ops.node(1, 0)
ops.fix(1, 1)
ops.node(2, 1)

# opsv.plot_model()
# plt.show()

k = 1000  # Bar stiffness (doesn't really matter)
ops.uniaxialMaterial('Hardening', 1, k, meanR, 0, 0.01*k)
ops.element('truss', 1, 1, 2, 1.0, 1)

ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, meanS)

ops.parameter(1, 'element', 1, 'Fy')
ops.parameter(2, 'loadPattern', 1, 'loadAtNode', 2, 1)

ops.analysis('Static')

nrv = len(ops.getRVTags())
nTrials = 50000
nFail = 0
for i in range(nTrials):
    ops.reset()

    U = list(norm.rvs(size=nrv))
    X = ops.transformUtoX(*U)
    r = X[0]
    s = X[1]
    ops.updateParameter(1, r)
    ops.updateParameter(2, s)

    ops.analyze(1)

    g = r/k - ops.nodeDisp(2, 1)
    if (g <= 0.0):
        nFail += 1

MCpf = nFail / nTrials
print(f'Monte Carlo simulation, pf_MC = {nFail} / {nTrials} = {MCpf}')

exit()
