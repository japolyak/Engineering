import numpy as np
import openseespy.opensees as ops
import matplotlib.pyplot as plt
from scipy.stats import norm
import opsvis as opsv


def calculate(n_trials, node_tag, dof, u_sims):
    nrv = len(ops.getRVTags())

    for i in range(n_trials):
        ops.reset()

        u = list(norm.rvs(size=nrv))
        x = ops.transformUtoX(*u)

        [ops.updateParameter(index + 1, x[index]) for index, _ in enumerate(x)]

        ops.analyze(1)

        u_sims[i] = ops.nodeDisp(node_tag, dof)


def save_results(n_fail: int, n_trials: int, u_sims, u_title: str, structure_name: str):
    m_cpf = n_fail / n_trials

    u_max = np.max(u_sims)
    u_min = np.min(u_sims)
    u_mean = np.mean(u_sims)
    u_std = np.std(u_sims)
    u_var = np.var(u_sims)
    u_cov = u_std/u_mean

    with open(f"{structure_name}_{n_trials}_results.txt", "w") as file:
        file.write(f'Monte Carlo symulacja dla {structure_name}, pf_MC = {n_fail} / {n_trials} = {m_cpf}\n')
        file.write(f'u_max: {u_max}\n')
        file.write(f'u_min: {u_min}\n')
        file.write(f'u_mean: {u_mean}\n')
        file.write(f'u_std: {u_std}\n')
        file.write(f'u_var: {u_var}\n')
        file.write(f'u_cov: {u_cov}\n')

    plt.figure()
    opsv.plot_model()
    plt.title(f'Model konstrukcji: {structure_name}')
    plt.savefig(f'{structure_name}_model.png', dpi=300)

    plt.figure()
    opsv.plot_defo()
    plt.title(f'Deformacja konstrukcji: {structure_name}')
    plt.savefig(f'{structure_name}_{n_trials}_def.png', dpi=300)

    plt.figure()
    plt.plot(u_sims)
    plt.axhline(u_mean, 0, 1, color='b', lw=0.6)
    plt.title(u_title)
    plt.xlabel('liczba symulacji [N]')
    plt.ylabel('Przemieszczenie [m]')
    plt.ylim(1.1 * u_min, 0)
    plt.savefig(f'{structure_name}_{n_trials}_sp.png', dpi=300)

    u_mean_cum = np.cumsum(u_sims)/np.arange(1, n_trials + 1)
    plt.figure()
    plt.plot(u_mean_cum)
    plt.axhline(u_mean, 0, 1, color='r', lw=1.2)
    plt.title('Zbieżność wartości średniej przemieszczenia')
    plt.xlabel('Liczba symulacji [N]')
    plt.ylabel('Wartość średnia przemieszczenia [m]')
    plt.savefig(f'{structure_name}_{n_trials}_zsp.png', dpi=300)

    u_std_cum = [u_sims[:x].std() for x in range(1, n_trials + 1)]
    plt.figure()
    plt.plot(u_std_cum)
    plt.axhline(u_std, 0, 1, color='r', lw=1.2)
    plt.title('Zbieżność odchylenia standardowego')
    plt.xlabel('Liczba symulacji [N]')
    plt.ylabel('Odchylenie standardowe przemieszczenia [m]')
    plt.savefig(f'{structure_name}_{n_trials}_zos.png', dpi=300)
