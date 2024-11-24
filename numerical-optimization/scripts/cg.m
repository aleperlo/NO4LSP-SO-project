function [xk, k, relres] = ...
    cg(A, b, kmax, tol)
% function [xk, k, relres] = ...
%     lab01_cg_linsys(A, b, x0, kmax, tol)
%
% Conjugate Gradient Method for linear systems.
%
% INPUTS:
% A : n-by-n symmetric, positive (semi-)definite matrix of the system
% b : column vector of n elements, known terms of the system
% x0 : columns vector of n elements, starting guess
% kmax : positive integer, maximum number of steps
% tol : positive real value, tolerance for relative residual

xk = zeros(size(b));
rk = b - A * xk;
pk = rk;

k = 0;

norm_b = norm(b);
relres = norm(rk) / norm_b;

while k < kmax && relres > tol
    zk = A * pk;
    if pk' * zk <= 0
        if k == 0
            xk = zk + pk;
        end
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