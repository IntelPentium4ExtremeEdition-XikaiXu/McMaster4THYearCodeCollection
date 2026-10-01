%% This is the question 2

%a
[impr, fs] = audioread('roomIR.wav');
%part b ``
figure;
plot(impr);
xlabel('samples');
ylabel('Ampitutes');
title("impluse response")
hold on;
soundsc(impr,fs);
%% partc

[y,fs] = audioread('convolution.wav');
%soundsc(y,fs);  %%original audio sound
 
x = conv(y, impr);
figure;
plot(x);

xlabel('samples');
ylabel("'y's impulse response");
title("convolution between y[n] and impr[n]")

hold on;
soundsc(x,fs);  %%audio sound with some echo
