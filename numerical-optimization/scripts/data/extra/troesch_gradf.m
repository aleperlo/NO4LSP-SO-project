function [gradf] = troesch_gradf(x)
    rho = 10;
    n = size(x, 1);
    h = 1/(n + 1);
    gradf = zeros(n, 1);

    f1 = 2*x(1) + rho*h^2*sinh(rho*x(1)) - x(2);
    fn = 2*x(n) + rho*h^2*sinh(rho*x(n)) - x(n-1) - 1;
    fk = [f1; 2*x(2:n-1) + rho*h^2*sinh(rho*x(2:n-1)) - x(1:n-2) - x(3:n); fn];

    g = 2 + rho^2*h^2*cosh(rho*x);
    gk = [0; -fk(1:n-2) - fk(3:n) + fk(2:n-1).*g(2:n-1); 0];
    gradf(2:n-1) = gk(2:n-1);
    gradf(1) = -fk(2) + f1*g(1);
    gradf(n) = -fk(n-1) + fn*g(n);
end