import openseespy.opensees as ops
from scipy.stats import norm

meanR, sigR = 2000, 135  # Resistance
meanS, sigS = 1700, 200  # Load

ops.randomVariable(1, 'normal', '-mean', meanR, '-stdv', sigR)
ops.randomVariable(2, 'normal', '-mean', meanS, '-stdv', sigS)

# pf ~ 0.04 or ~ 0.1 if commented (uncorrelated RVs)
ops.correlate(1, 2, 0.5)
ops.probabilityTransformation('Nataf')

nrv = len(ops.getRVTags())
nTrials = 50000
nFail = 0
for i in range(nTrials):
    U = list(norm.rvs(size=nrv))  # RVs on N(0,1)
    X = ops.transformUtoX(*U)
    r = X[0]
    s = X[1]

    g = r-s
    if (g <= 0.0):
        nFail += 1

MCpf = nFail / nTrials
print(f'Monte Carlo simulation, pf_MC = {nFail} / {nTrials} = {MCpf}')

exit()
