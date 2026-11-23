%%Question 1 
%% part a
wc = pi/3;
M_list = [20 50 150];
h_trunc = cell(1, length(M_list));
for k = 1:length(M_list)
    M = M_list(k);
    N = M + 1;
    delay = M/2;

    %Choose ideal Low-pass amplitude response
    % Aid(w) = 1 for |w| < pi/3, otherwise 0
    % Choose phase characteristics
    alpha = 0; %linear phase
    tau = delay; 

    % Calculate ideal impulse response using inverse DTFT
    n = 0:M;

    h = sin(wc*(n-tau)) ./ (pi*(n-tau)); %from slide 16 in topic 6
    % Handle the centre sample
    h(n == tau) = wc/pi;
    % Keep only N samples: n = 0, 1, ..., M
    h = h(1:N);
    h_trunc{k} = h;
    %plot the figure
    figure;
    stem(n, h, 'filled');
    grid on;
    xlabel('n');
    ylabel('h[n]');
    title(['Truncated LPF Impulse Response, M = ', num2str(M)]);

end
%% part b and c
w = linspace(-pi, pi, 1000);
%convert the 3 filter into frequency domain
H = cell(1, length(M_list));
for k = 1:length(M_list)
    H{k} = calculate_dtft(h_trunc{k}, w);
end
 
%plot the DTFT of the truncation impulse response
%magnitude
figure;
hold on;
for k = 1:length(M_list)
    plot(w, abs(H{k}),'DisplayName',['M = ', num2str(M_list(k))]);
end
xlabel('Frequency (rad/sample)');
ylabel('Magnitude');
title('Magnitude Responses of Truncated FIR Filters');
legend show;
grid on;
%Gibbs phenomenon is the maximum at the passband

%phase (linear phase)
figure;
hold on;
for k = 1:length(M_list)
    phase = angle(H{k});
    plot(w, phase, 'DisplayName', ['M = ', num2str(M_list(k))]);
end
xlim([-pi/3 pi/3]); %limit the frequency axis into the passband to have a better scaling
xlabel('Frequency (rad/sample)');
ylabel('Phase (radians)');
title('Phase Responses of Truncated FIR Filters');
legend show;
grid on;

%three straight lines passing the point (0,0)
%% part d
f = [0 wc/pi wc/pi 1];
a = [1 1 0 0];
h_firls = cell(1, length(M_list));
for k = 1:length(M_list)
    M = M_list(k);
    % Design FIR filter using firls()
    h_firls{k} = firls(M, f, a);
    % Plot and compare impulse responses
    figure;
    stem(0:M, h_trunc{k}, 'b', 'filled');
    hold on;
    stem(0:M, h_firls{k}, 'ro');
    xlabel('n');
    ylabel('h[n]');
    title(['Comparison of Impulse Responses, M = ', num2str(M)]);
    legend('Truncation Method', 'firls()');
    grid on;

end
%% part e
% Generate white Gaussian noise
rng(0804);
x = randn(1000, 1);

% Store outputs
y_conv = cell(1, length(M_list));
y_filter = cell(1, length(M_list));
for k = 1:length(M_list)
    M = M_list(k); %used in plotting
    h = h_trunc{k};
    % Convolution
    y_conv{k} = conv(x, h);
    % Using filter() function
    y_filter{k} = filter(h, 1, x);
    % Plot the outputs
    figure;
    stem(y_conv{k}, 'b');
    hold on;
    stem(y_filter{k}, 'r--');
    xlabel('Sample Index');
    ylabel('Amplitude');
    title(['Output Comparison, M = ', num2str(M)]);
    legend('conv()', 'filter()');
    grid on;
end
%% function used in the lab 
function [output_dtft] = calculate_dtft(x,w)
    output_dtft = zeros(size(w));
    for n = 0:length(x)-1
        output_dtft = output_dtft+x(n+1)*exp(-j*w*n);
    end

end