clear all; clc;

n = 1e5;
x0 = banded_trigonometric_initializer(n);

f = @banded_trigonometric;
h = 1e-6;
gradf = @banded_trigonometric_gradf;
Hessf = @banded_trigonometric_Hessf;

load('data/forcing_terms.mat');
beta = 1e-3;
kmax = 1e3;
tolgrad = 1e-8;
c1 = 1e-4;
rho = 0.5;
btmax = 100;
max_chol_iter = 100;
pcg_maxit = 1000;

tic;
[~, fk, gradfk_norm, k, T1, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter, true, false);
toc
disp(['MODIFIED Newton converged in ', num2str(k), ' iterations.'])
disp(['The gradient norm at the solution is ', mat2str(gradfk_norm), '.'])
% disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])

tic;
[xk, fk, gradfk_norm, k, T2, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, kmax, tolgrad, c1, rho, btmax, fterms_lin, pcg_maxit, true, false);
toc
disp(['TRUNCATED Newton converged in ', num2str(k), ' iterations.'])
disp(['The gradient norm at the solution is ', mat2str(gradfk_norm), '.'])
% disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])