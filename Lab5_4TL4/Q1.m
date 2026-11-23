%% Lab 5 Q1 — Truncation method for linear-phase lowpass FIR
% Cutoff wc = pi/3, orders M = 20, 50, 150 (lengths 21, 51, 151).
% Run this script in MATLAB (Signal Processing Toolbox). It prints the
% checks the TA will ask about and saves figures under figures/.

clear; close all; clc;
outdir = fullfile(fileparts(mfilename('fullpath')), 'figures');
if ~exist(outdir, 'dir'); mkdir(outdir); end

wc = pi/3;
fc = wc/pi;                 % firls / fir1 use Nyquist = 1
orders = [20 50 150];
nfft = 4096;

h_trunc = cell(1, numel(orders));
h_ls    = cell(1, numel(orders));

for k = 1:numel(orders)
    M = orders(k);
    n = 0:M;
    delay = M/2;
    h = sin(wc * (n - delay)) ./ (pi * (n - delay));
    h(n == delay) = wc/pi;          % removable singularity at the centre tap
    h_trunc{k} = h;

    % Zero-width transition: least squares on the Fourier basis IS truncation.
    % Some MATLAB releases reject a repeated frequency; a 1e-6 gap is
    % numerically the same comparison for the demo.
    try
        h_ls{k} = firls(M, [0 fc fc 1], [1 1 0 0]);
    catch
        gap = 1e-6;
        h_ls{k} = firls(M, [0 fc-gap fc+gap 1], [1 1 0 0]);
    end

    err = max(abs(h_trunc{k} - h_ls{k}));
    sym_err = max(abs(h - fliplr(h)));
    fprintf('M = %3d | max |h_trunc - h_firls| = %.3e | symmetry error = %.3e\n', ...
        M, err, sym_err);
end

%% (b) Gibbs phenomenon — ripple height stays, transition gets narrower
figure('Name', 'Q1 Gibbs', 'Color', 'w', 'Position', [80 80 900 700]);
for k = 1:numel(orders)
    [H, w] = freqz(h_trunc{k}, 1, nfft);
    subplot(3,1,k);
    plot(w/pi, abs(H), 'b', 'LineWidth', 1.1); hold on;
    plot([fc fc], [0 1.25], 'k--', 'LineWidth', 0.8);
    plot([0 fc], [1 1], 'r:', 'LineWidth', 0.8);
    ylim([0 1.25]); xlim([0 1]); grid on;
    title(sprintf('Truncation LPF, M = %d  (Gibbs ripple does not shrink)', orders(k)));
    xlabel('\omega / \pi'); ylabel('|H(e^{j\omega})|');
    legend('|H|', '\omega_c = \pi/3', 'ideal passband', 'Location', 'northeast');
end
saveas(gcf, fullfile(outdir, 'q1_gibbs_magnitude.png'));

figure('Name', 'Q1 Gibbs dB', 'Color', 'w', 'Position', [100 80 900 420]);
hold on;
for k = 1:numel(orders)
    [H, w] = freqz(h_trunc{k}, 1, nfft);
    plot(w/pi, 20*log10(abs(H)+eps), 'LineWidth', 1.1, ...
        'DisplayName', sprintf('M = %d', orders(k)));
end
xline(fc, 'k--', '\omega_c', 'LabelVerticalAlignment', 'bottom');
ylim([-80 5]); xlim([0 1]); grid on;
xlabel('\omega / \pi'); ylabel('Magnitude (dB)');
title('Same filters in dB: sidelobe height stays near -21 dB, width shrinks');
legend('Location', 'southwest');
saveas(gcf, fullfile(outdir, 'q1_gibbs_db.png'));

%% (c) Linear phase — unwrapped phase tracks -(M/2) \omega, group delay is M/2
figure('Name', 'Q1 phase', 'Color', 'w', 'Position', [120 60 900 700]);
for k = 1:numel(orders)
    M = orders(k);
    [H, w] = freqz(h_trunc{k}, 1, nfft);
    ph = unwrap(angle(H));
    ideal = -(M/2) * w;
    subplot(3,1,k);
    plot(w/pi, ph, 'b', 'LineWidth', 1.1); hold on;
    plot(w/pi, ideal, 'r--', 'LineWidth', 1.0);
    grid on; xlim([0 1]);
    title(sprintf('Unwrapped phase, M = %d', M));
    xlabel('\omega / \pi'); ylabel('arg H (rad)');
    legend('unwrapped phase', sprintf('-(M/2)\\omega = -%g \\omega', M/2), ...
        'Location', 'southwest');
    % phase error only where the magnitude is not in a stopband zero
    mask = abs(H) > 0.2;
    fprintf('M = %3d | max phase error in |H|>0.2 : %.3e rad | group delay = M/2 = %.1f\n', ...
        M, max(abs(ph(mask) - ideal(mask))), M/2);
end
saveas(gcf, fullfile(outdir, 'q1_phase.png'));

figure('Name', 'Q1 group delay', 'Color', 'w', 'Position', [140 80 800 360]);
hold on;
for k = 1:numel(orders)
    [gd, wgd] = grpdelay(h_trunc{k}, 1, nfft);
    plot(wgd/pi, gd, 'LineWidth', 1.1, 'DisplayName', sprintf('M = %d', orders(k)));
end
grid on; xlim([0 1]); ylim([0 160]);
xlabel('\omega / \pi'); ylabel('Group delay (samples)');
title('Constant group delay = M/2 confirms exact linear phase');
legend('Location', 'northwest');
saveas(gcf, fullfile(outdir, 'q1_group_delay.png'));

%% (d) firls matches truncation
figure('Name', 'Q1 firls', 'Color', 'w', 'Position', [80 40 900 700]);
for k = 1:numel(orders)
    subplot(3,1,k);
    stem(0:orders(k), h_trunc{k}, 'b', 'Marker', 'o'); hold on;
    stem(0:orders(k), h_ls{k}, 'r', 'Marker', '.');
    grid on;
    title(sprintf('Impulse response M = %d, max |trunc - firls| = %.2e', ...
        orders(k), max(abs(h_trunc{k} - h_ls{k}))));
    xlabel('n'); ylabel('h[n]');
    legend('truncation', 'firls', 'Location', 'northeast');
end
saveas(gcf, fullfile(outdir, 'q1_firls_compare.png'));

%% (e) conv vs filter on 1000-sample white Gaussian noise
rng(1);
x = randn(1, 1000);
figure('Name', 'Q1 conv vs filter', 'Color', 'w', 'Position', [60 40 950 750]);
for k = 1:numel(orders)
    h = h_trunc{k};
    y_conv = conv(x, h);             % length 1000+M
    y_filt = filter(h, 1, x);        % length 1000
    d = y_conv(1:numel(x)) - y_filt;
    fprintf('M = %3d | max |conv(1:N) - filter| = %.3e | conv length %d, filter length %d\n', ...
        orders(k), max(abs(d)), numel(y_conv), numel(y_filt));

    subplot(3,1,k);
    plot(y_filt, 'b'); hold on;
    plot(d, 'r');
    grid on; xlim([1 1000]);
    title(sprintf('M = %d: filter output (blue) and conv-filter error (red, ~0)', orders(k)));
    xlabel('n'); ylabel('amplitude');
    legend('filter(h,1,x)', 'conv(1:N) - filter', 'Location', 'northeast');
end
saveas(gcf, fullfile(outdir, 'q1_conv_vs_filter.png'));

fprintf(['\nQ1(e): the first length(x) samples of conv(x,h) match filter(h,1,x).\n' ...
    'conv also returns the M-sample tail after the input ends; filter does not.\n']);
