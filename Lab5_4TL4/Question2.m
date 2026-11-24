%%Question 2
%% part a
%initialization
wc = pi/3;
fc = wc/pi;
orders = [20 50 150];
attenuation = 80; %could be changed 
h_fir = cell(1, length(orders));
%find the impulse response for different filter orders
for k = 1:length(orders)
    M = orders(k);
    w_window = chebwin(M+1, attenuation);
    h_fir{k} = fir1(M, fc, 'low', w_window);
end

% Calculate DTFT and plot magnitude responses
w = linspace(0, pi, 2048);

for k = 1:length(orders)
    H = calculate_dtft(h_fir{k}, w);
    figure;
    plot(w, 20*log10(abs(H)+1e-10));
    xlabel('\omega ');
    ylabel('Magnitude (dB)');
    title(['Dolph-Chebyshev FIR, M = ', num2str(orders(k))]);
    grid on;
end

%% part b
Rs = attenuation;
z_iir = cell(1, length(orders));
p_iir = cell(1, length(orders));
g_iir = zeros(1, length(orders));
% Design IIR filters
for k = 1:length(orders)
    M = orders(k);
    [z_iir{k}, p_iir{k}, g_iir(k)] = cheby2(M, Rs, fc, 'low');  %record poles, zeroes and corresponding gains
end

% Frequency range
w = linspace(-3*pi, 3*pi, 10000);

for k = 1:length(orders)
    %find the DTFT of the IRR filters
    H = calculate_iir_dtft(z_iir{k},p_iir{k},g_iir(k),w);
    %plot the figure
    figure;
    plot(w, 20*log10(abs(H)+1e-10));
    xlabel('\omega /');
    ylabel('Magnitude (dB)');
    title(['Chebyshev Type II IIR, M = ', num2str(orders(k))]);
    grid on;
end


b_iir = cell(1,length(orders));
a_iir = cell(1,length(orders));

for k = 1:length(orders)
    M = orders(k);
    [b_iir{k},a_iir{k}] = cheby2(M,Rs,fc,'low');
end

%% part c

N = 1000;  %the number of the samples in the impulse response
K = 10000; %the number of the samples chosen in the frequency domian of the impulse response

w = linspace(-pi, pi, K);
h_iir = cell(1,length(orders)); %save the impulse reponse
for k = 1:length(orders)
    %find the IIRs' DTFT
    H = calculate_iir_dtft(z_iir{k},p_iir{k},g_iir(k),w);
    %do the inverse DTFT
    h = calculate_inverse_dtft(H,w,N);
    h_iir{k} = h;
    %PLOT THE FIGURE
    figure;
    stem(0:N-1,real(h),'filled');
    xlabel('Sample n');
    ylabel('Amplitude');
    % xlim([0 200]);
    title(['Impulse Response, M = ',num2str(orders(k))]);
    grid on;
end

%% part d

w = linspace(0, pi, 2048);
for k = 1:length(orders)
    % FIR frequency response
    H_fir = calculate_dtft(h_fir{k},w);
    % IIR frequency response
    H_iir = calculate_iir_dtft(z_iir{k},p_iir{k},g_iir(k),w);
    
    %plot the phase of frequency response of FIR and IIR filters
    figure;
    % Compare magnitude responses
    subplot(2,1,1);
    plot(w,20*log10(abs(H_fir)+1e-10));
    hold on;
    plot(w,20*log10(abs(H_iir)+1e-10));
    hold off;
    xlabel('\omega');
    ylabel('Magnitude (dB)');
    title(['Magnitude Comparison, M = ',num2str(orders(k))]);
    legend('FIR','IIR');
    grid on;

    % Compare phase responses
    subplot(2,1,2);
    plot(w,unwrap(angle(H_fir)));
    hold on;
    plot(w,unwrap(angle(H_iir)));
    hold off;
    xlabel('\omega');
    ylabel('Phase (radians)');
    title('Phase Comparison');
    legend('FIR','IIR');
    grid on;

end
%% part e
% x = randn(1,1000); % Generate 1000 samples of white Gaussian noise
% for k = 1:length(orders)
%     % Get the filter coefficients
%     b = b_iir{k};
%     a = a_iir{k};
%     % Get the impulse response from Part (c)
%     h = h_iir{k};
%     % Calculate the output using filter()
%     y_filter = filter(b,a,x);
%     % Estimate the output using convolution
%     y_conv = conv(x,h);
% 
%     % Keep only the first 1000 samples for comparison
%     y_conv = y_conv(1:length(x));
% 
%     % Plot the output comparison
%     figure;
%     plot(0:length(x)-1,y_filter);
%     hold on;
%     plot(0:length(x)-1,real(y_conv),'--');
%     hold off;
%     xlabel('Sample n');
%     ylabel('Amplitude');
%     title(['Output Comparison, M = ',num2str(orders(k))]);
%     legend('filter()','conv()');
%     grid on;
% end

%% Part (e)

x = randn(1,1000); % Generate 1000 samples of Gaussian noise
for k = 1:length(orders)
    % Get the filter coefficients in zero-pole-gain form
    z = z_iir{k};
    p = p_iir{k};
    g = g_iir(k);
    % Convert the filter into second-order sections
    [sos, gain] = zp2sos(z,p,g);
    sos(1,1:3) = gain*sos(1,1:3);
    % Calculate the output using SOS
    y_filter = x(:);
    for s = 1:size(sos,1)
        b = sos(s,1:3);
        a = sos(s,4:6);
        y_filter = filter(b,a,y_filter);
    end
    % Get the impulse response from Part (c)
    h = h_iir{k};
    % Estimate the output using convolution
    y_conv = conv(x,h);
    y_conv = y_conv(1:length(x));
    % Plot the output comparison
    figure;
    plot(0:length(x)-1,y_filter);
    hold on;
    plot(0:length(x)-1,real(y_conv),'--');
    hold off;
    xlabel('Sample n');
    ylabel('Amplitude');
    title(['Output Comparison, M = ',num2str(orders(k))]);
    legend('SOS filter','Convolution');
    grid on;
    % Calculate the relative error
    error = y_filter(:)-real(y_conv(:));
    relative_error = norm(error)/norm(y_filter);
    fprintf('M = %d, Relative error = %.6e\n', ...
        orders(k),relative_error);

end
%% function used in the question
%DTFT generated in lab 3
function [output_dtft] = calculate_dtft(x,w)
    output_dtft = zeros(size(w));
    for n = 0:length(x)-1
        output_dtft = output_dtft+x(n+1)*exp(-j*w*n);
    end

end


function H = calculate_iir_dtft(z, p, g, w)
    numerator = g*ones(size(w));
    denominator = ones(size(w));
    % Calculate numerator using zeros
    for n = 1:length(z)
        numerator = numerator .* (1-z(n)*exp(-1j*w));
    end
    % Calculate denominator using poles
    for n = 1:length(p)
        denominator = denominator .* (1-p(n)*exp(-1j*w));
    end
    % Calculate frequency response
    H = numerator ./ denominator;

end

function h = calculate_inverse_dtft(H, w, N)

    K = length(w);
    h = zeros(1,N);

    for n = 0:N-1
        for k = 1:K
            h(n+1) = h(n+1) + H(k)*exp(1j*w(k)*n);
        end

        h(n+1) = h(n+1)/K;
    end

end