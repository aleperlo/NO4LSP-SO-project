function [Hessf] = generalized_broyden_Hessf_fd(x, h, relative)
n = length(x);
if relative
    hs = h*abs(x);
else
    hs = h*ones(n, 1);
end
Bin = zeros(n, 5);
fk = @(y) (3-2*y).*y + 1 - [0; x(1:n-1)] - [x(2:n); 0];
fkp1 = @(y) [(3-2*x(2:n)).*x(2:n) + 1 - y(1:n-1) - [x(3:n); 0]; 0];
fkm1 = @(y) [0; (3-2*x(1:n-1)).*x(1:n-1) + 1 - [0; x(1:n-2)] - y(2:n)];

F = @(y) 1/2 * (fk(y).^2 + fkp1(y).^2 + fkm1(y).^2);
Bin(:, 3) = (F(x + hs) - 2*F(x) + F(x - hs)) ./ (hs.^2);

fk1 = @(y, z) (3-2*y(1:n-1)).*y(1:n-1) + 1 - [0; x(1:n-2)] - z(2:n);
fk1p = @(y, z) (3-2*z(2:n)).*z(2:n) + 1 - y(1:n-1) - [x(3:n); 0];
F1 = @(y) 1/2*(fk1(y, y).^2 + fk1p(y, y).^2);
F1m = @(y, z) 1/2*(fk1(y, z).^2 + fk1p(y, z).^2);
Bin(1:n-1, 2) = (F1(x + hs) - F1m(x + hs, x) - F1m(x, x+hs) + F1(x)) ./ (hs(1:n-1).*hs(2:n));
Bin(2:n, 4) = Bin(1:n-1, 2);

fk2 = @(y, z) (3-2*x(2:n-1)).*x(2:n-1) + 1 - y(1:n-2) - z(3:n); 0;
F2 = @(y) 1/2*fk2(y, y).^2;
Bin(1:n-2, 1) = (F2(x+hs) - 1/2*fk2(x+hs, x).^2 - 1/2*fk2(x, x+hs).^2 + F2(x)) ./ (hs(1:n-2).*hs(3:n));
Bin(3:n, 5) = Bin(1:n-2, 1);

Hessf = spdiags(Bin, -2:2, n, n);
end