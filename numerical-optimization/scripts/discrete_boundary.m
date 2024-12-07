function [f] = discrete_boundary(x)
n = length(x);
h = 1/(n+1);
x_i = x(1:n);
x_i_m1 = [0; x(1:n-1)];
x_i_p1 = [x(2:n); 0];
i = linspace(1, n, n)';
f = sum((2*x_i - x_i_m1 - x_i_p1 + h^2*(x_i + h*i + 1).^3/2).^2);
end