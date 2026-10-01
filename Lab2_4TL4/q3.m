%% Question 3(a)

img = imread('KillarneyPic.png');

info = imfinfo('KillarneyPic.png');

% Image size
[height,width]= size(img);
disp(size(img));

% File size in bytes
Bytes=info.FileSize;
disp(Bytes);

%% part b 

doubleimage = im2double(img); 
imshow(doubleimage);
%% part c
%%i
doubleimage1 = im2double(img); 
for i = 1:height
    if mod(i,5) ~= 1
        doubleimage1(i,:) = 0;
    end
end

for i = 1:width
    if mod(i,5) ~= 1
        doubleimage1(:,i) = 0;
    end
end
%% ii
doubleimage2 = zeros(floor(height/5), floor(width/5));

for i = 1:width
    for j = 1:height

        if mod(j,5) == 1 && mod(i,5) == 1
            doubleimage2((j+4)/5, (i+4)/5) = doubleimage1(j,i);
        end

    end
end
%% iii
doubleimage3 = zeros(height,width);







