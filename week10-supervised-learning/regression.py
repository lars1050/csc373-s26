import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.optimize import minimize


# ── Data loading ───────────────────────────────────────────────────────────────

def load_data(filepath, x_cols, y_col):
    df = pd.read_csv(filepath)
    X = df[x_cols].values.astype(float)
    y = df[y_col].values.astype(float)
    return X, y


# ── Model ──────────────────────────────────────────────────────────────────────

def predict(params, X):
    """Predict y values given params [b, m1, m2, ...] and feature matrix X."""
    b = params[0]
    m = params[1:]
    return X @ m + b


# ── Loss functions ─────────────────────────────────────────────────────────────

def loss_l0(params, X, y):
    residuals = y - predict(params, X)
    return -np.sum(residuals == 0)

def loss_l1(params, X, y):
    residuals = y - predict(params, X)
    return np.sum(np.abs(residuals))

def loss_l2(params, X, y):
    residuals = y - predict(params, X)
    return np.sum(residuals ** 2)

def loss_linf(params, X, y):
    residuals = y - predict(params, X)
    return np.max(np.abs(residuals))


LOSS_FUNCTIONS = {
    'L0':   loss_l0,
    'L1':   loss_l1,
    'L2':   loss_l2,
    'Linf': loss_linf,
}


# ── Fitting ────────────────────────────────────────────────────────────────────

def fit(X, y, loss_name):
    """
    Fit a linear model to X and y using the specified loss function.

    Parameters
    ----------
    X : np.ndarray, shape (n_samples, n_features)
    y : np.ndarray, shape (n_samples,)
    loss_name : str -- one of 'L0', 'L1', 'L2', 'Linf'

    Returns
    -------
    params : np.ndarray -- [intercept, coef1, coef2, ...]
    """
    loss_fn = LOSS_FUNCTIONS[loss_name]
    X_aug = np.column_stack([np.ones(len(y)), X])

    if loss_name == 'L2':
        params, _, _, _ = np.linalg.lstsq(X_aug, y, rcond=None)
        return params

    params0, _, _, _ = np.linalg.lstsq(X_aug, y, rcond=None)
    result = minimize(loss_fn, x0=params0, args=(X, y),
                      method='Nelder-Mead',
                      options={'maxiter': 100000, 'xatol': 1e-8, 'fatol': 1e-8})
    return result.x


# ── PCA helper ─────────────────────────────────────────────────────────────────

def _pca_reduce(X, n_components=2):
    """
    Reduce X to n_components using PCA.

    Returns
    -------
    X_reduced  : np.ndarray, shape (n_samples, n_components)
    components : np.ndarray, shape (n_features, n_components)  -- projection matrix
    mean       : np.ndarray, shape (n_features,)               -- column means of X
    explained  : np.ndarray, shape (n_components,)             -- fraction of variance explained
    """
    X_centered = X - X.mean(axis=0)
    cov = np.cov(X_centered.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = eigvecs[:, :n_components]
    X_reduced = X_centered @ components
    explained = eigvals[:n_components] / eigvals.sum()
    return X_reduced, components, X.mean(axis=0), explained


# ── Plotting ───────────────────────────────────────────────────────────────────

def plot_results(X, y, fits, x_cols, title="Linear regression", save_path='regression_results.png'):
    """
    Plot regression results.

    1 feature  -> 2D scatter + regression line.
    2 features -> 3D scatter + regression plane (exact).
    3+ features -> 3D scatter + regression plane (PCA-projected to 2 components).

    Parameters
    ----------
    X         : np.ndarray, shape (n_samples, n_features)
    y         : np.ndarray, shape (n_samples,)
    fits      : dict  { loss_name: params_array }
    x_cols    : list[str] -- feature column names
    title     : str
    save_path : str or None -- path to save PNG (None to skip saving)
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    colors = {'L0': '#E24B4A', 'L1': '#EF9F27', 'L2': '#378ADD', 'Linf': '#1D9E75'}
    n_features = X.shape[1]
    n_samples = len(y)

    # Select at most 20 points at random for plotting
    max_plot_points = 20
    if n_samples > max_plot_points:
        plot_idx = np.random.choice(n_samples, size=max_plot_points, replace=False)
    else:
        plot_idx = np.arange(n_samples)

    use_3d = n_features >= 2

    # For 3+ features: project down to 2D via PCA (computed once, shared across subplots)
    pca_note = None
    pca_components = None
    pca_mean = None
    if n_features > 2:
        X_2d, pca_components, pca_mean, explained = _pca_reduce(X, n_components=2)
        pca_note = (f'Axes are PCA components '
                    f'({explained[0]*100:.1f}% + {explained[1]*100:.1f}% = '
                    f'{(explained[0]+explained[1])*100:.1f}% variance explained)')
    else:
        X_2d = X  # 1 or 2 features, use directly

    fig = plt.figure(figsize=(5 * len(fits), 5))

    for i, (loss_name, params) in enumerate(fits.items()):
        color = colors.get(loss_name, '#378ADD')
        y_pred = predict(params, X)
        b = params[0]
        m = params[1:]

        if use_3d:
            ax = fig.add_subplot(1, len(fits), i + 1, projection='3d')
        else:
            ax = fig.add_subplot(1, len(fits), i + 1)

        # Subset for scatter
        X2d_plot = X_2d[plot_idx]
        y_plot   = y[plot_idx]
        res_plot = (y - y_pred)[plot_idx]

        if n_features == 1:
            # ── 2D: scatter + regression line ─────────────────────────────
            x_vals = X2d_plot[:, 0]
            x_line = np.linspace(X_2d[:, 0].min(), X_2d[:, 0].max(), 200)
            ax.scatter(x_vals, y_plot, color='#888780', zorder=3, s=50, label='Data')
            ax.plot(x_line, m[0] * x_line + b, color=color, linewidth=2,
                    label=f'y = {m[0]:.3f}x + {b:.3f}')
            for xi, yi, ri in zip(x_vals, y_plot, res_plot):
                ax.plot([xi, xi], [yi, yi - ri], color=color, alpha=0.3, linewidth=1)
            ax.set_xlabel(x_cols[0])
            ax.set_ylabel('y')
            ax.set_title(f'{loss_name}  |  m={m[0]:.3f}, b={b:.3f}', fontsize=10)

        else:
            # ── 3D: scatter + regression plane ────────────────────────────
            # Project regression coefficients into the 2D space.
            # Original model: y = m @ x + b
            # In PCA space z: x = P @ z + mean, so y = m @ (P @ z + mean) + b
            #                                          = (m @ P) @ z + (m @ mean + b)
            if n_features > 2:
                m_2d = m @ pca_components
                b_2d = float(m @ pca_mean) + b
                x_label, y_label = 'PC1', 'PC2'
            else:
                m_2d = m
                b_2d = b
                x_label, y_label = x_cols[0], x_cols[1]

            # Grid for regression plane
            g1 = np.linspace(X_2d[:, 0].min(), X_2d[:, 0].max(), 20)
            g2 = np.linspace(X_2d[:, 1].min(), X_2d[:, 1].max(), 20)
            G1, G2 = np.meshgrid(g1, g2)
            Z = m_2d[0] * G1 + m_2d[1] * G2 + b_2d

            # Scatter
            ax.scatter(X2d_plot[:, 0], X2d_plot[:, 1], y_plot,
                       color='#888780', s=50, zorder=3, label='Data')

            # Regression plane
            ax.plot_surface(G1, G2, Z, color=color, alpha=0.35)

            # Residual lines dropped to the plane
            for x1, x2, ya in zip(X2d_plot[:, 0], X2d_plot[:, 1], y_plot):
                yp_proj = m_2d[0] * x1 + m_2d[1] * x2 + b_2d
                ax.plot([x1, x1], [x2, x2], [ya, yp_proj],
                        color=color, alpha=0.4, linewidth=1)

            ax.set_xlabel(x_label, fontsize=8)
            ax.set_ylabel(y_label, fontsize=8)
            ax.set_zlabel('y', fontsize=8)
            coef_str = ', '.join(f'{col}:{mi:.3f}' for col, mi in zip(x_cols, m))
            ax.set_title(f'{loss_name}\nb={b:.3f} | {coef_str}', fontsize=8)

        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.2)

    sup = title
    if pca_note:
        sup += f'\n{pca_note}'
    fig.suptitle(sup, fontsize=11, y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()
    return fig


# ── Public API ─────────────────────────────────────────────────────────────────

def run_regression(X, y, x_cols=None, loss='L2', plot=True,
                   save_path='regression_results.png', title='Linear regression'):
    """
    Fit linear regression and optionally plot results.

    Parameters
    ----------
    X         : np.ndarray, shape (n_samples, n_features)
                Feature matrix.
    y         : np.ndarray, shape (n_samples,)
                Target values.
    x_cols    : list[str], optional
                Feature names used in plot labels. Defaults to ['x0', 'x1', ...].
    loss      : str or list[str]
                Loss function(s) to use. One of 'L0', 'L1', 'L2', 'Linf', 'all',
                or a list like ['L1', 'L2']. Default is 'L2'.
    plot      : bool
                Whether to show/save the plot. Default True.
    save_path : str or None
                Path to save the PNG. Pass None to skip saving.
    title     : str
                Plot title.

    Returns
    -------
    results : dict
        {
          loss_name: {
            'intercept':  float,
            'coefs':      np.ndarray,   -- one coefficient per feature
            'params':     np.ndarray,   -- [intercept, coef1, coef2, ...]
            'y_pred':     np.ndarray,
            'residuals':  np.ndarray,
            'l1_error':   float,
            'l2_error':   float,
            'linf_error': float,
          }
        }

    Examples
    --------
    Single feature:
        import numpy as np
        from regression import run_regression

        X = np.array([[1], [2], [3], [4]])
        y = np.array([2.1, 3.9, 6.2, 7.8])
        results = run_regression(X, y, loss='L2')

    Multiple features:
        X = np.column_stack([age, income])
        results = run_regression(X, y, x_cols=['age', 'income'], loss='all')

    Specific losses:
        results = run_regression(X, y, loss=['L1', 'Linf'])

    Access results:
        r = results['L2']
        print(r['intercept'], r['coefs'], r['l2_error'])
    """
    X = np.array(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    y = np.array(y, dtype=float)

    if x_cols is None:
        x_cols = [f'x{i}' for i in range(X.shape[1])]

    if loss == 'all':
        losses_to_run = list(LOSS_FUNCTIONS.keys())
    elif isinstance(loss, list):
        losses_to_run = loss
    else:
        losses_to_run = [loss]

    fits = {}
    results = {}

    for loss_name in losses_to_run:
        params = fit(X, y, loss_name)
        y_pred = predict(params, X)
        residuals = y - y_pred
        fits[loss_name] = params
        results[loss_name] = {
            'intercept':  float(params[0]),
            'coefs':      params[1:],
            'params':     params,
            'y_pred':     y_pred,
            'residuals':  residuals,
            'l1_error':   float(np.sum(np.abs(residuals))),
            'l2_error':   float(np.sum(residuals ** 2)),
            'linf_error': float(np.max(np.abs(residuals))),
        }

        print(f"\n{loss_name}:")
        print(f"  intercept = {params[0]:.4f}")
        for col, mi in zip(x_cols, params[1:]):
            print(f"  {col:15s} = {mi:.4f}")
        print(f"  L1 error  = {results[loss_name]['l1_error']:.4f}")
        print(f"  L2 error  = {results[loss_name]['l2_error']:.4f}")
        print(f"  Linf error= {results[loss_name]['linf_error']:.4f}")

    if plot:
        plot_results(X, y, fits, x_cols, title=title, save_path=save_path)

    return results


def run_regression_from_csv(filepath, x_cols, y_col, loss='L2', plot=True,
                             save_path='regression_results.png'):
    """
    Convenience wrapper: load a CSV and run regression.

    Parameters
    ----------
    filepath : str           -- path to CSV file
    x_cols   : list[str]     -- feature column name(s)
    y_col    : str           -- target column name
    loss     : str or list   -- see run_regression()
    plot     : bool
    save_path: str or None

    Returns
    -------
    results : dict -- see run_regression()

    Examples
    --------
    Single feature:
        from regression import run_regression_from_csv
        results = run_regression_from_csv('data.csv', x_cols=['age'], y_col='salary')

    Multiple features, compare all losses:
        results = run_regression_from_csv(
            'data.csv',
            x_cols=['age', 'income', 'education'],
            y_col='salary',
            loss='all'
        )

    No plot, specific losses:
        results = run_regression_from_csv(
            'data.csv',
            x_cols=['age', 'income'],
            y_col='salary',
            loss=['L1', 'L2'],
            plot=False
        )
    """
    X, y = load_data(filepath, x_cols, y_col)
    print(f"Loaded {len(y)} samples from '{filepath}'")
    print(f"Features ({len(x_cols)}): {x_cols}")
    return run_regression(X, y, x_cols=x_cols, loss=loss, plot=plot,
                          save_path=save_path,
                          title=f"Linear regression -- {filepath}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Linear regression with multiple loss functions')
    parser.add_argument('csv',         type=str,            help='Path to CSV file')
    parser.add_argument('--x',         type=str, nargs='+', required=True,
                        help='Name(s) of x column(s). E.g. --x age income education')
    parser.add_argument('--y',         type=str,            required=True,
                        help='Name of y column')
    parser.add_argument('--loss',      type=str,            default='L2',
                        choices=['L0', 'L1', 'L2', 'Linf', 'all'],
                        help='Loss function to use (default: L2). Use "all" to compare all.')
    parser.add_argument('--no-plot',   action='store_true', help='Skip plotting')
    parser.add_argument('--save-path', type=str,            default='regression_results.png',
                        help='Path to save plot PNG (default: regression_results.png)')
    args = parser.parse_args()

    run_regression_from_csv(
        filepath=args.csv,
        x_cols=args.x,
        y_col=args.y,
        loss=args.loss,
        plot=not args.no_plot,
        save_path=args.save_path,
    )


if __name__ == '__main__':
    main()
