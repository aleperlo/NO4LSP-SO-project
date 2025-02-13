function [xk, fk, gradfk_norm, k, T, success, xseq] = ...
    modified_newton(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, max_chol_iter, preconditioning, logging, modification_coeff)
% MODIFIED_NEWTON: Newton method with backtracking line search and Hessian modification
% INPUTS
% x0: initial point
% f: function handle for the objective function
% gradf: function handle for the gradient of the objective function
% Hessf: function handle for the Hessian of the objective function
% beta: parameter for the Hessian modification
% kmax: maximum number of iterations
% tolgrad: tolerance for the norm of the gradient
% c1: parameter for the Armijo condition
% rho: parameter for the backtracking strategy
% btmax: maximum number of backtracking steps
% max_chol_iter: maximum number of attempts for Hessian modification
% preconditioning: flag for preconditioning
% logging: flag for logging the sequence of iterates
% modification_coeff: parameter for the Hessian modification
% OUTPUTS
% xk: optimal point
% fk: optimal value of the objective function
% gradfk_norm: norm of the gradient at the optimal point
% k: number of iterations
% T: table with the sequence of iterates
% success: flag for successful convergence
% xseq: sequence of iterates

% Default values
if nargin < 14
    modification_coeff = 2;
end

n = length(x0);
% Function handle for the armijo condition
farmijo = @(fk, alpha, c1_gradfk_pk) ...
    fk + alpha * c1_gradfk_pk;

% Initializations
if logging
    xseq = zeros(n, kmax);
else
    xseq = [];
end
success = 1;

gradfkseq = zeros(1, kmax);
fkseq = zeros(1, kmax);
btseq = zeros(1, kmax);
pcgiterseq = zeros(1, kmax);
correctionseq = zeros(1, kmax);
errornormseq = zeros(1, kmax);

xk = x0;
fk = f(xk);
gradfk = gradf(xk);
k = 0;
gradfk_norm = norm(gradfk);

Hessfk = Hessf(xk);

while k < kmax && gradfk_norm >= tolgrad
    % Compute the Hessian modification
    [B, tau] = chol_with_addition(Hessfk, beta, modification_coeff, max_chol_iter);
    Hkm = Hessfk + B;
    % Compute the descent direction as solution of
    % Hessf(xk) p = - gradf(xk)
    if preconditioning
        try
            L = ichol(Hkm);
            [pk, ~, ~, iterk, ~] = pcg(Hkm, -gradfk, 1e-6, 1000, L, L');
        catch
            [pk, ~, ~, iterk, ~] = pcg(Hkm, -gradfk);
        end
    else
        [pk, ~, ~, iterk, ~] = pcg(Hkm, -gradfk);
    end

    % Reset the value of alpha
    alpha = 1;

    % Compute the candidate new xk
    xnew = xk + alpha * pk;
    % Compute the value of f in the candidate new xk
    fnew = f(xnew);

    c1_gradfk_pk = c1 * gradfk' * pk;
    bt = 0;
    % Backtracking strategy
    while bt < btmax && fnew > farmijo(fk, alpha, c1_gradfk_pk)
        % Reduce the value of alpha
        alpha = rho * alpha;
        % Update xnew and fnew w.r.t. the reduced alpha
        xnew = xk + alpha * pk;
        fnew = f(xnew);

        % Increase the counter by one
        bt = bt + 1;
    end

    % Check if the Armijo condition could not be satisfied
    if bt == btmax && fnew > farmijo(fk, alpha, c1_gradfk_pk)
        disp("Armijo condition could not be satisfied!")
        success = 0;
        break
    end

    % Compute the error norm
    errornormseq(k+1) = norm(xnew - xk);
    % Update xk, fk, gradfk_norm
    xk = xnew;
    fk = fnew;
    gradfk = gradf(xk);
    gradfk_norm = norm(gradfk);
    Hessfk = Hessf(xk);

    % Increase the step by one
    k = k + 1;

    % Log iteration data
    if logging
        xseq(:, k) = xk;
    end
    gradfkseq(k) = gradfk_norm;
    fkseq(k) = fk;
    btseq(k) = bt;
    pcgiterseq(k) = iterk;
    correctionseq(k) = tau;
end

% Truncate the sequences
gradfkseq = gradfkseq(1:k);
fkseq = fkseq(1:k);
btseq = btseq(1:k);
pcgiterseq = pcgiterseq(1:k);
correctionseq = correctionseq(1:k);
errornormseq = errornormseq(1:k);
T = table(gradfkseq', fkseq', btseq', pcgiterseq', correctionseq', errornormseq', ...
    'VariableNames', {'gradient_norm', 'function_value', 'backtrack', 'inner_iterations', 'correction', 'error_norm'});
if logging
    xseq = xseq(:, 1:k);
end
% Check if the algorithm did not converge within the maximum number of iterations
if k >= kmax && gradfk_norm >= tolgrad
    success = 0;
end

end