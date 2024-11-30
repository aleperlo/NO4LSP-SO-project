function [Hessf] = chained_rosenbrock_Hessf(x)
n = length(x);
Hessf = zeros(n, n);

for i = 2:n-1
    Hessf(i, i) = 1200*x(i)^2 - 400*x(i+1) + 202;
    Hessf(i, i+1) = -400*x(i);
    Hessf(i+1, i) = -400*x(i);
end
Hessf(1, 1) = 1200*x(1)^2 - 400*x(2) + 2;
Hessf(n, n) = 200;
end