function [gradf] = generalized_broyden_gradf_fd(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    fk = @(y) (3-2*y).*y + 1 - [0; x(1:n-1)] - [x(2:n); 0];
    fkp1 = @(y) [(3-2*x(2:n)).*x(2:n) + 1 - y(1:n-1) - [x(3:n); 0]; 0];
    fkm1 = @(y) [0; (3-2*x(1:n-1)).*x(1:n-1) + 1 - [0; x(1:n-2)] - y(2:n)];
    F = @(y) 1/2 * (fk(y).^2 + fkp1(y).^2 + fkm1(y).^2);
    gradf = (F(x + hs) - F(x - hs)) ./ (2*hs);
end