function [gradf] = banded_trigonometric_gradf(x)
    n = length(x);
    i = (2:n-1)';
    gradf = zeros(n, 1);
    gradf(2:n-1) = i.*sin(x(2:n-1)) + 2*cos(x(2:n-1));
    gradf(1) = sin(x(1)) + 2*cos(x(1));
    gradf(n) = n*sin(x(n)) - (n-1)*cos(x(n));
end