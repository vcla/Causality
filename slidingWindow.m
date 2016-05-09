function results = slidingWindow(startFrame, endFrame, individualFrames, logSpace, allowOverlaps, windowSize, absoluteMaxWindowSize)
%allowOverlaps = true allows competing solutions; false performs surround suppression
%windowSize = 50; % starting window size
%absoluteMaxWindowSize = false; % don't allow windows larger than this; false ignores this

thresh = 0.000001; % added onto 1/7 for threshold for overlap case
nonOverlapThresh = .7; %only used if ~allowOverlaps

vectorOfFrames = arrayfun(@(foo) foo.frame_ind, individualFrames);

results = [0;0;0;0];
    % start, end, action, prob
    
maxFrameWidth = windowSize*floor((endFrame - startFrame)/windowSize);
if absoluteMaxWindowSize 
    maxFrameWidth = min(absoluteMaxWindowSize, maxFrameWidth); 
end

%for frameWidth = 5:5:40
            % TODO: if there was overlap, then it deleted the lower
            % probability one.  and then the next one might overlap the
            % 2nd (with higher probability), but not the first.  so should
            % have kept the first.  does running the window size in reverse
            % order fix that?  maybe so...  do it, run diff/compare
            % results.  
for frameWidth = windowSize:windowSize:maxFrameWidth %FOR SLIDING WINDOW
%for frameWidth = maxFrameWidth:-windowSize:windowSize %FOR REVERSE SLIDING WINDOW
    disp(frameWidth); %CHANGED THIS
    for tryingWindowStart = startFrame:(endFrame-frameWidth+1)
        % gather the frames
        tryingWindowEnd = tryingWindowStart+frameWidth-1;
        frameInds = tryingWindowStart:tryingWindowEnd;
        indicesOfArray = arrayfun(@(foo) ismember(foo,frameInds), vectorOfFrames);
        
        % calculate the probability (multiply) and renormalize
        if any(indicesOfArray) > 0
            if ~logSpace
                probs = arrayfun(@(foo) foo.act_prob, individualFrames(indicesOfArray));
                prob = 1;
                for probIndex = 1:numel(probs)
                    %disp(probs(probIndex).prob)
                    prob = prob .* probs(probIndex).prob;
                    %disp('---')
                end
                prob = prob/sum(prob);

                [maxprob action] = max(prob);
            else
                %convert to logs
                probs = arrayfun(@(foo) foo.act_prob, individualFrames(indicesOfArray));
                prob = 0;
                for probIndex = 1:numel(probs)
                    %disp(probs(probIndex).prob)
                    prob = prob + log(probs(probIndex).prob);
                    %disp('---')
                end
                %prob = prob/sum(prob);

                [maxprob action] = max(prob);
                maxprob = exp(maxprob)/sum(exp(prob));
            end

            overLap1 = tryingWindowStart >= results(1,:) & tryingWindowEnd <= results(2,:);
            overLap2 = tryingWindowStart >= results(1,:) & tryingWindowStart <= results(2,:);
            overLap3 = tryingWindowEnd >= results(1,:) & tryingWindowEnd <= results(2,:);
            overLap4 = tryingWindowStart <= results(1,:) & tryingWindowEnd >= results(2,:);
            noOverLap = tryingWindowEnd < results(1,:) | tryingWindowStart > results(2,:);
            overlaps = overLap1 | overLap2 | overLap3 | overLap4;
            if any(noOverLap ~= (~overlaps))
                error('problem with my logic')
            end
            if ~allowOverlaps
                addResult = false;
                deleteResult = false;
                if all(noOverLap)
                    % if doesn't overlap, and has "high enough" probability, keep it
                    addResult = true;
                else % there is an overlap
                    % if has higher probability than something in our stored results
                    % and overlaps, keep it and ditch the other (surround suppression)
                    if maxprob > results(4,overlaps)
                        % find where that happens
                        entriesToDelete = (maxprob > results(4,:)) & overlaps;
                        deleteResult = true;
                        addResult = true;
                    end

                    % if it has equal probability and overlaps, keep both
                    %if maxprob - results(4,overlaps) > thresh % then maxprob bigger
                    if maxprob == results(4,overlaps)
                        entriesToDelete = (maxprob == results(4,:)) & overlaps;
                        deleteResult = true;

                        addResult = true;
                    end

                    % if overlap is equality, pass
                    if tryingWindowStart == results(1,:) & tryingWindowEnd == results(2,:)
                        addResult = false;
                        asdf3
                    end

                end

                if deleteResult
                    %results
                    results(:,entriesToDelete) = [];   %CHANGED THIS
                    %results
                    %asdf1
                end
                
                if addResult && (maxprob > 1/7 + thresh)
                    results = [results [tryingWindowStart tryingWindowEnd action maxprob]'];
                    %disp(results);  
                end

                
            else
                if (maxprob > nonOverlapThresh)   
                    results = [results [tryingWindowStart tryingWindowEnd action maxprob]'];
                    %disp(results);  
                end
            end
            
            
            % TODO: clean up results (only keep top N performers)
            % either keep this in the loop, or move it to the end (probably
            % move to the end)
        
        end
         
        
    end
end

% drop initializing 0 from results
results(:,1) = [];