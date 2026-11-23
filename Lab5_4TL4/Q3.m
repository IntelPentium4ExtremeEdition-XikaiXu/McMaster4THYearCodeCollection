%% Lab 5 Q3(b-v) — DTFT of the two-pulse and three-pulse MTI cancellers
% Two-pulse:    y[n] = x[n] - x[n-1]                 h = [1, -1]
% Three-pulse:  y[n] = x[n] - 2 x[n-1] + x[n-2]      h = [1, -2, 1]
% H2(e^{jw}) = 1 - e^{-jw},            |H2| = 2 |sin(w/2)|
% H3(e^{jw}) = (1 - e^{-jw})^2,        |H3| = 4 sin^2(w/2)

clear; close all; clc;
outdir = fullfile(fileparts(mfilename('fullpath')), 'figures');
if ~exist(outdir, 'dir'); mkdir(outdir); end

h2 = [1 -1];
h3 = [1 -2 1];
nfft = 4096;
[H2, w] = freqz(h2, 1, nfft);
[H3, ~] = freqz(h3, 1, nfft);

fprintf('H2(w=0) = %.3e   (barrier / zero Doppler)\n', abs(H2(1)));
fprintf('H3(w=0) = %.3e\n', abs(H3(1)));
fprintf('|H2(pi)| = %.4f    |H3(pi)| = %.4f   (high-Doppler gain)\n', ...
    abs(H2(end)), abs(H3(end)));

figure('Name', 'Q3 MTI magnitude', 'Color', 'w', 'Position', [80 80 860 420]);
plot(w/pi, abs(H2), 'LineWidth', 1.3); hold on;
plot(w/pi, abs(H3), 'LineWidth', 1.3);
grid on; xlim([0 1]);
xlabel('\omega / \pi   (normalized Doppler)');
ylabel('|H(e^{j\omega})|');
title('MTI cancellers: both null DC; the three-pulse notch is wider');
legend('two-pulse  |1 - e^{-j\omega}| = 2|sin(\omega/2)|', ...
       'three-pulse  4 sin^2(\omega/2)', 'Location', 'northwest');
saveas(gcf, fullfile(outdir, 'q3_mti_magnitude.png'));

figure('Name', 'Q3 MTI dB', 'Color', 'w', 'Position', [100 80 860 420]);
plot(w/pi, 20*log10(abs(H2)+eps), 'LineWidth', 1.3); hold on;
plot(w/pi, 20*log10(abs(H3)+eps), 'LineWidth', 1.3);
grid on; xlim([0 1]); ylim([-80 15]);
xlabel('\omega / \pi   (normalized Doppler)');
ylabel('Magnitude (dB)');
title('Three-pulse stays down longer near 0 Hz, then has more high-frequency gain');
legend('two-pulse', 'three-pulse', 'Location', 'southeast');
saveas(gcf, fullfile(outdir, 'q3_mti_db.png'));

figure('Name', 'Q3 MTI phase', 'Color', 'w', 'Position', [120 80 860 380]);
plot(w/pi, unwrap(angle(H2)), 'LineWidth', 1.2); hold on;
plot(w/pi, unwrap(angle(H3)), 'LineWidth', 1.2);
grid on; xlim([0 1]);
xlabel('\omega / \pi'); ylabel('Unwrapped phase (rad)');
title('Both cancellers are linear-phase FIR highpass filters');
legend('two-pulse (delay 0.5)', 'three-pulse (delay 1)', 'Location', 'southwest');
saveas(gcf, fullfile(outdir, 'q3_mti_phase.png'));
