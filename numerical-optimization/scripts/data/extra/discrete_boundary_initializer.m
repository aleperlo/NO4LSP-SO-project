function [x0] = discrete_boundary_initializer(n)
h = 1/ (n + 1);
x0 = zeros(n, 1);
x0(2:end) = h * (1:n-1) * (1 - h * (1:n-1));
end