function [Hessf] = extended_rosenbrock_Hessf_fd(x, h, relative)
    n = length(x);
    Bin = zeros(n, 3);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    F_odd_diag = @(y) 1/2*10^2*(y.^2 - x(2:2:n)).^2 + 1/2*(y - 1).^2;
    F_even_diag = @(y) 1/2*10^2*(x(1:2:n).^2 - y).^2;
    F_diag = @(y) reshape([F_odd_diag(y(1:2:end)), F_even_diag(y(2:2:end))]', [], 1);

    F_off = @(y) 1/2*10^2*(y(1:2:end).^2 - y(2:2:end)).^2 + 1/2*(y(1:2:end) - 1).^2;
    h_odd = zeros(n, 1);
    h_odd(1:2:n) = hs(1:2:n);
    h_even = zeros(n, 1);
    h_even(2:2:n) = hs(2:2:n);

    Bin(:,2) = (F_diag(x + 2*hs) - 2*F_diag(x + hs) + F_diag(x)) ./ hs.^2;
    Bin(1:2:n-1, 1) = (F_off(x + hs) - F_off(x + h_odd) - F_off(x + h_even) + F_off(x)) ./ (hs(1:2:n).*hs(2:2:n));
    Bin(2:2:n, 3) = Bin(1:2:n-1, 1);
    Hessf = spdiags(Bin, -1:1, n, n);
end