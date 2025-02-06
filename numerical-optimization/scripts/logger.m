function [] = logger(root_dir, i, success, method, pre, dimension, point_number, exact, h, absolute,  fk, gradfk, k, T, time)
    % Create the directory if it does not exist
    if ~exist(root_dir, 'dir')
        mkdir(root_dir);
    end
    % Save the results
    writetable(T, [root_dir, 'experiment_', num2str(i), '.csv']);
    % Append the experiment results to the log csv file
    writematrix([i, success, method, pre, dimension, point_number, exact, h, absolute, fk, gradfk, k, time], [root_dir, 'results.csv'], 'WriteMode', 'append');
end