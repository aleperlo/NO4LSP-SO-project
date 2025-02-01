function [gradf] = discrete_boundary_gradf(x)
n = length(x);
h = 1/(n+1);
x_i = x(1:n);
x_i_m1 = [0; x(1:n-1)];
x_i_p1 = [x(2:n); 0];
i = linspace(1, n, n)';
gradf = zeros(n,1);
factor = 2*(2*x_i - x_i_m1 - x_i_p1 + h^2*(x_i + i*h + 1).^3/2);

gradf(1) = factor(1)*(h^2*3/2*(x_i(1) + h + 1)^2 + 1);
gradf(n) = factor(n)*(h^2*3/2*(x_i(n) + n*h + 1)^2 + 1);
gradf(2:n-1) = factor(2:n-1).*(h^2*3/2*(x_i(2:n-1) + i(2:n-1)*h + 1).^2);
end