function [B, tau] = chol_with_addition(A, beta, coeffient, max_iter)

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
if i == max_iter
    tau = 0;
    disp('Tau could not be found!')
end

B = speye(n) * tau;

end
