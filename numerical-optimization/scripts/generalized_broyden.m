function [f] = generalized_broyden(x)
    fk_function = @(x) (3-2*x).*x + 1 - [0; x(1:end-1)] - [x(2:end); 0];
    fk = fk_function(x);
    f = sum(fk.^2)/2;
end