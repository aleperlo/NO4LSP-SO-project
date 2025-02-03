clear all; clc;

n = 1e4;
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

load('data/forcing_terms.mat');
beta = 10^-3;
kmax = 50*10^3;
tolgrad = 1e-6;
c1 = 1e-4;
rho = 0.8;
btmax = 100;
max_chol_iter = 100;
pcg_maxit = 1000;

tic;
[xk, fk, gradfk_norm, k, T1, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter, true, false);
toc

disp(['MODIFIED Newton converged in ', num2str(k), ' iterations.'])
% disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The norm of the gradient at the solution is ', mat2str(gradfk_norm), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])

tic;
[xk, fk, gradfk_norm, k, T2, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, kmax, tolgrad, c1, rho, btmax, fterms_suplin, pcg_maxit, true, false);
toc
disp(['TRUNCATED Newton converged in ', num2str(k), ' iterations.'])
% disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The norm of the gradient at the solution is ', mat2str(gradfk_norm), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])
% Write the table to a CSV file
% writetable(T1, 'data/1.csv');