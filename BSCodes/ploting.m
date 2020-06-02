clear;clc;
filename = 'log.txt'
f = csvread(filename)

x = 1:size(f)(1);

no = size(f)(2);

y1 = f(:,1);
y2 = f(:,2);
y3 = f(:,3);
y4 = f(:,4);

plot(x,y1,x,y2,x,y3,x,y4);
legend('Hydrogen','Alcohol','Carbon Dioxide','Carbon Monoxide');

