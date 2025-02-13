function f = rosenbrock(x)
f = 100*(x(2) - x(1)^2)^2 + (1 - x(1))^2;
end

function g = rosenbrock_gradient(x)
g = [-400*x(1)*(x(2) - x(1)^2) - 2*(1 - x(1));
    200*(x(2) - x(1)^2)];
end

function H = rosenbrock_hessian(x)
H = [1200*x(1)^2 - 400*x(2) + 2, -400*x(1);
    -400*x(1), 200];
end

x0_0 = [1.2; 1.2];
x0_1 = [-1.2; 1];
starting_points = {x0_0, x0_1};

kmax = 1e3;
tol = 1e-6;
% Backtracking parameters
rho = 0.5;
c1 = 1e-4;
btmax = 50;
% Modified Newton parameters
beta = 1e-3;
c = 2;
% Truncated Newton parameters
fterm_suplin = @(k, gradfk) min(0.5, sqrt(norm(gradfk)));

% Define the Rosenbrock function
rosenbrockFunction = @(x, y) (1 - x).^2 + 100 * (y - x.^2).^2;

% Create a grid of X and Y values
x = linspace(-1.5, 1.5, 100);
y = linspace(-0.5, 2.5, 100);
[X, Y] = meshgrid(x, y);
Z = rosenbrockFunction(X, Y);

% Run the optimization algorithms
for i = 1:length(starting_points)
    % Set figure properties for readability in a paper
    set(groot, 'defaultAxesFontSize', 30);
    set(groot, 'defaultTextInterpreter', 'latex');
    set(groot, 'defaultLegendInterpreter', 'latex');
    set(groot, 'defaultColorbarTickLabelInterpreter', 'latex');
    set(groot, 'defaultAxesTickLabelInterpreter', 'latex');
    % Plot the Rosenbrock function contour
    figure;
    contourLevels = logspace(-0.5, 3.5, 20); % Logarithmically spaced contour levels
    contour(X, Y, Z, contourLevels);
    xlabel('$x_1$', 'Interpreter', 'latex');
    ylabel('$x_2$', 'Interpreter', 'latex');
    colorbar;
    % Starting point
    x0 = starting_points{i};
    disp(' ');
    disp(['Starting point: ', mat2str(x0)]);
    tic;
    [xk, fk, gradfk_norm, k, ~, success, xseq] = modified_newton( ...
        x0, @rosenbrock, @rosenbrock_gradient, @rosenbrock_hessian, ...
        beta, kmax, tol, c1, rho, btmax, 50, false, true, 2);
    time = toc;
    disp([9, 'Modified Newton: ', num2str(success), ', ', num2str(k), ', ', num2str(gradfk_norm), ', ', num2str(fk)]);
    disp([9, 'time: ', num2str(time), ' k = ', num2str(k)]);
    disp([9, 'xk = ', mat2str(xk)]);
    % Plot the descent path for Modified Newton
    hold on;
    plot(xseq(1, :), xseq(2, :), 'r*-', 'MarkerSize', 10);

    tic;
    [xk, fk, gradfk_norm, k, ~, success, xseq] = truncated_newton( ...
        x0, @rosenbrock, @rosenbrock_gradient, @rosenbrock_hessian, ...
        kmax, tol, c1, rho, btmax, fterm_suplin, 100, false, true);
    time = toc;
    disp([9, 'Truncated Newton: ', num2str(success), ', ', num2str(k), ', ', num2str(gradfk_norm), ', ', num2str(fk)]);
    disp([9, 'time: ', num2str(time), ' k = ', num2str(k)]);
    disp([9, 'xk = ', mat2str(xk)]);
    % Plot the descent path for Truncated Newton
    plot(xseq(1, :), xseq(2, :), 'b*-', 'MarkerSize', 10);
    hold off;
    legend('Rosenbrock function', 'Modified Newton', 'Truncated Newton');

    % Save the figure
    orient landscape;
    set(gca, 'LooseInset', get(gca, 'TightInset'));
    filename = ['../report/figures/rosenbrock_x0_', num2str(i)];
    saveas(gcf, filename, 'pdf');
end