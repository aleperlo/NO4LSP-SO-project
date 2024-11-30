clear all; clc;

n = 10^3;
x0 = zeros(n, 1);
for i = 1:n
    if mod(i, 2) == 1
        x0(i) = -1.2;
    else
        x0(i) = 1;
    end
end

f = @chained_rosenbrock;
gradf = @chained_rosenbrock_gradf;
Hessf = @chained_rosenbrock_Hessf;

beta = 10^-3;
kmax = 5*10^3;
tolgrad = 1e-8;
c1 = 1e-4;
rho = 0.8;
btmax = 50;
max_chol_iter = 100;


[xk, fk, ~, k, ~, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter);

disp(['Modified Newton converged in ', num2str(k), ' iterations.'])
disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])

fk(1)

fk(10^3)

[xk, fk, ~, k, ~, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter);

disp(['Modified Newton converged in ', num2str(k), ' iterations.'])
disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])
