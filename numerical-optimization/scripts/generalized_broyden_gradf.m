function [gradf] = generalized_broyden_gradf(x)
    n = length(x);
    fk_function = @(x) (3-2*x).*x + 1 - [0; x(1:end-1)] - [x(2:end); 0];
    fk = fk_function(x);
    gradf = zeros(n, 1);
    gradf(2:n-1) = (3-4*x(2:n-1)).*fk(2:n-1) - fk(3:n) - fk(1:n-2);
    gradf(1) = (3-4*x(1))*fk(1) - fk(2);
    gradf(n) = (3-4*x(n))*fk(n) - fk(n-1);
end