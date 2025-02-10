clear all; close all; clc; %#ok<CLALL>

load('data/test_functions2.mat');
load('data/forcing_terms.mat');

% Seed for reproducibility
seed = min([331794 337131 338682]);

% //TODO rosenbrock

fterm = @(k, gradf) fterms_suplin(k, gradf);
kmax = dictionary([3, 4, 5], [1e3, 1e3, 1e3]);
modified_coeffs = [5, 2, 2];

rng(seed);
disp('**** CHAINED ROSENBROCK *****')
codiags = 1;
test(@(x) extended_rosenbrock(x), @(x) extended_rosenbrock_gradf(x),...
    @(x)extended_rosenbrock_Hessf(x), @(n) extended_rosenbrock_initializer(n),...
    @extended_rosenbrock_gradf_fd1, @extended_rosenbrock_Hessf_fd1, codiags,...
    kmax, 1e-6, 1e-4, 0.5, 50, 100, 1e-3, fterm, 100, '../results/extended_rosenbrock/', true, 5);

rng(seed);
disp('**** GENERALIZED BROYDEN *****')
codiags = 2;
test(@(x) generalized_broyden(x), @(x) generalized_broyden_gradf(x),...
    @(x)generalized_broyden_Hessf(x), @(n) generalized_broyden_initializer(n),...
    @generalized_broyden_gradf_fd1, @generalized_broyden_Hessf_fd1, codiags,...
    kmax, 1e-6, 1e-4, 0.5, 50, 100, 1e-3, fterm, 100, '../results/generalized_broyden/', true, 2);

rng(seed);
disp('**** BANDED TRIGONOMETRIC *****')
codiags = 0;
test(@(x) banded_trigonometric(x), @(x) banded_trigonometric_gradf(x),...
    @(x)banded_trigonometric_Hessf(x), @(n) banded_trigonometric_initializer(n),...
    @banded_trigonometric_gradf_fd1, @banded_trigonometric_Hessf_fd1, codiags,...
    kmax, 1e-6, 1e-4, 0.5, 50, 100, 1e-3, fterm, 100, '../results/banded_trigonometric/', true, 5);