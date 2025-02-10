function [Hessf] = extended_rosenbrock_Hessf_fd(x, h, relative)
    n = length(x);
    Bin = zeros(n, 3);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    
    % Diagonal
    Bin(1:2:n, 2) = 1200*hs(1:2:n).*x(1:2:n) - 200.*x(2:2:n)...
        + 1 + 700*hs(1:2:n).^2 + 600*x(1:2:n).^2;
    Bin(2:2:n, 2) = 100;
    % Off-diagonal
    Bin(1:2:n, 1) = -100*hs(1:2:n) - 200*x(1:2:n);
    Bin(2:2:n, 3) = Bin(1:2:n, 1);
    Hessf = spdiags(Bin, -1:1, n, n);
end