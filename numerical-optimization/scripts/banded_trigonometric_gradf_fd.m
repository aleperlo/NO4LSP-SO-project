function [gradf] = banded_trigonometric_gradf_fd(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    i = (1:n-1)';

    gradf = [
        2*i.*sin(x(1:n-1)).*sin(hs(1:n-1)) + 4*cos(x(1:n-1)).*sin(hs(1:n-1));
        2*n.*sin(x(n)).*sin(hs(n)) - 2*(n-1)*cos(x(n)).*sin(hs(n));
    ];
    gradf = gradf ./ (2*hs);
end