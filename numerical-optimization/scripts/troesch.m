function [y] = troesch(x)
    rho = 10;
    n = size(x, 1);
    h = 1/(n + 1);
    f1 = 2*x(1) + rho*h^2*sinh(rho*x(1)) - x(2);
    fk = @(k) 2*x(k) + rho*h^2*sinh(rho*x(k)) - x(k-1) - x(k+1);
    fn = 2*x(n) + rho*h^2*sinh(rho*x(n)) - x(n-1) - 1;
    y = .5 * (f1^2 + fn^2 + sum(arrayfun(fk, 2:n-1).^2));
end