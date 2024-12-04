function [Hessf] = chained_rosenbrock_Hessf(x)
n = length(x);

Hessf_diag = zeros(n, 1);
Hessf_codiag = zeros(n-1, 1);
Hessf_diag(1) = 1200*x(1)^2 - 400*x(2) + 2;
Hessf_diag(n) = 200;

for i = 1:n-1
    Hessf_codiag(i) = -400*x(i);
end
for i = 2:n-1
    Hessf_diag(i) = 1200*x(i)^2 - 400*x(i+1) + 202;
end

Bin = zeros(n, 3);
Bin(1:n-1, 1) = Hessf_codiag;
Bin(:,2) = Hessf_diag;
Bin(2:n, 3) = Hessf_codiag;

Hessf = spdiags(Bin, -1:1, n, n);
end