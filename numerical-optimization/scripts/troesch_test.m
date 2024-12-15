clear all; clc;

n = 1e2;
x0 = ones(n, 1);

f = @troesch;
gradf = @troesch_gradf;
Hessf = @troesch_Hessf;

load('data/forcing_terms.mat');
beta = 10^-3;
kmax = 5*10^3;
tolgrad = 1e-3;
c1 = 1e-4;
rho = 0.8;
btmax = 100;
max_chol_iter = 100;
pcg_maxit = 1000;


% [xk, fk, gradfk_norm, k, ~, ~] = ...
%     modified_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter, false);

% disp(['MODIFIED Newton converged in ', num2str(k), ' iterations.'])
% %disp(['The x value at the solution is ', mat2str(xk), '.'])
% disp(['The function value at the solution is ', mat2str(fk), '.'])


[xk, fk, gradfk_norm, k, ~, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, kmax, tolgrad, c1, rho, btmax, fterms_lin, pcg_maxit, false);

disp(['TRUNCATED Newton converged in ', num2str(k), ' iterations.'])
%disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])