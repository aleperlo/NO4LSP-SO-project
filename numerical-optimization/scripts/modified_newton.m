function [xk, fk, gradfk_norm, k, xseq, btseq] = ...
    modified_newton(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, max_chol_iter)
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
xseq = zeros(length(x0), kmax);
btseq = zeros(1, kmax);

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
    % [pk, flagk, relresk, iterk, resveck] = pcg(Hessf(xk), -gradfk);
    [tau, ~, ~] = chol_with_addition(Hessfk, beta, 2, max_chol_iter);
    [pk, ~, ~, ~, ~] = pcg(Hessfk + tau*eye(n), -gradfk);
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
        break
    end

    % Update xk, fk, gradfk_norm
    xk = xnew;
    fk = fnew;
    gradfk = gradf(xk);
    gradfk_norm = norm(gradfk);
    Hessfk = Hessf(xk);

    % Increase the step by one
    k = k + 1;

    % Store current xk in xseq
    xseq(:, k) = xk;
    % Store bt iterations in btseq
    btseq(k) = bt;
end

% "Cut" xseq and btseq to the correct size
xseq = xseq(:, 1:k);
btseq = btseq(1:k);
% "Add" x0 at the beginning of xseq (otherwise the first el. is x1)
xseq = [x0, xseq];

end