function [Hessf] = banded_trigonometric_Hessf(x)
    n = length(x);
    diag_entries = zeros(n, 1);
    i = (2:n-1)';
    diag_entries(2:n-1) = i.*cos(x(2:n-1)) - 2*sin(x(2:n-1));
    diag_entries(1) = cos(x(1)) - 2*sin(x(1));
    diag_entries(n) = n*cos(x(n)) + (n-1)*sin(x(n));
    Hessf = spdiags(diag_entries, 0, n, n);
end