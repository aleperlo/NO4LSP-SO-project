function [xk, fk, gradfk_norm, k, T, xseq] = ...
    modified_newton(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, max_chol_iter, preconditioning, logging)
%
%
% INPUTS:
% x0 = n-dimensional column vector;
% f = function handle that describes a function R^n->R;
% gradf = function handle that describes the gradient of f;
% Hessf = function handle that describes the Hessian of f;
% kmax = maximum number of iterations permitted;
% tolgrad = value used as stopping criterion w.r.t. the norm of the gradient;
% c1 = the factor of the Armijo condition that must be a scalar in (0,1);
% rho = fixed factor, lesser than 1, used for reducing alpha0;
% btmax = maximum number of steps for updating alpha during the backtracking strategy.
%
% OUTPUTS:
% xk = the last x computed by the function;
% fk = the value f(xk);
% gradfk_norm = value of the norm of gradf(xk)
% k = index of the last iteration performed
% xseq = n-by-k matrix where the columns are the elements xk of the
% sequence
% btseq = 1-by-k vector where elements are the number of backtracking
% iterations at each optimization step.
%

% Function handle for the armijo condition
farmijo = @(fk, alpha, c1_gradfk_pk) ...
    fk + alpha * c1_gradfk_pk;

% Initializations
if logging
    xseq = zeros(length(x0), kmax);
else
    xseq = [];
end

gradfkseq = zeros(1, kmax);
fkseq = zeros(1, kmax);
btseq = zeros(1, kmax);
pcgiterseq = zeros(1, kmax);
correctionseq = zeros(1, kmax);

xk = x0;
fk = f(xk);
gradfk = gradf(xk);
k = 0;
gradfk_norm = norm(gradfk);

Hessfk = Hessf(xk);
sizes = size(Hessfk);
n = sizes(1);

while k < kmax && gradfk_norm >= tolgrad
    % Compute the descent direction as solution of
    % Hessf(xk) p = - gradf(xk)
    %%%%%% L.S. SOLVED WITH BACKSLASH (NOT USED) %%%%%%%%%%
    % pk = -Hessf(xk)\gradfk;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%% L.S. SOLVED WITH pcg %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % For simplicity: default values for tol and maxit; no preconditioning
    % pk = pcg(Hessf(xk), -gradfk);
    % If you want to silence the messages about "solution quality", use
    % instead:
    [B, tau] = chol_with_addition(Hessfk, beta, 5, max_chol_iter);
    % B = eigenvalue_modification(Hessfk);
    % B = modchol_ldlt(Hessfk);
    % TODO Warning: Input tol may not be achievable by PCG - Try to use a bigger tolerance
    Hkm = Hessfk + B;
    if preconditioning
        L = ichol(Hkm);
        [pk, ~, ~, iterk, ~] = pcg(Hkm, -gradfk, 1e-6, 1000, L, L');
    else
        [pk, ~, ~, iterk, ~] = pcg(Hkm, -gradfk);
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % Reset the value of alpha
    alpha = 1;

    % Compute the candidate new xk
    xnew = xk + alpha * pk;
    % Compute the value of f in the candidate new xk
    fnew = f(xnew);

    c1_gradfk_pk = c1 * gradfk' * pk;
    bt = 0;
    % Backtracking strategy:
    % 2nd condition is the Armijo condition not satisfied
    while bt < btmax && fnew > farmijo(fk, alpha, c1_gradfk_pk)
        % Reduce the value of alpha
        alpha = rho * alpha;
        % Update xnew and fnew w.r.t. the reduced alpha
        xnew = xk + alpha * pk;
        fnew = f(xnew);

        % Increase the counter by one
        bt = bt + 1;
    end
    if bt == btmax && fnew > farmijo(fk, alpha, c1_gradfk_pk)
        disp("Armijo condition could not be satisfied!")
        return
    end

    % Update xk, fk, gradfk_norm
    xk = xnew;
    fk = fnew;
    gradfk = gradf(xk);
    gradfk_norm = norm(gradfk);
    Hessfk = Hessf(xk);

    % Increase the step by one
    k = k + 1;

    if logging
        xseq(:, k) = xk;
    end
    gradfkseq(k) = gradfk_norm;
    fkseq(k) = fk;
    btseq(k) = bt;
    pcgiterseq(k) = iterk;
    correctionseq(k) = tau;
end

gradfkseq = gradfkseq(1:k);
fkseq = fkseq(1:k);
btseq = btseq(1:k);
pcgiterseq = pcgiterseq(1:k);
correctionseq = correctionseq(1:k);
T = table(gradfkseq', fkseq', btseq', pcgiterseq', correctionseq', ...
    'VariableNames', {'gradient_norm', 'function_value', 'backtrack', 'inner_iterations', 'correction'});
if logging
    xseq = xseq(:, 1:k);
end

end