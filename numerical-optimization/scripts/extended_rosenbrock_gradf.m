function [gradf] = extended_rosenbrock_gradf(x)
n = length(x);
gradf = zeros(n,1);
gradf(1:2:n-1) = 200*x(1:2:n-1).^3 - 200*x(2:2:n).*x(1:2:n-1) + x(1:2:n-1) - 1;
gradf(2:2:n) = -100*(x(1:2:n-1).^2 - x(2:2:n));
end