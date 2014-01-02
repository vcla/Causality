function cutPoints =  getCutPoints(exampleName, cutPointFileName)

fid = fopen(cutPointFileName);
tline = fgets(fid);
while ischar(tline)
    if numel(exampleName) < numel(tline)
        %disp('here')
        if isequal(tline(1:numel(exampleName)), exampleName)
            cutPointLine = tline;
            %disp(tline)
        end
    end
    tline = fgets(fid);
end
fclose(fid);

commaPoints = regexp(cutPointLine, ',');

cutPoints = zeros(1,numel(commaPoints));
for ind = 1:numel(commaPoints)
    if ind == numel(commaPoints)
        cutPoints(ind) = str2num(cutPointLine(commaPoints(ind):end));
    else
        cutPoints(ind) = str2num(cutPointLine(commaPoints(ind):(commaPoints(ind+1)-1)));
    end
end

