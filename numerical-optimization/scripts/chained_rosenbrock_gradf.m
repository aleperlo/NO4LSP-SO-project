function [gradf] = chained_rosenbrock_gradf(x)
n = length(x);
gradf = zeros(n,1);

gradf(1) = 400*x(1)^3 - 400*x(1)*x(2) + 2*x(1) - 2;
gradf(n) = 200*(x(n) - x(n-1)^2);
gradf(2:n-1) = 400.*x(2:n-1).^3 - 400*x(2:n-1).*x(3:n) + 2*x(2:n-1) - 2 + 200*x(2:n-1) - 200*x(1:n-2).^2;

return
end