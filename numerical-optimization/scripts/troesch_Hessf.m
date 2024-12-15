function [Hessf] = troesch_Hessf(x)
    rho = 10;
    n = size(x, 1);
    h = 1/(n + 1);

    g = @(k) 2 + rho^2*h^2*cosh(rho*x(k));

    d = @(k) 2 + g(k)^2 + rho^3 * h^2 * sinh(rho*x(k));
    diag = arrayfun(d, 1:n);

    cd = @(k) -2 - rho^2 * h^2 * cosh(rho*x(k)) - g(k);
    codiag = arrayfun(cd, 1:n-1);

    Bin = zeros(n, 3);
    Bin(:, 2) = diag;
    Bin(1:n-1, 1) = codiag;
    Bin(2:n, 3) = codiag;
    Hessf = spdiags(Bin, -1:1, n, n);
end