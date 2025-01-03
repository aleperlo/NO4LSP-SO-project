clear all; close all; clc;

load('data/test_functions2.mat');
load('data/forcing_terms.mat');

% Seed for reproducibility
seed = min([331794 337131 338682]);
rng(seed);


disp('**** CHAINED ROSENBROCK *****')
test(@(x) chained_rosenbrock(x), @(x) chained_rosenbrock_gradf(x),...
    @(x)chained_rosenbrock_Hessf(x), @(n) chained_rosenbrock_initializer(n),...
    5000, 1e-6, 1e-4, 0.8, 100, 1000, 1e-3, fterms_suplin, 100);

% disp('**** DISCRETE BOUNDARY *****')
% test(@(x) discrete_boundary(x), @(x) discrete_boundary_gradf(x),...
%     @(x)discrete_boundary_Hessf(x), @(n) chained_rosenbrock_initializer(n),...
%     5000, 1e-6, 1e-4, 0.8, 100, 1000, 1e-3, fterms_quad, 100);
