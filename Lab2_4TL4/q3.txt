%% Question 3(a)

%Import KillarneyPic.png
img = imread('KillarneyPic.png');

info = imfinfo('KillarneyPic.png');

% Image size
[height,width]= size(img);
disp(size(img));

% bytes
Bytes=info.FileSize;
disp(Bytes);

%% part b Convert the imported picture into a double-class variable, plot it

doubleimage = im2double(img); 
imshow(doubleimage);
%% part c
%%i Impulse sampling at 1/5 of the original rate

doubleimage1 = im2double(img); 
for i = 1:height
    if mod(i,5) ~= 1 %when the indices is divided by 5 and has 1 as remainder, keep their value
        doubleimage1(i,:) = 0;
    end
end

for i = 1:width
    if mod(i,5) ~= 1
        doubleimage1(:,i) = 0;
    end
end
%% ii Downsampling by a factor of 5
%if doubleimage1 has data for one index, recorded in double image 2.
doubleimage2 = zeros(ceil(height/5), ceil(width/5));

for i = 1:width
    for j = 1:height

        if mod(j,5) == 1 && mod(i,5) == 1
            doubleimage2((j+4)/5, (i+4)/5) = doubleimage1(j,i);
        end

    end
end
%% iii
doubleimage3 = zeros(height, width);

%Horizontal reconstruction

for i = 1:size(doubleimage2,1) %the number of rows of downsampling matrix
    for j = 1:size(doubleimage2,2)

        for k = 1:5
            col = (j-1)*5 + k;

            if col <= width
                doubleimage3(i,col) = doubleimage2(i,j); % copy the value in part ii and paste for 5 times horizontally
            end

        end
    end
end

%Vertical reconstruction

temp = doubleimage3;

for i = 1:size(temp,1)
    for j = 1:width

        for k = 1:5
            row = (i-1)*5 + k;

            if row <= height
                doubleimage3(row,j) = temp(i,j); %copy the value in the matrix above and paste for 5 times vertically
            end

        end
    end
end
%% iv.
doubleimage4 = zeros(height, width);

small_height = size(doubleimage2,1);
small_width = size(doubleimage2,2);


% Horizontal interpolation

for i = 1:small_height

    for j = 1:small_width-1   %%last column will be process individually

        % Two known samples
        x1 = doubleimage2(i,j);
        x2 = doubleimage2(i,j+1);

        % Calculate the 4 points between x1 and x2
        points = interpolate4(x1,x2);

        % Starting column
        start_col = (j-1)*5 + 1;

        % First known point
        doubleimage4(i,start_col) = x1;

        % Four interpolated points
        for k = 1:4
            col = start_col + k;

            if col <= width
                doubleimage4(i,col) = points(k);
            end
        end

    end

    % Last column
    j = small_width;
    start_col = (j-1)*5 + 1;

    for col = start_col:width
        doubleimage4(i,col) = doubleimage2(i,j);
    end

end


%Vertical interpolation

temp = doubleimage4;
doubleimage4 = zeros(height,width);

for j = 1:width

    for i = 1:small_height-1

        % Two known samples
        x1 = temp(i,j);
        x2 = temp(i+1,j);

        % Calculate the 4 points between x1 and x2
        points = interpolate4(x1,x2);

        % Starting row
        start_row = (i-1)*5 + 1;

        % First known point
        doubleimage4(start_row,j) = x1;

        % Four interpolated points
        for k = 1:4
            row = start_row + k;

            if row <= height
                doubleimage4(row,j) = points(k);
            end
        end

    end

    % Last row
    i = small_height;
    start_row = (i-1)*5 + 1;

    for row = start_row:height
        doubleimage4(row,j) = temp(i,j);
    end

end

%% Part d
%plot the figure for the 4 double matrixes
figure;


imshow(doubleimage1);
title('(i) Impulse Sampling');

figure;
imshow(doubleimage2);
title('(ii) Downsampling');

figure;
imshow(doubleimage3);
title('(iii) Zero-Order Hold');

figure;
imshow(doubleimage4);
title('(iv) First-Order Hold');

%% function used (linear interpolation)
function points = interpolate4(x1,x2)

    points = zeros(1,4);

    for k = 1:4
        points(k) = x1 + k*(x2-x1)/5;
    end

end






