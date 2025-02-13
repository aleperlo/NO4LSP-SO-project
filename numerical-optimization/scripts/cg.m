function [xk, k, relres, truncated] = ...
    cg(A, b, kmax, tol)
% CG Conjugate Gradient method
% Input:
%   A: matrix
%   b: right-hand side vector
%   kmax: maximum number of iterations
%   tol: tolerance
% Output:
%   xk: approximate solution
%   k: number of iterations
%   relres: relative residual
%   truncated: 1 if the method is truncated, 0 otherwise

% Initializations
xk = zeros(size(b));
rk = b - A * xk;
pk = rk;

truncated = 0;
k = 0;

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
    alphak = (rk' * pk) / (pk' * zk);
    xk = xk + alphak * pk;
    rk = rk - alphak * zk;

    betak = -(rk' * zk) / (pk' * zk);
    pk = rk + betak * pk;

    relres = norm(rk) / norm_b;
    k = k + 1;
end

end