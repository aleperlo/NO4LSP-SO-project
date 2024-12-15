function [tau, L, i] = chol_with_addition(A, beta, coeffient, max_iter)

if min(diag(A)) > 0
    tau = 0;
else
    tau = -min(diag(A)) + beta;
end

sizes = size(A);
n = sizes(1);

for i = 1:max_iter
    try L = chol(A + tau*eye(n));
        % if i > 1
        %     disp(['Choosing tau', num2str(tau)])
        % end
        return
    catch
        tau = max(coeffient*tau, beta);
    end
end

end
