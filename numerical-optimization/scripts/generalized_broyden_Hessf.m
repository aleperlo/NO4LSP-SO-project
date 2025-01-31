function [Hessf] = generalized_broyden_Hessf(x)
    n = length(x);
    fk_function = @(x) (3-2*x).*x + 1 - [0; x(1:end-1)] - [x(2:end); 0];
    fk = fk_function(x);
    Bin = zeros(n, 5);
    % Main diagonal
    Bin(2:n-1, 3) = -4*fk(2:n-1) + (3-4*x(2:n-1)).^2 + 2;
    Bin(1, 3) = (3-4*x(1)).^2 - 4*fk(1) + 1;
    Bin(n, 3) = (3-4*x(n)).^2 - 4*fk(n) + 1;
    % First codiagonal
    Bin(1:n-1, 2) = 4*x(1:n-1) + 4*x(2:n) - 6;
    Bin(2:n, 4) = Bin(1:n-1, 2);
    % Second codiagonal
    Bin(1:n-2, 1) = 1;
    Bin(3:n, 5) = 1;
    % Create banded matrix
    Hessf = spdiags(Bin, -2:2, n, n);
end