function [Hessf] = banded_trigonometric_Hessf_fd1(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    i = (1:n)';
    diagonal = (-i.*cos(x) + 2*sin(x)).*(-hs.^2) ...
        + (i.*sin(x) + 2*cos(x)).*(-hs.^3);
    diagonal(n) = (-n.*cos(x(n)) - (n-1)*sin(x(n))).*(-hs(n).^2) ...
        + (n.*sin(x(n)) - (n-1)*cos(x(n))).*(-hs(n).^3);
    diagonal = diagonal ./ hs.^2;
    Hessf = spdiags(diagonal, 0, n, n);
end