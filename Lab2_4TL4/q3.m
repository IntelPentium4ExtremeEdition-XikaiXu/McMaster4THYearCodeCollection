%%Question3 
%

%a 
filename = 'KillarneyPic.png';

img = imread(filename);
[h,w,c] = size(img);
d = dir(filename);

fprintf('Image Information\n');
fprintf('-----------------\n');
fprintf('Width     : %d px\n', w);
fprintf('Height    : %d px\n', h);
fprintf('Channels  : %d\n', c);
fprintf('File Size : %d bytes\n', d.bytes);
fprintf('File Size : %.2f KB\n', d.bytes/1024);

doulbeimg = im2double(img);
imshow(doulbeimg);

