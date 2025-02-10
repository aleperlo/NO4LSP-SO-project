function [gradf] = generalized_broyden_gradf_fd1(x, h, relative)
    n = length(x);
    if relative
        hs = h*abs(x);
    else
        hs = h*ones(n, 1);
    end
    xm2 = [0; 0; x(1:end-2)];
    xm1 = [0; x(1:end-1)];
    xp1 = [x(2:end); 0];
    xp2 = [x(3:end); 0; 0];
    gradf = 2*xm1.^2 + 4*xm1.*x - 6*xm1 + 8*x.^3 - 18*x.^2 + 4*x.*xp1 + 8*x.*hs.^2 + 7.*x ...
        + 2*xp1.^2 - 6*xp1 - 6*hs.^2 + xm2 + xp2 + 1;
    gradf(1) =  6*x(1) - 6*x(2) + x(3)+ 4*x(1)*x(2) + 8*x(1)*hs(1)^2 ...
        - 18*x(1)^2 + 8*x(1)^3 + 2*x(2)^2 - 6*hs(1)^2 + 2;
    gradf(n) = x(n-2) - 6*x(n-1) + 6*x(n) + 4*x(n-1)*x(n) + 8*x(n)*hs(n)^2 ...
        + 2*x(n-1)^2 - 18*x(n)^2 + 8*x(n)^3 - 6*hs(n)^2 + 2;
end