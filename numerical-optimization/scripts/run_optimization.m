function [] = run_optimization(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, fterms, pcg_maxit)

disp('  MODIFIED NEWTON *****')
[~, fk, gradfk_norm, k, ~, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, false);
disp(['  f(xk): ', num2str(fk)])
disp(['  gradfk_norm: ', num2str(gradfk_norm)])
disp(['  k: ', num2str(k)])
disp('  ********************************')

disp('  TRUNCATED NEWTON')
[~, fk, gradfk_norm, k, ~, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, ...
    kmax, tolgrad, c1, rho, btmax, fterms, pcg_maxit, false);
disp(['  f(xk): ', num2str(fk)])
disp(['  gradfk_norm: ', num2str(gradfk_norm)])
disp(['  k: ', num2str(k)])
disp('  ********************************')
end

