%% This is the question 2
%
%
%a
[impr, fs] = audioread('roomIR.wav');
%b ``
plot(impr);
xlable('samples');
ylable('Ampitutes');
hold on;
soundsc(impr);

%c

[y,fs] = audioread('convolution.wav');

%d
%
x = conv(y, impr);

plot(x);

xlable('samples');
ylable('y's impulse response');

hold on;


