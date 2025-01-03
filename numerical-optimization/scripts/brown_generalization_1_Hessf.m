function [Hessf] = brown_generalization_1_Hessf(x)
    n = size(x, 1);
    Bin = zeros(n, 3);
    x_odd = x(1:2:n-1);
    x_even = x(2:2:n);
    % Diagonal
    Bin(1:2:n-1, 2) = 2/1000 + 400*exp(20*(x_odd - x_even)) + 2;
    Bin(2:2:n, 2) = 400*exp(20*(x_odd - x_even));
    % Off-diagonal
    Bin(1:2:n-1, 1) = -400*exp(20*(x_odd - x_even));
    Bin(2:n, 3) = Bin(1:n-1, 1);
    Hessf = spdiags(Bin, -1:1, n, n);
    % Vectorize the nested loops
    [row, col] = meshgrid(1:2:n, 1:2:n); % Odd row and column indices
    is_diag = (row == col);              % Identify diagonal elements
    row = row(~is_diag);                 % Exclude diagonal rows
    col = col(~is_diag);                 % Exclude diagonal columns
    Hessf = Hessf + sparse(row, col, 2, n, n);
end