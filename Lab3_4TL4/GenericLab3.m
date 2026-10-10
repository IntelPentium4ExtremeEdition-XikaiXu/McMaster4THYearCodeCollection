

% defined the delta function 
delta = @(x, x0) double(x == x0);
% defined the RMS function: 

for i in length(n)

h1n = (n) (1/4)delta(n) + (1/2)delta(n,-1) + (1/4)delta(n, -2);
h2n = (n) (-1/4)delta(n) + (1/2)delta(n,-1) + (-1/4)delta(n, -2);

xa = (n) 5*cos(0*n);
xb = (n) 5*cos((pi/5)*n);
xc = (n) 5*cos((2*pi/5)*n);
xd = (n) 5*cos((3*pi/5)*n);
xe = (n) 5*cos((4*pi/5)*n);
xf = (n) 5*cos(pi*n);