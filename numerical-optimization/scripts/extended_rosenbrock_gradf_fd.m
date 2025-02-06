function [gradf] = extended_rosenbrock_gradf_fd(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    F_odd = @(y) 1/2*10^2*(y.^2 - x(2:2:n)).^2 + 1/2*(y - 1).^2;
    F_even = @(y) 1/2*10^2*(x(1:2:n).^2 - y).^2;
    F = @(y) reshape([F_odd(y(1:2:end)), F_even(y(2:2:end))]', [], 1);

    gradf = (F(x+hs) - F(x-hs)) ./ (2*hs);
end