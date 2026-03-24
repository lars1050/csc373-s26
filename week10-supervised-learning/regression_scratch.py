import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse


# ── Utility ────────────────────────────────────────────────────────────────────

def load_data(filepath, x_col, y_col):
    df = pd.read_csv(filepath)
    x = df[x_col].values.astype(float)
    y = df[y_col].values.astype(float)
    return x, y


def predict(m, b, x):
    return m * x + b


# ── L2 — Ordinary Least Squares (closed form) ─────────────────────────────────
#
# Minimizes: sum of (y_i - (m*x_i + b))^2
#
# Setting the partial derivatives to zero gives a system of two equations
# (the "normal equations") which we solve directly:
#
#   m = ( n*sum(x*y) - sum(x)*sum(y) ) / ( n*sum(x^2) - sum(x)^2 )
#   b = ( sum(y) - m*sum(x) ) / n
#
# This is an exact solution — no iteration needed.

def fit_l2(x, y):
    n      = len(x)
    sum_x  = np.sum(x)
    sum_y  = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_xx = np.sum(x * x)

    m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x ** 2)
    b = (sum_y - m * sum_x) / n

    return m, b


# ── L1 — Least Absolute Deviations (iteratively reweighted least squares) ─────
#
# Minimizes: sum of |y_i - (m*x_i + b)|
#
# No closed form exists. We use IRLS: at each iteration, each point is given
# a weight inversely proportional to its current residual. Points with large
# residuals (outliers) are down-weighted. We then solve a weighted L2 problem.
# This converges to the L1 solution.
#
# Weighted normal equations:
#   m = sum(w * x * y) / sum(w * x^2)  (after centering by weighted means)

def fit_l1(x, y, iterations=50, epsilon=1e-6):
    # Start with L2 solution
    m, b = fit_l2(x, y)

    for i in range(iterations):
        residuals = np.abs(y - predict(m, b, x))

        # Weights are inverse of absolute residuals (epsilon avoids division by zero)
        weights = 1.0 / np.maximum(residuals, epsilon)

        # Solve weighted least squares using weighted normal equations
        w_sum    = np.sum(weights)
        x_mean_w = np.sum(weights * x) / w_sum
        y_mean_w = np.sum(weights * y) / w_sum

        numerator   = np.sum(weights * (x - x_mean_w) * (y - y_mean_w))
        denominator = np.sum(weights * (x - x_mean_w) ** 2)

        m_new = numerator / denominator
        b_new = y_mean_w - m_new * x_mean_w

        # Check convergence
        if abs(m_new - m) < 1e-10 and abs(b_new - b) < 1e-10:
            print(f"  L1 converged at iteration {i+1}")
            break

        m, b = m_new, b_new

    return m, b


# ── L0 — Minimize number of non-zero residuals (brute force over point pairs) ──
#
# Minimizes: count of points NOT exactly on the line
# Equivalently: maximizes points exactly on (or very near) the line.
#
# For continuous data an exact fit through every point is impossible,
# so we find the line passing through each pair of points and pick the one
# that brings the most other points within a tolerance band.
#
# This is O(n^2) in the number of candidate lines.

def fit_l0(x, y, tolerance=0.5):
    n = len(x)
    best_m, best_b = fit_l2(x, y)
    best_count = 0

    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            if abs(dx) < 1e-10:
                continue  # vertical line, skip

            m_candidate = (y[j] - y[i]) / dx
            b_candidate = y[i] - m_candidate * x[i]

            residuals = np.abs(y - predict(m_candidate, b_candidate, x))
            count = np.sum(residuals < tolerance)

            if count > best_count:
                best_count = count
                best_m, best_b = m_candidate, b_candidate

    print(f"  L0 best line passes within tolerance of {best_count}/{n} points")
    return best_m, best_b


# ── Linf — Minimax / Chebyshev fit (iterative reweighting) ────────────────────
#
# Minimizes: max( |y_i - (m*x_i + b)| )  — the single worst residual
#
# We use a reweighting scheme: points with the largest residuals get the
# highest weights, forcing the optimizer to focus on reducing the worst case.
# This converges to the Chebyshev (L-infinity) solution.
#
# An exact algorithm (Chebyshev equioscillation) is more complex;
# this iterative approach is instructive and converges well in practice.

def fit_linf(x, y, iterations=200):
    m, b = fit_l2(x, y)

    for i in range(iterations):
        residuals = np.abs(y - predict(m, b, x))
        max_res   = np.max(residuals)

        # Weight points proportional to their residual relative to the max
        weights = (residuals / (max_res + 1e-10)) ** 4

        w_sum    = np.sum(weights)
        x_mean_w = np.sum(weights * x) / w_sum
        y_mean_w = np.sum(weights * y) / w_sum

        numerator   = np.sum(weights * (x - x_mean_w) * (y - y_mean_w))
        denominator = np.sum(weights * (x - x_mean_w) ** 2)

        m_new = numerator / denominator
        b_new = y_mean_w - m_new * x_mean_w

        if abs(m_new - m) < 1e-12 and abs(b_new - b) < 1e-12:
            print(f"  Linf converged at iteration {i+1}")
            break

        m, b = m_new, b_new

    return m, b


# ── Fit dispatcher ─────────────────────────────────────────────────────────────

def fit(x, y, loss_name):
    print(f"\nFitting with {loss_name}:")
    if loss_name == 'L0':
        return fit_l0(x, y)
    elif loss_name == 'L1':
        return fit_l1(x, y)
    elif loss_name == 'L2':
        return fit_l2(x, y)
    elif loss_name == 'Linf':
        return fit_linf(x, y)


# ── Plot ───────────────────────────────────────────────────────────────────────

def plot_results(x, y, fits):
    colors = {'L0': '#E24B4A', 'L1': '#EF9F27', 'L2': '#378ADD', 'Linf': '#1D9E75'}
    fig, axes = plt.subplots(1, len(fits), figsize=(5 * len(fits), 4), sharey=True)
    if len(fits) == 1:
        axes = [axes]

    x_line = np.linspace(x.min(), x.max(), 200)

    for ax, (loss_name, (m, b)) in zip(axes, fits.items()):
        y_pred    = predict(m, b, x)
        residuals = y - y_pred
        color     = colors.get(loss_name, '#378ADD')

        ax.scatter(x, y, color='#888780', zorder=3, s=50, label='Data')
        ax.plot(x_line, predict(m, b, x_line), color=color, linewidth=2,
                label=f'y = {m:.3f}x + {b:.3f}')

        for xi, yi, ri in zip(x, y, residuals):
            ax.plot([xi, xi], [yi, yi - ri], color=color, alpha=0.35, linewidth=1)

        ax.set_title(f'{loss_name}  |  m={m:.3f}, b={b:.3f}', fontsize=11)
        ax.set_xlabel('x')
        if ax == axes[0]:
            ax.set_ylabel('y')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.2)

    plt.suptitle('Linear regression — from-scratch algorithms', fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig('regression_scratch_results.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved to regression_scratch_results.png")
    plt.show()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='From-scratch linear regression')
    parser.add_argument('csv',    type=str, help='Path to CSV file')
    parser.add_argument('--x',   type=str, required=True, help='Name of x column')
    parser.add_argument('--y',   type=str, required=True, help='Name of y column')
    parser.add_argument('--loss', type=str, default='L2',
                        choices=['L0', 'L1', 'L2', 'Linf', 'all'],
                        help='Loss function (default: L2). Use "all" to compare.')
    args = parser.parse_args()

    x, y = load_data(args.csv, args.x, args.y)
    print(f"Loaded {len(x)} samples from '{args.csv}'")

    losses_to_run = ['L0', 'L1', 'L2', 'Linf'] if args.loss == 'all' else [args.loss]

    fits = {}
    for loss_name in losses_to_run:
        m, b = fit(x, y, loss_name)
        fits[loss_name] = (m, b)
        residuals = y - predict(m, b, x)
        print(f"  slope     = {m:.4f}")
        print(f"  intercept = {b:.4f}")
        print(f"  L1 error  = {np.sum(np.abs(residuals)):.4f}")
        print(f"  L2 error  = {np.sum(residuals**2):.4f}")
        print(f"  Linf error= {np.max(np.abs(residuals)):.4f}")

    plot_results(x, y, fits)


if __name__ == '__main__':
    main()
