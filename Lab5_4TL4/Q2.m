%% Lab 5 Q2 — Dolph-Chebyshev window FIR and Chebyshev Type II IIR
% Cutoff wc = pi/3. Window sidelobe attenuations are compared on M = 50.
% The IIR stopband spec Rs uses one of those same values (60 dB).
% High-order IIR transfer functions are kept in second-order sections
% so order 150 does not blow up in polynomial (b,a) form.

clear; close all; clc;
outdir = fullfile(fileparts(mfilename('fullpath')), 'figures');
if ~exist(outdir, 'dir'); mkdir(outdir); end

wc = pi/3;
fc = wc/pi;
nfft = 8192;
atten_list = [40 60 100];   % Dolph-Chebyshev sidelobe attenuation, dB
Rs = 60;                    % IIR stopband attenuation, matched to one window
orders = [20 50 150];
Mshow = 50;                 % order used for the attenuation comparison

%% (a) Window method, fir1 + chebwin
figure('Name', 'Q2a windows', 'Color', 'w', 'Position', [70 60 920 520]);
subplot(2,1,1); hold on;
for r = atten_list
    h = fir1(Mshow, fc, chebwin(Mshow+1, r));
    [H, w] = freqz(h, 1, nfft);
    plot(w/pi, 20*log10(abs(H)+eps), 'LineWidth', 1.15, ...
        'DisplayName', sprintf('%d dB sidelobes', r));
end
xline(fc, 'k--', 'HandleVisibility', 'off');
grid on; xlim([0 1]); ylim([-120 5]);
xlabel('\omega / \pi'); ylabel('Magnitude (dB)');
title(sprintf('fir1 + Dolph-Chebyshev window, M = %d', Mshow));
legend('Location', 'southwest');

subplot(2,1,2); hold on;
for r = atten_list
    h = fir1(Mshow, fc, chebwin(Mshow+1, r));
    [H, w] = freqz(h, 1, nfft);
    plot(w/pi, 20*log10(abs(H)+eps), 'LineWidth', 1.15, ...
        'DisplayName', sprintf('%d dB', r));
end
xline(fc, 'k--', 'HandleVisibility', 'off');
grid on; xlim([0.15 0.55]); ylim([-80 5]);
xlabel('\omega / \pi'); ylabel('Magnitude (dB)');
title('Zoom on the transition: more sidelobe attenuation \Rightarrow wider, gentler transition');
legend('Location', 'southwest');
saveas(gcf, fullfile(outdir, 'q2a_window_attenuation.png'));

% also store the three windowed FIRs used later
h_win = cell(1, numel(orders));
for k = 1:numel(orders)
    h_win{k} = fir1(orders(k), fc, chebwin(orders(k)+1, Rs));
end

%% (b)(c) Chebyshev Type II IIR, impulse responses
figure('Name', 'Q2c impulse', 'Color', 'w', 'Position', [80 40 920 720]);
Limp = 800;
for k = 1:numel(orders)
    N = orders(k);
    sos = cheby2_sos(N, Rs, fc);
    h = impz_sos(sos, Limp);

    subplot(3,1,k);
    stem(0:Limp-1, h, 'Marker', 'none');
    grid on; xlim([0 Limp-1]);
    title(sprintf('Chebyshev II impulse response, N = %d, R_s = %d dB (still nonzero at the right edge)', N, Rs));
    xlabel('n'); ylabel('h[n]');
    fprintf('IIR N = %3d | |h[%d]| = %.3e | FIR of same order is exactly 0 for n > %d\n', ...
        N, Limp-1, abs(h(end)), N);
end
saveas(gcf, fullfile(outdir, 'q2c_iir_impulse.png'));

figure('Name', 'Q2c log impulse', 'Color', 'w', 'Position', [100 80 860 380]);
hold on;
for k = 1:numel(orders)
    N = orders(k);
    sos = cheby2_sos(N, Rs, fc);
    h = impz_sos(sos, 2000);
    semilogy(0:numel(h)-1, abs(h)+1e-18, 'LineWidth', 1.1, ...
        'DisplayName', sprintf('N = %d', N));
end
grid on; xlim([0 2000]);
xlabel('n'); ylabel('|h[n]|');
title('IIR tails decay exponentially and never become identically zero');
legend('Location', 'northeast');
saveas(gcf, fullfile(outdir, 'q2c_iir_impulse_log.png'));

%% (d) FIR window vs IIR Chebyshev II, magnitude and phase
figure('Name', 'Q2d magnitude', 'Color', 'w', 'Position', [60 40 920 720]);
for k = 1:numel(orders)
    N = orders(k);
    sos = cheby2_sos(N, Rs, fc);
    [Hi, w] = freqz_sos(sos, nfft);
    [Hf, ~] = freqz(h_win{k}, 1, nfft);

    subplot(3,1,k);
    plot(w/pi, 20*log10(abs(Hf)+eps), 'LineWidth', 1.05); hold on;
    plot(w/pi, 20*log10(abs(Hi)+eps), 'LineWidth', 1.05);
    yline(-Rs, 'k:'); xline(fc, 'k--');
    grid on; xlim([0 1]); ylim([-100 5]);
    title(sprintf('Magnitude, order = %d, attenuation spec = %d dB', N, Rs));
    xlabel('\omega / \pi'); ylabel('dB');
    legend('FIR Dolph-Chebyshev window', 'IIR Chebyshev II', ...
        sprintf('-%d dB', Rs), '\omega_c', 'Location', 'southwest');
end
saveas(gcf, fullfile(outdir, 'q2d_magnitude_compare.png'));

figure('Name', 'Q2d phase', 'Color', 'w', 'Position', [80 40 920 720]);
for k = 1:numel(orders)
    N = orders(k);
    sos = cheby2_sos(N, Rs, fc);
    [Hi, w] = freqz_sos(sos, nfft);
    [Hf, ~] = freqz(h_win{k}, 1, nfft);

    subplot(3,1,k);
    plot(w/pi, unwrap(angle(Hf)), 'LineWidth', 1.05); hold on;
    plot(w/pi, unwrap(angle(Hi)), 'LineWidth', 1.05);
    grid on; xlim([0 1]);
    title(sprintf('Unwrapped phase, order = %d', N));
    xlabel('\omega / \pi'); ylabel('rad');
    legend('FIR (linear)', 'IIR (not linear)', 'Location', 'southwest');
end
saveas(gcf, fullfile(outdir, 'q2d_phase_compare.png'));

%% (e) filter() vs convolution with a long truncated impulse response
rng(1);
x = randn(1, 1000);
N = 20;   % moderate order keeps the (b,a) and sos results easy to compare
sos = cheby2_sos(N, Rs, fc);
y_filt = sosfilt_local(sos, x);

figure('Name', 'Q2e estimate', 'Color', 'w', 'Position', [70 50 900 640]);
lengths = [50 200 2000];
for i = 1:numel(lengths)
    L = lengths(i);
    h = impz_sos(sos, L);
    y_hat = conv(x, h);
    y_hat = y_hat(1:numel(x));
    err = y_hat - y_filt;
    rel = norm(err) / norm(y_filt);
    fprintf('Truncated h length %4d | rel. error ||e||/||y|| = %.3e | max |e| = %.3e\n', ...
        L, rel, max(abs(err)));

    subplot(3,1,i);
    plot(y_filt, 'b'); hold on;
    plot(err, 'r');
    grid on; xlim([1 1000]);
    title(sprintf('N = %d, h truncated to %d samples, relative error %.2e', N, L, rel));
    xlabel('n'); ylabel('amplitude');
    legend('filter output', 'conv estimate error', 'Location', 'northeast');
end
saveas(gcf, fullfile(outdir, 'q2e_conv_estimate.png'));

fprintf(['\nQ2(e): once the kept impulse response covers the significant tail,\n' ...
    'conv(x, h_truncated) matches filter to numerical accuracy.\n']);

function sos = cheby2_sos(N, Rs, fc)
    [z, p, kk] = cheby2(N, Rs, fc);
    [sos, g] = zp2sos(z, p, kk);
    sos(1, 1:3) = g * sos(1, 1:3);
end

%% ----- local helpers (no toolbox dependency beyond zp2sos / freqz) -----
function h = impz_sos(sos, L)
    x = zeros(L, 1);
    x(1) = 1;
    h = sosfilt_local(sos, x);
    h = h(:).';
end

function [H, w] = freqz_sos(sos, nfft)
    % Cascade each second-order section. Gain is already inside sos from zp2sos.
    w = linspace(0, pi, nfft).';
    ejw = exp(-1j * w);
    H = ones(nfft, 1);
    for s = 1:size(sos, 1)
        b = sos(s, 1:3);
        a = sos(s, 4:6);
        num = b(1) + b(2)*ejw + b(3)*ejw.^2;
        den = a(1) + a(2)*ejw + a(3)*ejw.^2;
        H = H .* (num ./ den);
    end
end

function y = sosfilt_local(sos, x)
    % Direct-form II transposed, one section at a time. Column in, column out.
    x = x(:);
    y = x;
    for s = 1:size(sos, 1)
        b = sos(s, 1:3);
        a = sos(s, 4:6);
        y = filter(b, a, y);
    end
end
