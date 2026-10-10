

% defined the delta function 
delta = @(x, x0) double(x == x0);
% defined the RMS function: 


h1n = (n) (1/4)delta(n) + (1/2)delta(n,-1) + (1/4)delta(n, -2);
h2n = (n) (-1/4)delta(n) + (1/2)delta(n,-1) + (-1/4)delta(n, -2);

xa = (n) 5*cos(0*n);
xb = (n) 5*cos((pi/5)*n);
xc = (n) 5*cos((2*pi/5)*n);
xd = (n) 5*cos((3*pi/5)*n);
xe = (n) 5*cos((4*pi/5)*n);
f = (n) 5*cos(pi*n);

%calculated the RMS: 
%
for i in length(x):
  summary = x *2 ;

summary = sqrt(summary);
return summary;



%%part 2  
output_dtft = calculated_dtft(x,w);

n = 0:length(x)-1;

%b)
%c)

plot;
ytitle('Freq domain');
xtitle('Ampitude');
hold on;

%%Part C: Gaussian distrbute noise 
%a)


%b)



