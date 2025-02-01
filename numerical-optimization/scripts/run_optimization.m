function [] = run_optimization(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, fterms, pcg_maxit)

disp([9, 9, 9, 'MODIFIED NEWTON *****'])
[~, fk, gradfk_norm, k, ~, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, false);
disp([9, 9, 9, 'f(xk): ', num2str(fk)])
disp([9, 9, 9, 'gradfk_norm: ', num2str(gradfk_norm)])
disp([9, 9, 9, 'k: ', num2str(k)])
disp([9, 9, 9, '********************************'])

disp([9, 9, 9, 'TRUNCATED NEWTON'])
[~, fk, gradfk_norm, k, ~, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, ...
    kmax, tolgrad, c1, rho, btmax, fterms, pcg_maxit, false);
disp([9, 9, 9, 'f(xk): ', num2str(fk)])
disp([9, 9, 9, 'gradfk_norm: ', num2str(gradfk_norm)])
disp([9, 9, 9, 'k: ', num2str(k)])
disp([9, 9, 9, '********************************'])

end

