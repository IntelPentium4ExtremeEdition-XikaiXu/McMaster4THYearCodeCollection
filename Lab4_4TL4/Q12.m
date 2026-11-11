%% Question 1
%%part b
N_values = [16, 32, 64, 128, 256];

X_all = cell(1,length(N_values)); %%a box to store all the DFT values

figure;

for i = 1:length(N_values)

    N = N_values(i);

    % Generate rectangular signal using unit step
    x = unit_step(N,0) - unit_step(N,16);

    % Calculate DFT
    X_all{i} = calculate_dft(x);

    % Frequency index
    k = 0:N-1;

    % Plot DFT magnitude
    subplot(5,1,i);
    stem(k,abs(X_all{i}),'filled');
    title(['DFT Magnitude, N = ',num2str(N)]);
    xlabel('Frequency index k');
    ylabel('|X[k]|');
    grid on;

end
%% part d

%generated two box to store DTFT and corresponding radian frequency axis
w_all = cell(1,length(N_values));
X_DTFT_all= cell(1,length(N_values));
figure;

for i = 1:length(N_values)
    N = N_values(i);
    w_all{i} =  2*pi*(0:N-1)/N;
    X_DTFT_all{i} = calculate_dtft(x,w_all{i}); %since DTFT has no differences with the length of x

    % Plot DTFT magnitude
    subplot(5,1,i);
    stem(w_all{i},abs(X_DTFT_all{i}),'filled');
    title(['DTFT Magnitude, N = ',num2str(N)]);
    xlabel('Frequency w');
    ylabel('|X[w]|');
    grid on;

end
%% Part e
X_FFT_all = cell(1,length(N_values));

figure;

for i = 1:length(N_values)

    N = N_values(i);

    % Generate rectangular signal
    x = unit_step(N,0) - unit_step(N,16);

    % Calculate FFT
    X_FFT_all{i} = fft(x);

    % Plot FFT magnitude
    k = 0:N-1;

    subplot(5,1,i);
    stem(k,abs(X_FFT_all{i}),'filled');
    title(['FFT Magnitude, N = ',num2str(N)]);
    xlabel('Frequency index k');
    ylabel('|X[k]|');
    grid on;

end


%% Question 2


%% Part a
[x, Fs] = audioread('aaa.wav'); % load the audio file
disp(Fs);
N = length(x);
disp(N);
%% part b

figure;

t = (0:299)/Fs; %%choose first 300 samples

plot(t,x(1:300));
xlabel('Time (seconds)');
ylabel('Amplitude');
title('First 300 Samples of Vowel /A/');
grid on;

%% part c 
T = (0.03475 - 0.024875);
TN=  int64(T*Fs);

x1 = x(1:TN);
x2 = x(1:2*TN);

% Calculate DFT
X1 = calculate_dft(x1);
X2 = calculate_dft(x2);

% Frequency vectors (Hz)
N1 = length(x1);
N2 = length(x2);

k1 = (0:N1-1)*Fs/N1;
k2 = (0:N2-1)*Fs/N2;

% Plot DFT magnitude
figure;

subplot(2,1,1);
stem(k1,abs(X1),'filled');
title('DFT of One Natural Period');
xlabel('Frequency index');
ylabel('Magnitude');
grid on;

subplot(2,1,2);
stem(k2,abs(X2),'filled');
title('DFT of Two Natural Periods');
xlabel('Frequency index');
ylabel('Magnitude');
grid on
%% Part d
x1_zero = zeros(1,1024);
x2_zero = zeros(1,1024);

% Zero-padding x1
for i = 1:TN
    x1_zero(i) = x1(i);
end

% Zero-padding x2
for i = 1:2*TN
    x2_zero(i) = x2(i);
end

% Calculate DFT
X1_zero = calculate_dft(x1_zero);
X2_zero = calculate_dft(x2_zero);

k = (0:1023)*Fs/1024;

figure;

subplot(2,1,1);
stem(k,abs(X1_zero),"filled");
title('One Period Zero-padded to 1024');
xlabel('Frequency index');
ylabel('Magnitude');
grid on;

subplot(2,1,2);
stem(k,abs(X2_zero),"filled");
title('Two Periods Zero-padded to 1024');
xlabel('Frequency index');
ylabel('Magnitude');
grid on;

%% part e
windows = cell(1,5);
for i = 1:5
    windows{i} = x(1:i*TN);
end

figure;

for i = 1:5
    N = length(windows{i});

    X = calculate_dft(windows{i});

    % Frequency index
    kw = 0:N-1;

    % Plot magnitude of DFT
    subplot(5,1,i);
    stem(kw, abs(X));
    title(['Window length = ', num2str(i), 'TN']);
    xlabel('Frequency index kw');
    ylabel('|X[k]|');
    grid on;
end

%% the functions are used in the lab


function[x] = unit_step(lengthx,shift)

x=zeros(1,lengthx);
% the samples at the left of the starting sample is 0, and the others are
% 1.
for i = 0:length(x)-1    
    if i < shift
        x(i+1) = 0;  %%since matlab do not have 0 index, i+1 will be represented the first number x[0]
    else
        x(i+1) = 1;
    end
end
end

function [output_dft] = calculate_dft(x)

    N = length(x);
    k = 0:N-1;
    output_dft = zeros(size(k));

    for n = 0:N-1
        output_dft = output_dft + x(n+1)*exp(-1j*2*pi*k*n/N);
    end

end

%DTFT generated in lab 3
function [output_dtft] = calculate_dtft(x,w)
    output_dtft = zeros(size(w));
    for n = 0:length(x)-1
        output_dtft = output_dtft+x(n+1)*exp(-j*w*n);
    end

end