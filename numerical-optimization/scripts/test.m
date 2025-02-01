function [] = test(f, gradf, Hessf, initializer, codiags,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, beta, fterms, pcg_maxit)
%
% INPUTS
% n = dimension of the problem;
% f = function handle that describes a function R^n->R;
% gradf = function handle that describes the gradient of f;
% Hessf = function handle that describes the Hessian of f;
% initializer = function handle that generate starting point x0;
% kmax = maximum number of iterations permitted;
% tolgrad = value used as stopping criterion w.r.t. the norm of the gradient;
% c1 = the factor of the Armijo condition that must be a scalar in (0,1);
% rho = fixed factor, lesser than 1, used for reducing alpha0;
% btmax = maximum number of steps for updating alpha during the backtracking strategy.
% chol_maxit = maximum number of iterations for the Cholesky factorization
% beta = fixed factor, greater than 1, used for the Cholesky factorization;
% fterms = function handle taking as input arguments k and gradfk, and returning the forcing term etak
% pcg_maxit = maximum number of iterations for the pcg solver
% h = step size for the finite difference approximation of the gradient and Hessian.
%
% OUTPUTS
%
for i=[3, 4, 5]
    % Dimension of the problem
    n=10^i;
    % Initialization of the starting point
    x0 = initializer(n);

    % Run the optimization algorithm for 11 different starting points
    for j=0:10
        if j == 0
            x0_j = x0;
        else
            x0_j = 2 * rand(n, 1) + x0 - 1;
        end
        disp([9, '* STARTING POINT: (dim:1e', num2str(i), ', test point #', num2str(j), ')'])
        disp([9, 9, '- EXACT GRADIENT AND HESSIAN ****'])
        % Exact gradient and Hessian
        run_optimization(x0_j, f, gradf, Hessf, beta, kmax, tolgrad, c1, rho, btmax, chol_maxit, fterms, pcg_maxit);

        % Finite difference gradient and Hessian for different values of h
        for k=2:2:12
            h = 10^(-k);

            % Absolute
            disp([9, 9, '- ABSOLUTE FINITE DIFFERENCE GRADIENT AND HESSIAN - h=', num2str(h), ' ****'])
            findiff_gradf = @(x) findiff_grad(f, x, h, 'fw', false);
            run_optimization(x0_j, f, findiff_gradf, @(x) findiff_banded(findiff_gradf, x, h, codiags, false), beta, kmax, tolgrad, c1, rho, btmax, chol_maxit, fterms, pcg_maxit);

            % Relative
            findiff_gradf = @(x) findiff_grad(f, x, h, 'fw', true);
            disp([9, 9, '- RELATIVE FINITE DIFFERENCE GRADIENT AND HESSIAN - h=', num2str(h), ' ****'])
            run_optimization(x0_j, f, findiff_gradf, @(x) findiff_banded(findiff_gradf, x, h, codiags, true ), beta, kmax, tolgrad, c1, rho, btmax, chol_maxit, fterms, pcg_maxit);

        end
    end
end
end