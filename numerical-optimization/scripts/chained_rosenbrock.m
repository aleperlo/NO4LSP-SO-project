function [f] =  chained_rosenbrock(x)
n = length(x);
xi = x(2:n);
xi_1 = x(1:n-1);
f = sum(100*(xi_1.^2 - xi).^2 + (xi_1 - 1).^2);
return
end