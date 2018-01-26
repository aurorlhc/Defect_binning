IMG = imread('Manual-Window1-Top-CMix0-0516090201.jpeg');
gray = rgb2gray(IMG);
B = gray;

for i=1:480
    for j=1:480
        if B(i,j) > 150
            B(i,j) = 255;
        else
            B(i,j) = 1;
        end;
    end;
end;

% figure,
% imshow(B);
% figure,
% imshow(I);

subplot(1,2,1), imshow(gray)
subplot(1,2,2), imshow(B);
imwrite(B, 'Manual-Window1-Top-CMix0-0516090201.png');

% fid = fopen('Manual-Window1-C-ABWMix0-0420113720.txt','w');
% for i = 1:960
%     for j = 1:960
%         fprintf(fid, '%f\n', B(i,j)); %\n is for new line, \t is tab
%     end
% end
% 
% fclose(fid);




