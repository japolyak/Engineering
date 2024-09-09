def calculate(n_trials, node_tag, dof, u_sims):
    import openseespy.opensees as ops
    from scipy.stats import norm

    nrv = len(ops.getRVTags())

    for i in range(n_trials):
        ops.reset()

        u = list(norm.rvs(size=nrv))
        x = ops.transformUtoX(*u)

        [ops.updateParameter(index + 1, x[index]) for index, _ in enumerate(x)]

        ops.analyze(1)

        u_sims[i] = ops.nodeDisp(node_tag, dof)


def save_figure(values, mean, y_label: str, file_name: str, from_opsv: bool = False, opsv_fig: str = 'mod'):
    import matplotlib.pyplot as plt
    import opsvis as opsv
    import os

    dpi = 300
    save_dir = os.path.join('.')
    width_in_inches = 1920 * 1.35 / dpi
    height_in_inches = 1080 * 1.35 / dpi

    plt.figure(figsize=(width_in_inches, height_in_inches), dpi=dpi)

    if from_opsv:
        if opsv_fig == 'mod':
            opsv.plot_model()
        else:
            opsv.plot_defo()
    else:
        plt.plot(values)
        plt.axhline(mean, 0, 1, color='r', lw=1.2)
        plt.xlabel('Liczba symulacji N')
        plt.ylabel(y_label)

    plt.savefig(os.path.join(save_dir, f'{file_name}.png'), dpi=dpi, bbox_inches='tight')


def save_results(n_fail: int, n_trials: int, u_sims, structure_name: str, u_units: str, units_converter: float = 1.0):
    import numpy as np
    import os

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

    if units_converter > 1:
        u_sims = u_sims / units_converter
        u_mean = u_mean / units_converter
        u_std = u_std / units_converter

    save_figure([], None, '', f'{structure_name}_model', True)

    save_figure([], None, '', f'{structure_name}_deformation', True, 'defo')

    save_figure(u_sims, u_mean, f'Przemieszczenie [{u_units}]', f'{structure_name}_{n_trials}_sp')

    u_mean_cum = np.cumsum(u_sims)/np.arange(1, n_trials + 1)
    save_figure(u_mean_cum, u_mean, f'Wartość średnia przemieszczenia [{u_units}]', f'{structure_name}_{n_trials}_zsp')

    u_std_cum = [u_sims[:x].std() for x in range(1, n_trials + 1)]
    save_figure(u_std_cum, u_std, f'Odchylenie standardowe przemieszczenia [{u_units}]', f'{structure_name}_{n_trials}_zos')
