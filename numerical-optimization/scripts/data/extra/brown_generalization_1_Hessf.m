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
    % Vectorize the nested loops
    [odd_row, odd_col] = meshgrid(1:2:n, 1:2:n); % Odd row and column indices
    is_diag = (odd_row == odd_col);              % Identify diagonal elements
    odd_row = odd_row(~is_diag);                 % Exclude diagonal rows
    odd_col = odd_col(~is_diag);                 % Exclude diagonal columns
    odd_entries = 2 * ones(size(odd_row, 1), 1); % Odd entries
    row  = [odd_row; (1:n)'; (2:n)'; (1:n-1)'];
    col = [odd_col; (1:n)'; (1:n-1)'; (2:n)'];
    entries = [odd_entries; Bin(1:n, 2); Bin(1:n-1, 1); Bin(2:n, 3)];
    Hessf = sparse(row, col, entries, n, n);
end