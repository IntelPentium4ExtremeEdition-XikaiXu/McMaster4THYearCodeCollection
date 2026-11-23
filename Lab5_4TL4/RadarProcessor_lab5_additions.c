/*
 * COMPENG 4TL4 Lab 5 — pieces to drop into the official
 * "RadarProcessor_lab5.c" from Y:/COE4TL4/RadarProcessor/src.
 *
 * The starter already defines USE_MTI and a two-pulse set_mti_h().
 * Variable names in the starter (mti_h, mti_len, USE_THREE_PULSE, ...)
 * may differ slightly; keep the starter's names and use the coefficients
 * and the window formula below.
 *
 * Two-pulse:   y[n] = x[n] -     x[n-1]            h = { 1, -1 }
 * Three-pulse: y[n] = x[n] - 2 x[n-1] + x[n-2]    h = { 1, -2, 1 }
 *
 * If the platform moves, stationary clutter is no longer at 0 Hz Doppler.
 * Shift the null onto the clutter Doppler w0 = 2*pi*f_clutter/PRF:
 *     y[n] = x[n] - exp(j*w0) * x[n-1]
 * or, equivalently, derotate each sweep by the platform phase before the
 * ordinary canceller so the barrier sits back at DC.
 */

#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Set this to 2 for the two-pulse canceller and 3 for the three-pulse one. */
int MTI_PULSES = 2;

double mti_h[3];
int mti_h_len = 0;

void set_mti_h(void)
{
    if (MTI_PULSES == 3) {
        mti_h_len = 3;
        mti_h[0] =  1.0;
        mti_h[1] = -2.0;
        mti_h[2] =  1.0;
    } else {
        /* default: two-pulse canceller already in the starter */
        mti_h_len = 2;
        mti_h[0] =  1.0;
        mti_h[1] = -1.0;
        mti_h[2] =  0.0;
    }
}

/* Lab equation: wh = 0.5 * (1 - cos(2*pi*n/N)), n = 0..N-1. */
double hanning_window(int n, int N)
{
    if (N <= 1) {
        return 1.0;
    }
    return 0.5 * (1.0 - cos(2.0 * M_PI * (double)n / (double)N));
}

/*
 * Multiply the chirp by the window inside the existing prepare_fft_data().
 * Replace the copy loop with this pattern (keep the starter's buffer type).
 *
 *     for (i = 0; i < ncopy; i++) {
 *         double w = hanning_window(i, ncopy);
 *         data[i].real = dechirp_real[i] * w;
 *         data[i].imag = dechirp_img[i]  * w;
 *     }
 *
 * Same idea for the library buffer:
 *         data[2*i]     = dechirp_real[i] * w;
 *         data[2*i + 1] = dechirp_img[i]  * w;
 *
 * The window is applied on fast time, before the range FFT. It lowers
 * range sidelobes (less leakage from the bright barrier into nearby bins)
 * and widens each range peak slightly.
 */
