function [Hessf] = generalized_broyden_Hessf_fd1(x, h, relative)
n = length(x);
if relative
    hs = h*abs(x);
else
    hs = h*ones(n, 1);
end
Bin = zeros(n, 5);

xm1 = [0; x(1:n-1)];
xp1 = [x(2:n); 0];

% Diagonal
Bin(1:n, 3) = 24*x.^2 + 48*x.*hs - 36*x + 28*hs.^2 - 36*hs + 4*xm1 + 4*xp1 + 7;
Bin(1, 3) = 24*x(1)^2 + 48*x(1)*hs(1) - 36*x(1) + 28*hs(1)^2 - 36*hs(1) + 4*x(2) + 6;
Bin(n, 3) = 24*x(n)^2 + 48*x(n)*hs(n) - 36*x(n) + 28*hs(n)^2 - 36*hs(n) + 4*x(n-1) + 6;
% First codiagonal
Bin(1:n-1, 2) = 4*x(1:n-1) + 4*x(2:n) + 2*hs(1:n-1) + 2*hs(2:n) - 6;
Bin(2:n, 4) = Bin(1:n-1, 2);
% Second codiagonal
Bin(1:n-2, 1) = 1;
Bin(3:n, 5) = 1;

Hessf = spdiags(Bin, -2:2, n, n);
end