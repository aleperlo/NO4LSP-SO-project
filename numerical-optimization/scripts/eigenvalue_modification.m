function [B] = eigenvalue_modification(Hessfk)
    delta = sqrt(eps);
    smallest_eigenvalue = eigs(Hessfk, 1, 'smallestreal');
    tau = max([0, delta - smallest_eigenvalue]);
    B = speye(size(Hessfk)) * tau;
end