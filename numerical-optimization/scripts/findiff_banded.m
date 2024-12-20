function [JF] = findiff_banded(F, x, h, codiags)
    % k is the number of codiagonals per side
    n = length(x);
    step = 2*codiags + 1;
    Bin = zeros(n, step);
    Fx = F(x);
    
    for offset = 1:step
        % Allocate perturbation vector
        perturbation = zeros(n, 1);
        for j = 1:step:n
            if j+offset-1 <= n
                % Add component j+i-1 to perturbation vector
                perturbation(j+offset-1) = h;
            end
        end
        Fx_p = F(x + perturbation);
        temp = (Fx_p - Fx) / h;
        for col = offset:step:n
            for row = col-codiags:col+codiags
                if row <= n && row > 0
                    Bin(row, row-col+codiags+1) = temp(row);
                end
            end
        end
    end

    JF = spdiags(Bin, -codiags:codiags, n, n);
    JF = (JF + JF')/2;
end