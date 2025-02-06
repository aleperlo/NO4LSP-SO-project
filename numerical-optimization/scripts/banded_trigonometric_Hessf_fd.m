function [Hessf] = banded_trigonometric_Hessf_fd(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    i = (2:n-1)';
    F = @(x) [
        -cos(x(1)) + 2*sin(x(1));
        -i.*cos(x(i)) + 2*sin(x(i));
        -n*cos(x(n)) - (n-1)*sin(x(n))
    ];

    diagonal = (F(x + 2*hs) - 2*F(x + hs) + F(x)) ./ hs.^2;
    Hessf = spdiags(diagonal, 0, n, n);
end