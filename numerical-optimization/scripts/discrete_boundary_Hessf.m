function [Hessf] = discrete_boundary_Hessf(x)
n = length(x);
h = 1/(n+1);
Hessf_diag = zeros(n, 1);
i = linspace(1, n, n)';

Hessf_diag(1) = 2*(2+3*h^2/2*(x(1) + h + 1)^2)*(3*h^2/2*(x(1) + h + 1)^2 + 1);
Hessf_diag(n) = 2*(2+3*h^2/2*(x(n) + n*h + 1)^2)*(3*h^2/2*(x(n) + n*h + 1)^2 + 1);
Hessf_diag(2:n-1) = 2*(2+3*h^2/2*(x(2:n-1) + i(2:n-1)*h + 1).^2).*(3*h^2/2*(x(2:n-1) + i(2:n-1)*h + 1).^2 + 1);
Hessf_codiag = -3*h^2*(x(2:n) + i(2:n)*h + 1).^2;

Bin = zeros(n, 3);
Bin(1:n-1, 1) = Hessf_codiag;
Bin(:,2) = Hessf_diag;
Bin(2:n, 3) = Hessf_codiag;

Hessf = spdiags(Bin, -1:1, n, n);
end