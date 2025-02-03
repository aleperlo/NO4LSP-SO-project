function [fk_m, gradfk_norm_m, k_m, T_m, time_m, success_m, ...
        fk_t, gradfk_norm_t, k_t, T_t, time_t, success_t] = run_optimization(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, fterms, pcg_maxit, pre)

disp([9, 9, 9, 'MODIFIED NEWTON *****'])
disp([9, 9, 9, 'PRECONDITIONING: ', num2str(pre)])
tic;
[~, fk_m, gradfk_norm_m, k_m, T_m, success_m, ~] = ...
    modified_newton(x0, f, gradf, Hessf, beta,...
    kmax, tolgrad, c1, rho, btmax, chol_maxit, pre, false);
time_m = toc;
disp([9, 9, 9, 'f(xk): ', num2str(fk_m)])
disp([9, 9, 9, 'gradfk_norm: ', num2str(gradfk_norm_m)])
disp([9, 9, 9, 'k: ', num2str(k_m)])
disp([9, 9, 9, '********************************'])

disp([9, 9, 9, 'TRUNCATED NEWTON'])
disp([9, 9, 9, 'PRECONDITIONING: ', num2str(pre)])
tic;
[~, fk_t, gradfk_norm_t, k_t, T_t, success_t, ~] = ...
    truncated_newton(x0, f, gradf, Hessf, ...
    kmax, tolgrad, c1, rho, btmax, fterms, pcg_maxit, pre, false);
time_t = toc;
disp([9, 9, 9, 'f(xk): ', num2str(fk_t)])
disp([9, 9, 9, 'gradfk_norm: ', num2str(gradfk_norm_t)])
disp([9, 9, 9, 'k: ', num2str(k_t)])
disp([9, 9, 9, '********************************'])

end

