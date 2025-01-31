function [f] = banded_trigonometric(x)
    n = length(x);
    x_m1 = [0; x(1:n-1)];
    x_p1 = [x(2:n); 0];
    i = (1:n)';
    f = sum(i.*(1-cos(x) + sin(x_m1) - sin(x_p1)));
end