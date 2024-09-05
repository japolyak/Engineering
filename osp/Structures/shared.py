import numpy as np
import openseespy.opensees as ops
import matplotlib.pyplot as plt
from scipy.stats import norm
import opsvis as opsv
import os

def calculate(n_trials, node_tag, dof, u_sims):
    nrv = len(ops.getRVTags())

    for i in range(n_trials):
        ops.reset()

        u = list(norm.rvs(size=nrv))
        x = ops.transformUtoX(*u)

        [ops.updateParameter(index + 1, x[index]) for index, _ in enumerate(x)]

        ops.analyze(1)

        u_sims[i] = ops.nodeDisp(node_tag, dof)


def save_results(n_fail: int, n_trials: int, u_sims, structure_name: str):
    m_cpf = n_fail / n_trials

    u_max = np.max(u_sims)
    u_min = np.min(u_sims)
    u_mean = np.mean(u_sims)
    u_std = np.std(u_sims)
    u_var = np.var(u_sims)
    u_cov = u_std/u_mean

    save_dir = os.path.join('.')

    with open(os.path.join(save_dir, f"{structure_name}_{n_trials}_results.txt"), "w") as file:
        file.write(f'Monte Carlo symulacja dla {structure_name}, pf_MC = {n_fail} / {n_trials} = {m_cpf}\n')
        file.write(f'u_max: {u_max}\n')
        file.write(f'u_min: {u_min}\n')
        file.write(f'u_mean: {u_mean}\n')
        file.write(f'u_std: {u_std}\n')
        file.write(f'u_var: {u_var}\n')
        file.write(f'u_cov: {u_cov}\n')

    width_in_inches = 1920 * 1.35 / 300
    height_in_inches = 1080 * 1.35 / 300

    plt.figure(figsize=(width_in_inches, height_in_inches), dpi=300)
    opsv.plot_model()
    plt.savefig(os.path.join(save_dir, f'{structure_name}_model.png'), dpi=300, bbox_inches='tight')

    plt.figure(figsize=(width_in_inches, height_in_inches), dpi=300)
    opsv.plot_defo()
    plt.savefig(os.path.join(save_dir, f'{structure_name}_deformation.png'), dpi=300, bbox_inches='tight')

    plt.figure(figsize=(width_in_inches, height_in_inches), dpi=300)
    plt.plot(u_sims)
    plt.axhline(u_mean, 0, 1, color='b', lw=0.6)
    plt.xlabel('liczba symulacji N')
    plt.ylabel('Przemieszczenie [m]')
    plt.ylim(u_min - 0.1 * u_min, u_max + 0.1 * u_max)
    plt.savefig(os.path.join(save_dir, f'{structure_name}_{n_trials}_sp.png'), dpi=300, bbox_inches='tight')

    u_mean_cum = np.cumsum(u_sims)/np.arange(1, n_trials + 1)
    plt.figure(figsize=(width_in_inches, height_in_inches), dpi=300)
    plt.plot(u_mean_cum)
    plt.axhline(u_mean, 0, 1, color='r', lw=1.2)
    plt.xlabel('Liczba symulacji N')
    plt.ylabel('Wartość średnia przemieszczenia [m]')
    plt.savefig(os.path.join(save_dir, f'{structure_name}_{n_trials}_zsp.png'), dpi=300, bbox_inches='tight')

    u_std_cum = [u_sims[:x].std() for x in range(1, n_trials + 1)]
    plt.figure(figsize=(width_in_inches, height_in_inches), dpi=300)
    plt.plot(u_std_cum)
    plt.axhline(u_std, 0, 1, color='r', lw=1.2)
    plt.xlabel('Liczba symulacji N')
    plt.ylabel('Odchylenie standardowe przemieszczenia [m]')
    plt.savefig(os.path.join(save_dir, f'{structure_name}_{n_trials}_zos.png'), dpi=300, bbox_inches='tight')
