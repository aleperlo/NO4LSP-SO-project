function [Hessf] = troesch_Hessf(x)
    rho = 10;
    n = size(x, 1);
    h = 1/(n + 1);

    g = 2 + rho^2*h^2*cosh(rho*x);

    d = 2 + g.^2 + rho^3 * h^2 * sinh(rho*x);

    cd = -2 - rho^2 * h^2 * cosh(rho*x(1:n-1)) - g(1:n-1);

    Bin = zeros(n, 3);
    Bin(:, 2) = d;
    Bin(1:n-1, 1) = cd;
    Bin(2:n, 3) = cd;
    Hessf = spdiags(Bin, -1:1, n, n);
end