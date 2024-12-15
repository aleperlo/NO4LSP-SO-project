function [gradf] = troesch_gradf(x)
    rho = 10;
    n = size(x, 1);
    h = 1/(n + 1);
    gradf = zeros(n, 1);

    f1 = 2*x(1) + rho*h^2*sinh(rho*x(1)) - x(2);
    fk = @(k) 2*x(k) + rho*h^2*sinh(rho*x(k)) - x(k-1) - x(k+1);
    fn = 2*x(n) + rho*h^2*sinh(rho*x(n)) - x(n-1) - 1;

    g = @(k) 2 + rho^2*h^2*cosh(rho*x(k));
    gk = @(k) -fk(k-1) - fk(k+1) + fk(k)*g(k);
    gradf(3:n-2) = arrayfun(gk, 3:n-2);
    gradf(1) = -fk(2) + f1*g(1);
    gradf(n) = -fk(n-1) + fn*g(n);
    gradf(2) = -f1 - fk(3) + fk(2)*g(2);
    gradf(n-1) = -fk(n-2) + fk(n-1)*g(n-1) - fn;
end