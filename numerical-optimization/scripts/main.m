%% LOADING THE VARIABLES FOR THE TEST

clear
close all
clc

load('data/test_functions2.mat');

beta = 10^-3;
max_chol_iter = 10^3;
x0 = [1.2; 1.2];

%% RUN THE STEEPEST DESCENT

disp('**** STEEPEST DESCENT (BACKTRACK + FLAG): START *****')

[xk, fk, gradfk_norm, k, xseq, btseq] = ...
    modified_newton(x0, f2, gradf2, Hessf2, beta,...
    kmax, tolgrad, c1, rho, btmax, max_chol_iter);
disp('**** MODIFIED NEWTON DESCENT: FINISHED *****')
disp('**** MODIFIED NEWTON: RESULTS *****')
disp('************************************')
disp(['xk: ', mat2str(xk), ' (actual minimum: [0; 0]);'])
disp(['f(xk): ', num2str(fk), ' (actual min. value: 0);'])
disp('************************************')


%% PLOTS (BACKTRACK)

f_meshgrid = @(X,Y)reshape(f2([X(:),Y(:)]'),size(X));

% Creation of the meshgrid for the contour-plot
[X, Y] = meshgrid(linspace(-6, 6, 500), linspace(-6, 6, 500));
% Computation of the values of f for each point of the mesh
Z = f_meshgrid(X, Y);

% Plots

% Simple Plot
fig1 = figure();
% Contour plot with curve levels for each point in xseq
[C1, ~] = contour(X, Y, Z);
hold on
% plot of the points in xseq
plot(xseq(1, :), xseq(2, :), '--*')
hold off

% More interesting Plot
fig2 = figure();
% Contour plot with curve levels for each point in xseq
% ATTENTION: actually, the mesh [X, Y] is too coarse for plotting the last
% level curves corresponding to the last point in xseq (check it zooming
% the image).
[C2, ~] = contour(X, Y, Z, f2(xseq));
hold on
% plot of the points in xseq
plot(xseq(1, :), xseq(2, :), '--*')
hold off

% Barplot of btseq
fig3 = figure();
bar(btseq)

% Much more interesting plot
fig4 = figure();
surf(X, Y, Z,'EdgeColor','none')
hold on
plot3(xseq(1, :), xseq(2, :), f2(xseq), 'r--*')
hold off



