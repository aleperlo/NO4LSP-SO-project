function [Hessf] = banded_trigonometric_Hessf_fd(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    i = (1:n)';
    diagonal = (-i.*cos(x) + 2*sin(x)).*(-1) ...
        + (i.*sin(x) + 2*cos(x)).*(-hs);
    diagonal(n) = (-n.*cos(x(n)) - (n-1)*sin(x(n))).*(-1) ...
        + (n.*sin(x(n)) - (n-1)*cos(x(n))).*(-hs(n));
    Hessf = spdiags(diagonal, 0, n, n);
end