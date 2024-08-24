# Instalacja modułów
import openseespy.opensees as ops
import opsvis as opsv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Definicja przestrzeni i stopni swobody
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Definicja węzłów
ops.node(1, 0.0, 0.0)
ops.node(2, 3.0, 0.0)
ops.node(3, 6.0, 0.0)

# Definicja podpór
ops.fix(1, 1, 1, 0)
ops.fix(3, 0, 1, 0)

E = 30.0e6
A = 0.06
Iz = 0.00045
# wspolczynniki zmiennosci: std = cov * mu:
# odch. std. = wsp. zmien * średnia
covj = 0.12
covd = 0.12

ops.geomTransf('Linear', 1)

# Definicja elementów
ops.element('elasticBeamColumn', 1, 1, 2, A, E, Iz, 1)
ops.element('elasticBeamColumn', 2, 2, 3, A, E, Iz, 1)

# Definicja siły skupionej
P = -10.0
ops.timeSeries('Constant', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 0, P, 0)

ops.analysis('Static')

# definicja zmiennych losowych mean - wartość średnia, std - odch. standardowe.
ops.randomVariable(1, 'lognormal', '-mean', E, '-stdv', covj*E)
ops.randomVariable(2, 'lognormal', '-mean', E, '-stdv', covd*E)

# uwzględnienie ew. korelacji między zmiennymi losowymi
ops.correlate(1, 2, 0.0)  # brak korelacji

# przypisanie zmiennych losowych do parametrów i elementów
ops.parameter(1, 'element', 1, 'E')
ops.parameter(2, 'element', 2, 'E')

ops.probabilityTransformation('Nataf', '-print', 0)

ops.printModel()
opsv.plot_model()

# nTrials = 100000
# nTrials = 10000

nTrials = 1000
nFail = 0

rvTags = ops.getRVTags()
paramTags = ops.getParamTags()
nrv = len(rvTags)
print(f'rvTags: {rvTags}')
print(f'paramTags: {paramTags}')

u_sims = np.zeros(nTrials)
# u_mean_cum = np.zeros(nTrials)

for i in range(nTrials):
    ops.reset()

    U = list(norm.rvs(size=nrv))
    X = ops.transformUtoX(*U)
    ops.updateParameter(1, X[0])
    ops.updateParameter(2, X[1])

    ops.analyze(1)
    u2y = ops.nodeDisp(2, 2)
    u_sims[i] = u2y

opsv.plot_defo()

MCpf = nFail / nTrials
print(f'Monte Carlo simulation, pf_MC = {nFail} / {nTrials} = {MCpf}')

# statystyka wyników
u_max = np.max(u_sims)
u_min = np.min(u_sims)
u_mean = np.mean(u_sims)
u_std = np.std(u_sims)
u_var = np.var(u_sims)
u_cov = u_std/u_mean
print(f'u_max: {u_max}')
print(f'u_min: {u_min}')
print(f'u_mean: {u_mean}')
print(f'u_std: {u_std}')
print(f'u_var: {u_var}')
print(f'u_cov: {u_cov}')

plt.figure()
plt.plot(u_sims)
plt.axhline(u_mean, 0, 1, color='b', lw=0.6)
# plt.axhline(u_mean-u_std, 0, 1, color='r', lw=0.6)
# plt.axhline(u_mean+u_std, 0, 1, color='r', lw=0.6)
# plt.axhline(ulim, 0, 1, color='r', lw=1.2)
# plt.title('Displacement at midspan')
plt.title('Ugięie w środku rozpiętości belki')
plt.xlabel('liczba symulacji N')
plt.ylabel('przemieszczenie [m]')
plt.ylim(1.1*u_min, 0)
# plt.show()

u_mean_cum = np.cumsum(u_sims)/np.arange(1, nTrials+1)
plt.figure()
plt.plot(u_mean_cum)
plt.axhline(u_mean, 0, 1, color='r', lw=1.2)
plt.title('Zbieżność wartości średniej przemieszczenia')
plt.xlabel('liczba symulacji N')
plt.ylabel('wartość średnia przemieszczenia [m]')
# plt.show()

# std
u_std_cum = [u_sims[:x].std() for x in range(1, nTrials+1)]
# u_mean_cum = np.cumsum(u_sims)/np.arange(1, nTrials+1)
plt.figure()
plt.plot(u_std_cum)
plt.axhline(u_std, 0, 1, color='r', lw=1.2)
# plt.title('Standard deviation')
plt.title('Zbieżność odchylenia standardowego')
plt.xlabel('liczba symulacji N')
plt.ylabel('odchylenie standardowe przemieszczenia [m]')

plt.show()


ops.printModel()

# Monte Carlo simulation end
# --------------------------

exit()
