function [f] = brown_generalization_1(x)
    n = size(x, 1);
    f = sum(x(1:2:n-1) - 3)^2;
    for i = 2:2:n
        f = f + (x(i-1)-3)^2/1000 - (x(i-1) - x(i)) + exp(20*(x(i-1) - x(i)));
    end
end