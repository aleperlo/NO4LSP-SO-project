function [xk, k, relres, truncated] = ...
    cg_preconditioned(A, b, kmax, tol, L)
% CG_PRECONDITIONED Preconditioned Conjugate Gradient method
% Input:
%   A: matrix
%   b: right-hand side vector
%   kmax: maximum number of iterations
%   tol: tolerance
%   L: Cholesky factor of the preconditioner
% Output:
%   xk: approximate solution
%   k: number of iterations
%   relres: relative residual
%   truncated: 1 if the method is truncated, 0 otherwise

% Initializations
xk = zeros(size(b));
rk = A * xk - b;
wk = L \ rk;
yk = L' \ wk;
pk = -yk;

k = 0;
truncated = 0;

norm_b = norm(b);
relres = norm(rk) / norm_b;

while k < kmax && relres > tol
    zk = A * pk;
    % If negative curvature, truncate
    if pk' * zk <= 0
        % If the first iteration, return -grad(f)
        if k == 0
            xk = b;
        end
        truncated = 1;
        return
    end
    alphak = (rk' * yk) / (pk' * zk);
    xk = xk + alphak * pk;
    rk_new = rk + alphak * zk;

    wk = L \ rk_new;
    yk_new = L' \ wk;

    betak = (rk_new' * yk_new) / (rk' * yk);
    pk = -yk_new + betak * pk;

    rk = rk_new;
    yk = yk_new;

    relres = norm(rk) / norm_b;
    k = k + 1;
end

end