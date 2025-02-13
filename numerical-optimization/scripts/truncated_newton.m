function [xk, fk, gradfk_norm, k, T, success, xseq] = ...
    truncated_newton(x0, f, gradf, Hessf, ...
    kmax, tolgrad, c1, rho, btmax, fterms, pcg_maxit, preconditioning, logging)
% TRUNCATED_NEWTON Truncated Newton method for unconstrained optimization
% INPUTS
% x0: initial point
% f: function handle for the objective function
% gradf: function handle for the gradient of the objective function
% Hessf: function handle for the Hessian of the objective function
% kmax: maximum number of iterations
% tolgrad: tolerance for the norm of the gradient
% c1: parameter for the Armijo condition
% rho: parameter for the backtracking strategy
% btmax: maximum number of backtracking steps
% fterms: function handle for the tolerance varying w.r.t. forcing terms
% pcg_maxit: maximum number of iterations for the pcg in the inner loop
% preconditioning: flag for preconditioning
% logging: flag for logging the sequence of iterates
% OUTPUTS
% xk: optimal point
% fk: optimal value of the objective function
% gradfk_norm: norm of the gradient at the optimal point
% k: number of iterations
% T: table with the sequence of iterates
% success: flag for successful convergence
% xseq: sequence of iterates

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
truncatedseq = zeros(1, kmax);
errornormseq = zeros(1, kmax);

xk = x0;
fk = f(xk);
gradfk = gradf(xk);
k = 0;
gradfk_norm = norm(gradfk);

while k < kmax && gradfk_norm >= tolgrad
    % Compute adaptive tolerance for the pcg
    etak = fterms(k, gradfk);
    Hk = Hessf(xk);
    % Compute the descent direction
    % Hessf(xk) p = -gradf(xk)
    if preconditioning
        try
            L = ichol(Hk);
            [pk, ~, iterk, truncated] = cg_preconditioned(Hk, -gradfk, pcg_maxit, etak, L);
        catch
            [pk, ~, iterk, truncated] = cg(Hk, -gradfk, pcg_maxit, etak);
        end
    else
        [pk, ~, iterk, truncated] = cg(Hessf(xk), -gradfk, pcg_maxit, etak);
    end

    % Reset the value of alpha
    alpha = 1;

    % Compute the candidate new xk
    xnew = xk + alpha * pk;
    % Compute the value of f in the candidate new xk
    fnew = f(xnew);

    c1_gradfk_pk = c1 * gradfk' * pk;
    bt = 0;
    % Backtracking
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
        disp('Armijo condition could not be satisfied!')
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
    truncatedseq(k) = truncated;
end

% Truncate the sequence of iterates
gradfkseq = gradfkseq(1:k);
fkseq = fkseq(1:k);
btseq = btseq(1:k);
pcgiterseq = pcgiterseq(1:k);
truncatedseq = truncatedseq(1:k);
errornormseq = errornormseq(1:k);
T = table(gradfkseq', fkseq', btseq', pcgiterseq', truncatedseq', errornormseq', ...
    'VariableNames', {'gradient_norm', 'function_value', 'backtrack', 'inner_iterations', 'truncated', 'error_norm'});
if logging
    xseq = xseq(:, 1:k);
end

% Check if the algorithm did not converge within the maximum number of iterations
if k >= kmax && gradfk_norm >= tolgrad
    success = 0;
end

end