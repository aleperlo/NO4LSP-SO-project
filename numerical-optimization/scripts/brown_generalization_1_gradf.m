function [gradf] = brown_generalization_1_gradf(x)
    n = size(x, 1);
    x_odd = x(1:2:n-1);
    x_even = x(2:2:n);
    gradf = zeros(n, 1);
    s = sum(x(1:2:n-1) - 3);
    gradf(1:2:n-1) = 2*(x_odd - 3)/1000 - 1 + 20*exp(20*(x_odd - x_even)) + 2*s;
    gradf(2:2:n) = 1 - 20*exp(20*(x_odd - x_even));
end