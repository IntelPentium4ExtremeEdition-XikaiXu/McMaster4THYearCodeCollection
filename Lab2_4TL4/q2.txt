%% This is the question 2

%a) load the impulse response
[impr, fs] = audioread('roomIR.wav');
%part b plot the impulse response
figure;
plot(impr);
xlabel('samples');
ylabel('Ampitutes');
title("impluse response")
hold on;
soundsc(impr,fs);  %play the impulse response
%% partc
%Load the supplied speech signal
[y,fs] = audioread('convolution.wav');
%soundsc(y,fs);  %%original audio sound
 
%do the convolution and plot the result
x = conv(y, impr); 
figure;
plot(x);

xlabel('samples');
ylabel("'y's impulse response");
title("convolution between y[n] and impr[n]")

hold on;
%play the convolution result.
soundsc(x,fs);  %%audio sound with some echo
