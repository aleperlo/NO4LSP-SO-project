clear all; clc;

n = 1e4;
x0 = zeros(n, 1);
for i = 1:n
    if mod(i, 2) == 1
        x0(i) = 0;
    else
        x0(i) = -1;
    end
end

f = @brown_generalization_1;
gradf = @brown_generalization_1_gradf;
Hessf = @brown_generalization_1_Hessf;
% gradf = @(x) findiff_grad(f, x, 1e-8, 'fw');
% Hessf = @(x) findiff_banded(gradf, x, 1e-12, 1);
% Hessf = @(x) findiff_Hess(f, x, 1e-8);

load('data/forcing_terms.mat');
beta = 10^-3;
kmax = 5e3;
tolgrad = 1e-6;
c1 = 1e-4;
rho = 0.8;
btmax = 100;
max_chol_iter = 100;
pcg_maxit = 1000;


[xk, fk, gradfk_norm, k, ~, ~] = ...
   modified_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter, false);

disp(['MODIFIED Newton converged in ', num2str(k), ' iterations.'])
% disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])


[xk, fk, gradfk_norm, k, ~, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, kmax, tolgrad, c1, rho, btmax, fterms_lin, pcg_maxit, false);

disp(['TRUNCATED Newton converged in ', num2str(k), ' iterations.'])
% disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])
