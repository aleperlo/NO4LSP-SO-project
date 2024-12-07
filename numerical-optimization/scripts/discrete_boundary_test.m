clear all; clc;

n = 10^3;
h = 1/(n+1);
x0 = zeros(n, 1);
for i = 1:n
    x0(i) = i*h*(1 - i*h);
end

f = @discrete_boundary;
gradf = @discrete_boundary_gradf;
Hessf = @discrete_boundary_Hessf;

load('data/forcing_terms.mat');
beta = 10^-3;
kmax = 5*10^4;
tolgrad = 1e-10;
c1 = 1e-4;
rho = 0.8;
btmax = 100;
max_chol_iter = 100;
pcg_maxit = 1000;


[xk, fk, gradfk_norm, k, ~, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, max_chol_iter, false);

disp(['MODIFIED Newton converged in ', num2str(k), ' iterations.'])
disp(['The x value at the solution is ', mat2str(xk), '.'])
disp(['The function value at the solution is ', mat2str(fk), '.'])


% [xk, fk, gradfk_norm, k, ~, ~] = ...
%     truncated_newton(x0, f, gradf, Hessf, kmax, tolgrad, c1, rho, btmax, fterms_lin, pcg_maxit, false);

% disp(['TRUNCATED Newton converged in ', num2str(k), ' iterations.'])
% % disp(['The x value at the solution is ', mat2str(xk), '.'])
% disp(['The function value at the solution is ', mat2str(fk), '.'])
