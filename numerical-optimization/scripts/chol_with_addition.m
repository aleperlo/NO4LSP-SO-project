function [B, tau] = chol_with_addition(A, beta, coeffient, max_iter)
% CHOL_WITH_ADDITION Compute the Cholesky factorization of a matrix with an
% additional term, which is a multiple of the identity.
% Input:
% A: a symmetric matrix
% beta: a positive scalar
% coeffient: a scalar that is greater than 1
% max_iter: a positive integer
% Output:
% B: the modification necessary to make the A positive definite
% tau: a scalar
mindiag = min(diag(A));
if mindiag > 0
    tau = 0;
else
    tau = -mindiag + beta;
end

sizes = size(A);
n = sizes(1);

for i = 1:max_iter
    try chol(A + tau*speye(n));
        if i > 1
        end
        break
    catch
        tau = max(coeffient*tau, beta);
    end
end
if i >= max_iter
    tau = 0;
    disp('Tau could not be found!')
end

B = speye(n) * tau;

end
