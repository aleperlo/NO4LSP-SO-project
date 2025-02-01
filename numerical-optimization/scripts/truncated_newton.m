function [xk, fk, gradfk_norm, k, xseq, btseq, pcgiterseq] = ...
    truncated_newton(x0, f, gradf, Hessf, ...
    kmax, tolgrad, c1, rho, btmax, fterms, pcg_maxit, logging)
%
% Function that performs the Inexact Newton optimization method, using
% backtracking strategy for the step-length selection.
%
% INPUTS:
% x0 = n-dimensional column vector;
% f = function handle that describes a function R^n->R;
% gradf = function handle that describes the gradient of f;
% Hessf = function handle that describes the Hessian of f;
% kmax = maximum number of iterations permitted;
% tolgrad = value used as stopping criterion w.r.t. the norm of the
% gradient;
% c1 = the factor of the Armijo condition that must be a scalar in (0,1);
% rho = fixed factor, lesser than 1, used for reducing alpha0;
% btmax = maximum number of steps for updating alpha during the
% backtracking strategy.
% fterms = function handle taking as input arguments k and gradfk, and returning the forcing term etak
% pcg_maxit = maximum number of iterations for the pcg solver
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
% pcgiterseq = 1-by-k vector where elements are the number of pcg
% iterations at each optimization step.
%
n = length(x0);
% Function handle for the armijo condition
farmijo = @(fk, alpha, c1_gradfk_pk) ...
    fk + alpha * c1_gradfk_pk;

% Initializations
if logging
    xseq = zeros(length(x0), kmax);
    btseq = zeros(1, kmax);
    pcgiterseq = zeros(1, kmax);
else
    xseq = [];
    btseq = [];
    pcgiterseq = [];
end

xk = x0;
fk = f(xk);
gradfk = gradf(xk);
k = 0;
gradfk_norm = norm(gradfk);

while k < kmax && gradfk_norm >= tolgrad
    % "INEXACTLY" compute the descent direction as approximated solution of
    % Hessf(xk) p = - graf(xk)

    % TOLERANCE VARYING W.R.T. FORCING TERMS:
    etak = fterms(k, gradfk);
    % ATTENTION! We will use directly eta_k as tolerance in the pcg because
    % this function looks at the RELATIVE RESIDUAL and not the RESIDUAL!

    %%%%%% L.S. SOLVED WITH pcg %%%%%%%%%%%%%%%%%%%%%%%%%%%
    % For simplicity: default values for tol and maxit; no preconditioning
    % pk = pcg(Hessf(xk), -gradfk, etak, pcg_maxit);
    % If you want to silence the messages about solution "quality" use
    % instead:
    % [pk, flagk, relresk, iterk, resveck] = pcg(Hessf(xk), ...
    % -gradfk, etak, pcg_maxit);
    % [pk, ~, iterk] = cg(Hessf(xk), -gradfk, pcg_maxit, etak);
    Hk = Hessf(xk);
    try
        L = ichol(Hk);
        [pk, ~, iterk] = cg_preconditioned(Hk, -gradfk, pcg_maxit, etak, L);
    catch
        % If the preconditioner fails, we will use the default one
        [pk, ~, iterk] = cg(Hk, -gradfk, pcg_maxit, etak);
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % Reset the value of alpha
    alpha = 1;

    % Compute the candidate new xk
    xnew = xk + alpha * pk;
    % Compute the value of f in the candidate new xk
    fnew = f(xnew);
    fnew_min = fnew;
    alpha_min = alpha;

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
        % If fnew is the smallest value found so far, store it along with alpha
        if fnew < fnew_min
            fnew_min = fnew;
            alpha_min = alpha;
        end

        % Increase the counter by one
        bt = bt + 1;
    end
    if bt == btmax && fnew > farmijo(fk, alpha, c1_gradfk_pk)
        %disp('Armijo condition could not be satisfied!')
        alpha = alpha_min;
        fnew = fnew_min;
        xnew = xk + alpha * pk;
    end

    % Update xk, fk, gradfk_norm
    xk = xnew;
    fk = fnew;
    gradfk = gradf(xk);
    gradfk_norm = norm(gradfk);

    % Increase the step by one
    k = k + 1;

    if logging
        % Store current xk in xseq
        xseq(:, k) = xk;
        % Store bt iterations in btseq
        btseq(k) = bt;
        pcgiterseq(k) = iterk;
    end
end

if logging
    % "Cut" xseq and btseq to the correct size
    xseq = xseq(:, 1:k);
    btseq = btseq(1:k);
    pcgiterseq = pcgiterseq(1:k);
    % "Add" x0 at the beginning of xseq (otherwise the first el. is x1)
    xseq = [x0, xseq];
end

end