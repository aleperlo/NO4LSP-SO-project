function [f] = extended_rosenbrock(x)
n = length(x);
fk_odd = @(x) 10*(x(1:2:n-1).^2 - x(2:2:n));
fk_even = @(x) x(1:2:n-1) - 1;
f = 0.5*sum(fk_odd(x).^2 + fk_even(x).^2);
end