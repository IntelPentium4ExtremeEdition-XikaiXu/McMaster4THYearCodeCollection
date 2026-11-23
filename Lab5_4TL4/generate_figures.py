#!/usr/bin/env python3
"""Same designs as Q1.m / Q2.m / Q3.m, for machines without MATLAB."""

import os
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

WC = np.pi / 3
FC = 1.0 / 3.0
ORDERS = [20, 50, 150]
NFFT = 4096


def trunc(M, wc=WC):
    n = np.arange(M + 1, dtype=float)
    d = n - M / 2.0
    h = np.empty_like(d)
    h[d == 0] = wc / np.pi
    nz = d != 0
    h[nz] = np.sin(wc * d[nz]) / (np.pi * d[nz])
    return h


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=130, bbox_inches="tight")
    plt.close(fig)


def q1():
    hs, hls = [], []
    for M in ORDERS:
        h = trunc(M)
        b = signal.firls(M + 1, [0, FC, FC, 1], [1, 1, 0, 0])
        hs.append(h)
        hls.append(b)
        print(f"M={M:3d} |trunc-firls|={np.max(np.abs(h-b)):.3e} "
              f"sym={np.max(np.abs(h-h[::-1])):.3e}")

    fig, axes = plt.subplots(3, 1, figsize=(9, 8))
    for ax, M, h in zip(axes, ORDERS, hs):
        w, H = signal.freqz(h, worN=NFFT)
        ax.plot(w / np.pi, np.abs(H), label="|H|")
        ax.axvline(FC, color="k", ls="--", lw=0.8, label=r"$\omega_c=\pi/3$")
        ax.hlines(1, 0, FC, colors="r", linestyles=":", label="ideal passband")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.25)
        ax.grid(True)
        ax.set_title(f"Truncation LPF, M = {M}  (Gibbs ripple does not shrink)")
        ax.set_xlabel(r"$\omega / \pi$")
        ax.set_ylabel(r"$|H(e^{j\omega})|$")
        ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    save(fig, "q1_gibbs_magnitude.png")

    fig, ax = plt.subplots(figsize=(9, 4.2))
    for M, h in zip(ORDERS, hs):
        w, H = signal.freqz(h, worN=NFFT)
        ax.plot(w / np.pi, 20 * np.log10(np.abs(H) + 1e-16), label=f"M = {M}")
    ax.axvline(FC, color="k", ls="--", lw=0.8)
    ax.set_xlim(0, 1)
    ax.set_ylim(-80, 5)
    ax.grid(True)
    ax.set_xlabel(r"$\omega / \pi$")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_title("Sidelobe height stays near −21 dB; only the width shrinks")
    ax.legend()
    fig.tight_layout()
    save(fig, "q1_gibbs_db.png")

    fig, axes = plt.subplots(3, 1, figsize=(9, 8))
    for ax, M, h in zip(axes, ORDERS, hs):
        w, H = signal.freqz(h, worN=NFFT)
        ph = np.unwrap(np.angle(H))
        ideal = -(M / 2) * w
        ax.plot(w / np.pi, ph, label="unwrapped phase")
        ax.plot(w / np.pi, ideal, "r--", label=fr"$-(M/2)\omega$")
        ax.grid(True)
        ax.set_xlim(0, 1)
        ax.set_title(f"Unwrapped phase, M = {M}")
        ax.set_xlabel(r"$\omega / \pi$")
        ax.set_ylabel("arg H (rad)")
        ax.legend(fontsize=8, loc="lower left")
        mask = np.abs(H) > 0.2
        print(f"M={M:3d} phase err={np.max(np.abs(ph[mask]-ideal[mask])):.3e}")
    fig.tight_layout()
    save(fig, "q1_phase.png")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    for M, h in zip(ORDERS, hs):
        w, gd = signal.group_delay((h, 1), w=NFFT)
        ax.plot(w / np.pi, gd, label=f"M = {M}")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 160)
    ax.grid(True)
    ax.set_xlabel(r"$\omega / \pi$")
    ax.set_ylabel("Group delay (samples)")
    ax.set_title("Constant group delay = M/2")
    ax.legend()
    fig.tight_layout()
    save(fig, "q1_group_delay.png")

    fig, axes = plt.subplots(3, 1, figsize=(9, 8))
    for ax, M, h, b in zip(axes, ORDERS, hs, hls):
        n = np.arange(M + 1)
        ax.stem(n, h, linefmt="C0-", markerfmt="C0o", basefmt="k-", label="truncation")
        ax.stem(n, b, linefmt="C3-", markerfmt="C3.", basefmt=" ", label="firls")
        ax.grid(True)
        ax.set_title(f"M = {M}, max |trunc − firls| = {np.max(np.abs(h-b)):.2e}")
        ax.set_xlabel("n")
        ax.set_ylabel("h[n]")
        ax.legend()
    fig.tight_layout()
    save(fig, "q1_firls_compare.png")

    rng = np.random.default_rng(1)
    x = rng.standard_normal(1000)
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 8))
    for ax, M, h in zip(axes, ORDERS, hs):
        y_conv = np.convolve(x, h)
        y_filt = signal.lfilter(h, [1.0], x)
        d = y_conv[:1000] - y_filt
        print(f"M={M:3d} conv-filter max {np.max(np.abs(d)):.3e} "
              f"len conv {len(y_conv)} filter {len(y_filt)}")
        ax.plot(y_filt, label="filter")
        ax.plot(d, label="conv(1:N) − filter")
        ax.set_xlim(0, 999)
        ax.grid(True)
        ax.set_title(f"M = {M}: filter output and conv−filter error")
        ax.set_xlabel("n")
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "q1_conv_vs_filter.png")


def q2():
    attens = [40, 60, 100]
    Rs = 60
    Mshow = 50

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.2))
    for att in attens:
        h = signal.firwin(Mshow + 1, FC, window=("chebwin", att))
        w, H = signal.freqz(h, worN=8192)
        db = 20 * np.log10(np.abs(H) + 1e-16)
        axes[0].plot(w / np.pi, db, label=f"{att} dB sidelobes")
        axes[1].plot(w / np.pi, db, label=f"{att} dB")
    for ax in axes:
        ax.axvline(FC, color="k", ls="--", lw=0.8)
        ax.grid(True)
        ax.set_xlabel(r"$\omega / \pi$")
        ax.set_ylabel("Magnitude (dB)")
        ax.legend(fontsize=8)
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(-120, 5)
    axes[0].set_title(f"fir1 + Dolph-Chebyshev window, M = {Mshow}")
    axes[1].set_xlim(0.15, 0.55)
    axes[1].set_ylim(-80, 5)
    axes[1].set_title("Zoom: more attenuation ⇒ wider, gentler transition")
    fig.tight_layout()
    save(fig, "q2a_window_attenuation.png")

    h_win = [signal.firwin(M + 1, FC, window=("chebwin", Rs)) for M in ORDERS]

    fig, axes = plt.subplots(3, 1, figsize=(9, 8))
    Limp = 800
    for ax, N in zip(axes, ORDERS):
        sos = signal.cheby2(N, Rs, FC, output="sos")
        h = signal.sosfilt(sos, np.r_[1.0, np.zeros(Limp - 1)])
        ax.plot(np.arange(Limp), h, lw=0.8)
        ax.grid(True)
        ax.set_xlim(0, Limp - 1)
        ax.set_title(f"Chebyshev II impulse response, N = {N}, Rs = {Rs} dB")
        ax.set_xlabel("n")
        ax.set_ylabel("h[n]")
        print(f"IIR N={N:3d} |h[{Limp-1}]|={abs(h[-1]):.3e}")
    fig.tight_layout()
    save(fig, "q2c_iir_impulse.png")

    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    for N in ORDERS:
        sos = signal.cheby2(N, Rs, FC, output="sos")
        h = signal.sosfilt(sos, np.r_[1.0, np.zeros(1999)])
        ax.semilogy(np.arange(len(h)), np.abs(h) + 1e-18, label=f"N = {N}")
    ax.set_xlim(0, 2000)
    ax.grid(True, which="both")
    ax.set_xlabel("n")
    ax.set_ylabel("|h[n]|")
    ax.set_title("IIR tails decay exponentially and never become identically zero")
    ax.legend()
    fig.tight_layout()
    save(fig, "q2c_iir_impulse_log.png")

    fig, axes = plt.subplots(3, 1, figsize=(9, 8))
    figp, axesp = plt.subplots(3, 1, figsize=(9, 8))
    for ax, axp, N, hf in zip(axes, axesp, ORDERS, h_win):
        sos = signal.cheby2(N, Rs, FC, output="sos")
        w, Hi = signal.sosfreqz(sos, worN=8192)
        _, Hf = signal.freqz(hf, worN=8192)
        ax.plot(w / np.pi, 20 * np.log10(np.abs(Hf) + 1e-16), label="FIR Dolph-Chebyshev")
        ax.plot(w / np.pi, 20 * np.log10(np.abs(Hi) + 1e-16), label="IIR Chebyshev II")
        ax.axhline(-Rs, color="k", ls=":", lw=0.8)
        ax.axvline(FC, color="k", ls="--", lw=0.8)
        ax.set_xlim(0, 1)
        ax.set_ylim(-100, 5)
        ax.grid(True)
        ax.set_title(f"Magnitude, order = {N}, attenuation spec = {Rs} dB")
        ax.set_xlabel(r"$\omega / \pi$")
        ax.set_ylabel("dB")
        ax.legend(fontsize=8, loc="lower left")

        axp.plot(w / np.pi, np.unwrap(np.angle(Hf)), label="FIR (linear)")
        axp.plot(w / np.pi, np.unwrap(np.angle(Hi)), label="IIR (not linear)")
        axp.grid(True)
        axp.set_xlim(0, 1)
        axp.set_title(f"Unwrapped phase, order = {N}")
        axp.set_xlabel(r"$\omega / \pi$")
        axp.set_ylabel("rad")
        axp.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "q2d_magnitude_compare.png")
    figp.tight_layout()
    save(figp, "q2d_phase_compare.png")

    rng = np.random.default_rng(1)
    x = rng.standard_normal(1000)
    N = 20
    sos = signal.cheby2(N, Rs, FC, output="sos")
    y = signal.sosfilt(sos, x)
    fig, axes = plt.subplots(3, 1, figsize=(9, 7))
    for ax, L in zip(axes, [50, 200, 2000]):
        h = signal.sosfilt(sos, np.r_[1.0, np.zeros(L - 1)])
        yhat = np.convolve(x, h)[:1000]
        err = yhat - y
        rel = np.linalg.norm(err) / np.linalg.norm(y)
        print(f"L={L:4d} rel={rel:.3e} max={np.max(np.abs(err)):.3e}")
        ax.plot(y, label="filter output")
        ax.plot(err, label="conv estimate error")
        ax.set_xlim(0, 999)
        ax.grid(True)
        ax.set_title(f"N = {N}, h truncated to {L} samples, relative error {rel:.2e}")
        ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "q2e_conv_estimate.png")


def q3():
    w, H2 = signal.freqz([1, -1], worN=NFFT)
    _, H3 = signal.freqz([1, -2, 1], worN=NFFT)
    print(f"H2(0)={abs(H2[0]):.3e} H3(0)={abs(H3[0]):.3e}")
    print(f"|H2(pi)|={abs(H2[-1]):.4f} |H3(pi)|={abs(H3[-1]):.4f}")

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.plot(w / np.pi, np.abs(H2), label=r"two-pulse  $2|\sin(\omega/2)|$")
    ax.plot(w / np.pi, np.abs(H3), label=r"three-pulse  $4\sin^2(\omega/2)$")
    ax.set_xlim(0, 1)
    ax.grid(True)
    ax.set_xlabel(r"$\omega / \pi$  (normalized Doppler)")
    ax.set_ylabel(r"$|H(e^{j\omega})|$")
    ax.set_title("Both null DC; the three-pulse notch is wider")
    ax.legend()
    fig.tight_layout()
    save(fig, "q3_mti_magnitude.png")

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.plot(w / np.pi, 20 * np.log10(np.abs(H2) + 1e-16), label="two-pulse")
    ax.plot(w / np.pi, 20 * np.log10(np.abs(H3) + 1e-16), label="three-pulse")
    ax.set_xlim(0, 1)
    ax.set_ylim(-80, 15)
    ax.grid(True)
    ax.set_xlabel(r"$\omega / \pi$  (normalized Doppler)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_title("Three-pulse stays down longer near 0 Hz")
    ax.legend(loc="lower right")
    fig.tight_layout()
    save(fig, "q3_mti_db.png")

    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    ax.plot(w / np.pi, np.unwrap(np.angle(H2)), label="two-pulse (delay 0.5)")
    ax.plot(w / np.pi, np.unwrap(np.angle(H3)), label="three-pulse (delay 1)")
    ax.set_xlim(0, 1)
    ax.grid(True)
    ax.set_xlabel(r"$\omega / \pi$")
    ax.set_ylabel("Unwrapped phase (rad)")
    ax.set_title("Both cancellers are linear-phase FIR highpass filters")
    ax.legend()
    fig.tight_layout()
    save(fig, "q3_mti_phase.png")


if __name__ == "__main__":
    q1()
    q2()
    q3()
    print("wrote", OUT)
