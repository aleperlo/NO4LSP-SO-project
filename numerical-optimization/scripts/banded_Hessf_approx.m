function [Hessf] = banded_Hessf_approx(f, x, h, codiags, relative)
    n = length(x);
    Bin = zeros(codiags, 1);
    fx = f(x);
    if relative
        hs = h * abs(x);
    else
        hs = h * ones(n, 1);
    end

    for i = 1:n
        perturbation = zeros(n, 1);
        perturbation(i) = hs(i);
        xhp = x + perturbation;
        x2hp = x + 2 * perturbation;
        xhm = x - perturbation;
        x2hm = x - 2 * perturbation;
        Bin(i, codiags + 1) = (-f(x2hp) + 16*f(xhp) -30*fx + 16*f(xhm) - f(x2hm)) / (12*hs(i)^2);
    end

    if codiags == 0
        Hessf = spdiags(Bin, 0, n, n);
        return
    end

    for codiag = 1:codiags
        for i = 1:n-codiag
            perturbation_i = zeros(n, 1);
            perturbation_i(i) = hs(i);
            perturbation_j = zeros(n, 1);
            perturbation_j(i+codiag) = hs(i+codiag);
            fipjp = f(x + perturbation_i + perturbation_j);
            fimjp = f(x - perturbation_i + perturbation_j);
            fipjm = f(x + perturbation_i - perturbation_j);
            fimjm = f(x - perturbation_i - perturbation_j);
            Bin(i + codiag, codiags + 1 + codiag) = (fipjp - fimjp - fipjm + fimjm) / (4 * hs(i) * hs(i + codiag));
        end
        Bin(1:n-codiag, codiags + 1 - codiag) = Bin(1+codiag:n, codiags + 1 + codiag);
    end
    Hessf = spdiags(Bin, -codiags:codiags, n, n);
end