%%Question 1
%% part a
%generate the impulse response and 6 discrete time signal
n = 0 :50;

h1= 1/4*delta(0)+1/2*delta(1)+1/4*delta(2);
h2= -1/4*delta(0)+1/2*delta(1)-1/4*delta(2);


xa= 5*cos(0*n);
xb= 5*cos(pi/5*n);
xc= 5*cos(2*pi/5*n);
xd= 5*cos(3*pi/5*n);
xe= 5*cos(4*pi/5*n);
xf= 5*cos(pi*n);
%% part b 
%find the RMS of the each signal
Ea= RMS(xa);
Eb= RMS(xb);
Ec= RMS(xc);
Ed= RMS(xd);
Ee= RMS(xe);
Ef= RMS(xf);
%% part c
%do the convolution, and then find the rms of the output signals
Y_ah1 = conv(h1,xa);
Y_bh1 = conv(h1,xb);
Y_ch1 = conv(h1,xc);
Y_dh1 = conv(h1,xd);
Y_eh1 = conv(h1,xe);
Y_fh1 = conv(h1,xf);

Eah1= RMS(Y_ah1);
Ebh1= RMS(Y_bh1);
Ech1= RMS(Y_ch1);
Edh1= RMS(Y_dh1);
Eeh1= RMS(Y_eh1);
Efh1= RMS(Y_fh1);

RMS_in = [Ea, Eb, Ec, Ed, Ee, Ef];
RMS_out = [Eah1, Ebh1, Ech1, Edh1, Eeh1, Efh1];

%find the gain values and plot the gains
Gain1 = 20*log10(RMS_out ./ RMS_in);

w = [0, pi/5, 2*pi/5, 3*pi/5, 4*pi/5, pi];

figure;
plot(w, Gain1, 'o-');
xlabel('Frequency (rad/sample)');
ylabel('Gain (dB)');
title('Gain versus Frequency for h1');
grid on;
%% part d
%do the convolution with h2, and then find the rms of the output signals
Y_ah2 = conv(h2, xa);
Y_bh2 = conv(h2, xb);
Y_ch2 = conv(h2, xc);
Y_dh2 = conv(h2, xd);
Y_eh2 = conv(h2, xe);
Y_fh2 = conv(h2, xf);

%find the energy of the output signal
Eah2 = RMS(Y_ah2);
Ebh2 = RMS(Y_bh2);
Ech2 = RMS(Y_ch2);
Edh2 = RMS(Y_dh2);
Eeh2 = RMS(Y_eh2);
Efh2 = RMS(Y_fh2);

RMS_out = [Eah2, Ebh2, Ech2, Edh2, Eeh2, Efh2];

%find the gain and plot it
Gain2 = 20*log10(RMS_out ./ RMS_in);

figure;
plot(w, Gain2, 'o-');
xlabel('Frequency (rad/sample)');
ylabel('Gain (dB)');
title('Gain versus Frequency for h2');
grid on;


%% QUESTION 2
%% Part b
w = -3*pi:0.01:3*pi;

%calculate the DTFT of the impulse responses
H1 = calculate_dtft(h1,w);
H2 = calculate_dtft(h2,w);
%% part c
%plot the DTFT of the impulse responses
figure;

subplot(2,1,1);
plot(w, abs(H1));
xlabel('Frequency \omega (rad/sample)');
ylabel('|H_1(e^{j\omega})|');
title('Magnitude of DTFT of h1');
grid on;

subplot(2,1,2);
plot(w, abs(H2));
xlabel('Frequency \omega (rad/sample)');
ylabel('|H_2(e^{j\omega})|');
title('Magnitude of DTFT of h2');
grid on;

figure;

subplot(2,1,1);
plot(w, angle(H1));
xlabel('Frequency \omega (rad/sample)');
ylabel('Phase (rad)');
title('Phase of DTFT of h1');
grid on;

subplot(2,1,2);
plot(w, angle(H2));
xlabel('Frequency \omega (rad/sample)');
ylabel('Phase (rad)');
title('Phase of DTFT of h2');
grid on;

%% Question 3
%% part a
%create a signal with Gaussian distribution, then do the convolution with
%h1 and h2
signal = randn(1, 1000);
signalh1 = conv(signal, h1);
signalh2= conv(signal, h2);


%Calculate DTFT
S1 = calculate_dtft(signalh1, w);
S2 = calculate_dtft(signalh2, w);
%% Part b 
%plot the magnitude of the output
figure;

subplot(2,1,1);
plot(w, abs(S1));
xlabel('Frequency \omega (rad/sample)');
ylabel('|S_1(e^{j\omega})|');
title('Magnitude of DTFT of convlution between signal and h1');
grid on;

subplot(2,1,2);
plot(w, abs(S2));
xlabel('Frequency \omega (rad/sample)');
ylabel('|S_2(e^{j\omega})|');
title('Magnitude of DTFT of convlution between signal and h2');
grid on;




%% the functions are used in the lab

function[x] = delta(shift)

if shift > 50
    return 
end

% the samples at the left of the starting sample is 0, and the others are
% 1.
for i = 0:50    
    if i ~= shift
        x(i+1) = 0;  %%since matlab do not have 0 index, i+1 will be represented the first number x[0]
    else
        x(i+1) = 1;
    end
end
end


function [RMS] = RMS(x)
    N = length(x);
    sum_square = 0;
    %find the sum of square of each elements
    for n = 1:N
        sum_square = sum_square + x(n)^2;
    end
    %find the RMS
    RMS = sqrt(sum_square / N);
end


function [output_dtft] = calculate_dtft(x,w)
    output_dtft = zeros(size(w));
    for n = 0:length(x)-1
        output_dtft = output_dtft+x(n+1)*exp(-j*w*n);
    end

end

% Read the CSV file
data = readmatrix('result.csv');

% Extract data
real_part = data(:,1);
imag_part = data(:,2);
amp = data(:,3);
n = data(:,4);

% Plot
figure;
plot(n, real_part, n, imag_part, n, amp);

xlabel('Index');
ylabel('Value');
title('CSV Data vs. Index');
legend('Real', 'Imaginary', 'Amplitude');
grid on;

