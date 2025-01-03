function [x0] = chained_rosenbrock_initializer(n)
x0 = -1.2 * ones(n, 1);
x0(2:2:end) = 1.0;
end