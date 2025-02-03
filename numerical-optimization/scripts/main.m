clear all; close all; clc; %#ok<CLALL>

load('data/test_functions2.mat');
load('data/forcing_terms.mat');

% Seed for reproducibility
seed = min([331794 337131 338682]);

% //TODO rosenbrock

fterms = {@(k, gradf) fterms_suplin(k, gradf), @(k, gradf) fterms_quad(k, gradf)};

for i = 1:length(fterms)

    fterm = fterms{i};

    rng(seed);
    disp('**** CHAINED ROSENBROCK *****')
    codiags = 1;
    test(@(x) chained_rosenbrock(x), @(x) chained_rosenbrock_gradf(x),...
        @(x)chained_rosenbrock_Hessf(x), @(n) chained_rosenbrock_initializer(n), codiags,...
        5e4, 1e-6, 1e-4, 0.8, 100, 1000, 1e-3, fterm, 100, '../results/chained_rosenbrock/');

    % rng(seed);
    % disp('**** GENERALIZED BROYDEN *****')
    % codiags = 2;
    % test(@(x) generalized_broyden(x), @(x) generalized_broyden_gradf(x),...
    %     @(x)generalized_broyden_Hessf(x), @(n) generalized_broyden_initializer(n), codiags,...
    %     5000, 1e-6, 1e-4, 0.8, 100, 1000, 1e-3, fterm, 100);


    % rng(seed);
    % disp('**** BANDED TRIGONOMETRIC *****')
    % codiags = 0;
    % test(@(x) banded_trigonometric(x), @(x) banded_trigonometric_gradf(x),...
    %     @(x)banded_trigonometric_Hessf(x), @(n) banded_trigonometric_initializer(n), codiags,...
    %     5000, 1e-6, 1e-4, 0.8, 100, 1000, 1e-3, fterm, 100);

end
