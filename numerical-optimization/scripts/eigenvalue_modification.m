function [tau] = eigenvalue_modification(Hessfk)
    delta = sqrt(eps);
    smallest_eigenvalue = eigs(Hessfk, 1, 'smallestreal');
    tau = max([0, delta - smallest_eigenvalue]);
    if tau > 0
        disp(['Eigenvalue modification: ', num2str(tau)])
    end
end