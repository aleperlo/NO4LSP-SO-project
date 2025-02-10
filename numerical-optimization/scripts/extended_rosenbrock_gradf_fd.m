function [gradf] = extended_rosenbrock_gradf_fd(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    gradf = zeros(n, 1);
    gradf(1:2:n) = 2*x(1:2:n).*hs(1:2:n) - 2*hs(1:2:n)...
        + 400*x(1:2:n).^3.*hs(1:2:n) + 400*x(1:2:n).*hs(1:2:n).^3 - 400*x(1:2:n).*x(2:2:n).*hs(1:2:n);
    gradf(2:2:n) = -200.*hs(2:2:n).*x(1:2:n).^2 + 200*hs(2:2:n).*x(2:2:n);
    gradf = gradf ./ (2*hs);

end