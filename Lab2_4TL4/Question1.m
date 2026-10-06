%%Question 1:
%%Part a:
x = unit_step(0) - unit_step(10);  %create rectangular pulse

x = x(x ~= 0); %%remove all the 0 element in the x[n]

n = 0:9; %x axis

%plot the rectangular pulse

stem(n,x,"filled");
xlabel('n');
ylabel('x[n]');
title('x[n] = u[n]- u[n-10]');
%% Part b and c :

%do the convolution
a= conv(x,x);
b= conv(a,x);
c= conv(b,x);
d= conv(c,x);

%plot the result of convolutions
figure;
subplot(4,1,1);
stem(0:length(a)-1, a,"filled");
title('a = x*x');
xlabel('n');
ylabel('a[n]');

subplot(4,1,2);
stem(0:length(b)-1, b,"filled");
title('b = a*x');
xlabel('n');
ylabel('b[n]');

subplot(4,1,3);
stem(0:length(c)-1, c,"filled");
title('c = b*x');
xlabel('n');
ylabel('c[n]');

subplot(4,1,4);
stem(0:length(d)-1, d,"filled");
title('d = c*x');
xlabel('n');
ylabel('d[n]');




%% function used in the question

function[x] = unit_step(shift)

%if the starting sample of unit steps exceeds the maximum samples, ignore the shifting
if shift > 100
    return 
end

% the samples at the left of the starting sample is 0, and the others are
% 1.
for i = 0:100    
    if i < shift
        x(i+1) = 0;  %%since matlab do not have 0 index, i+1 will be represented the first number x[0]
    else
        x(i+1) = 1;
    end
end
end
