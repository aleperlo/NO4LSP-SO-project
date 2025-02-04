function [Hessf] = extended_rosenbrock_Hessf(x)
n = length(x);
Bin = zeros(n,3);
Bin(1:2:n-1, 2) = 200*(3*x(1:2:n-1).^2 - x(2:2:n)) + 1;
Bin(2:2:n, 2) = 100;
Bin(1:2:n-1, 1) = -200*x(1:2:n-1);
Bin(2:2:n-2, 1) = 0;
Bin(2:n, 3) = Bin(1:n-1, 1);
Hessf = spdiags(Bin, -1:1, n, n);
end