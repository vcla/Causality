function [] = writeTemporalParses(input, exampleName, folderName)
% input row = [action_start action_end action_number action_probability]
    input = input'; %i effed up the direction...  now can just send results

    fid = fopen(strcat(folderName,exampleName,'.py'),'w');
    fprintf(fid, 'temporal_parses = {\n');

    % find unique times, sorted
    times = sort(unique(input(:,1:2)));

    for ind = 1:numel(times)
        singleTime = times(ind);
        fprintf(fid, '\t%d: { ',singleTime);
        % collect events start/end there
        testingInput = (input(:,1:2) == singleTime);
        if any(testingInput(:,1))
            startInfo = input(testingInput(:,1),3:4);
            writeSingleAction(startInfo, true, fid);
            % then there are some starts
        end

        if any(testingInput(:,2))
            % if there were some starts, need a comma
            if any(testingInput(:,1))
                fprintf(fid, ', ');
            end
            % then there are some ends
            endInfo = input(testingInput(:,2),3:4);
            writeSingleAction(endInfo, false, fid)
        end
        fprintf(fid, ' },\n');
    end
    fprintf(fid, ' },\n');
    fclose(fid);
end

function [] = writeSingleAction(info, startBool, fid)
    nRows = size(info,1);
    for singleRowInd = 1:nRows
        if startBool
            actionAddOn = '_START';
        else
            actionAddOn = '_END';
        end
        actionName = actionLookUp(info(singleRowInd,1));
        %actionName = int2str(info(singleRowInd,1));
        energy = -log(info(singleRowInd,2));
        fprintf(fid, '"%s%s": {"energy": %f, "agent": "uuid1"}',actionName, actionAddOn, energy);
        if singleRowInd ~= nRows
            fprintf(fid, ', ');
        end
    end
end   
    
function [actionName] = actionLookUp(actionNumber)
actionNames = {'benddown' 'drink' 'makecall', 'pressbutton', 'standing', ...
    'throwtrash', 'usecomputer'};
actionName = actionNames{actionNumber};
end
    