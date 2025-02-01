function [y] = troesch(x)
    rho = 10;
    n = size(x, 1);
    h = 1/(n + 1);
    f1 = 2*x(1) + rho*h^2*sinh(rho*x(1)) - x(2);
    fn = 2*x(n) + rho*h^2*sinh(rho*x(n)) - x(n-1) - 1;
    fk = [f1; 2*x(2:n-1) + rho*h^2*sinh(rho*x(2:n-1)) - x(1:n-2) - x(3:n); fn];

    y = .5 * (sum(fk.^2));
end