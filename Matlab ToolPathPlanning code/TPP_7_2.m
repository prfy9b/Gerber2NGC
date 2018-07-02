% a raft is printed first
%% Initializing and reading data
clc; clear; close all;
phi= 0; % rotation angle about x axis in degrees (CCW)
theta= 0; % rotation angle about y axis in degrees (CCW)
psi= 0; % rotation angle about z axis in degrees (CCW)

Zstep= .20; % layer thickness in mm
Xstep= .60; % raster spacing in mm
gap= Xstep/2; % distance between rasters end points and segments (in y direction)
ss= 1.5; % raft raster spacing in mm

StartDwell= .800; % start dwell time in seconds
LayerDwell= 10; % dwell time between each layer in seconds
sd= 0; % early stop distance in mm

Vext= 5; % extrusion speed in micro m/s
Vtab= 13; % table speed in mm/s
minX= 55; % minimum X for the whole part in mm
minY= 130; % minimum Y for the whole part in mm
Zjump= 20; % move up amount after each stop in mm

I= fopen(uigetfile({'*.STL';'*.*'},'select the input file')); % the dimensions of the stl file must be in mm
fgetl(I);
i= 1;
n= fgetl(I);
count = 0;
while ~ strcmp(n, 'endsolid')
    disp(count);
    N(i,:)= str2num(n(16:length(n))); % N is the normal vectors matrix
    fgetl(I);
    v= fgetl(I); V(i,:,1)= str2num(v(16:length(v))); % V is a 3D matrix (dim= no. of triangles X 3 (x y z) X 3 (for each triangle))
    v= fgetl(I); V(i,:,2)= str2num(v(16:length(v)));
    v= fgetl(I); V(i,:,3)= str2num(v(16:length(v)));
    fgetl(I);
    fgetl(I);
    n= fgetl(I);
    i= i+1;
    count = count + 7;
end

ph= phi*pi/180;
th= theta*pi/180;
si= psi*pi/180;
for i= 1:3 % this loop rotates the part (about x, y and z respectively)
    V(:,:,i)= V(:,:,i)*[cos(si)*cos(th), cos(th)*sin(si), -sin(th); ...
        cos(si)*sin(ph)*sin(th) - cos(ph)*sin(si), cos(ph)*cos(si) + sin(ph)*sin(si)*sin(th), cos(th)*sin(ph);...
        sin(ph)*sin(si) + cos(ph)*cos(si)*sin(th), cos(ph)*sin(si)*sin(th) - cos(si)*sin(ph), cos(ph)*cos(th)];
end

% Move the part to the appropriate position for the gantry system
V(:,1,:)= V(:,1,:) - min(min(V(:,1,:)))+ minX;
V(:,2,:)= V(:,2,:) - min(min(V(:,2,:)))+ minY;
V(:,3,:)= V(:,3,:) - min(min(V(:,3,:)))+ .01;
%% Slicing
Zmax= max(max(V(:,3,:)));
Z= Zstep;
j= 0; k= 0; layer= 0; u= 0;
while Z <= Zmax % for each Z plane
    for i= 1:length(V) % for each triangle
        if Z >= min(V(i,3,:)) && Z <= max(V(i,3,:)) % if Z plane has intersection with ith triangle
            u= u+1;
            one_two=   (((Z >= V(i,3,1)) && (Z <= V(i,3,2))) || ((Z >= V(i,3,2)) && (Z <= V(i,3,1)))) && ((V(i,3,2)-V(i,3,1)) ~= 0);
            % if Z plane has intersection with the side between points 1&2
            one_three= (((Z >= V(i,3,1)) && (Z <= V(i,3,3))) || ((Z >= V(i,3,3)) && (Z <= V(i,3,1)))) && ((V(i,3,3)-V(i,3,1)) ~= 0);
            % if Z plane has intersection with the side between points 1&3
            two_three= (((Z >= V(i,3,3)) && (Z <= V(i,3,2))) || ((Z >= V(i,3,2)) && (Z <= V(i,3,3)))) && ((V(i,3,2)-V(i,3,3)) ~= 0);
            % if Z plane has intersection with the side between points 3&2
            if one_two % find the intersection. P contains (x y z) of the intersection
                j= j+1;
                P(j,:)= [(V(i,1,2)-V(i,1,1))*(Z-V(i,3,1))/(V(i,3,2)-V(i,3,1))+V(i,1,1) (V(i,2,2)-V(i,2,1))*(Z-V(i,3,1))/(V(i,3,2)-V(i,3,1))+V(i,2,1) Z];
            end
            if one_three % find the intersection. Q contains (x y z) of the intersection
                k= k+1;
                Q(k,:)= [(V(i,1,3)-V(i,1,1))*(Z-V(i,3,1))/(V(i,3,3)-V(i,3,1))+V(i,1,1) (V(i,2,3)-V(i,2,1))*(Z-V(i,3,1))/(V(i,3,3)-V(i,3,1))+V(i,2,1) Z];
            end
            if two_three % find the intersection. R contains (x y z) of the intersection
                layer= layer+1;
                R(layer,:)= [(V(i,1,2)-V(i,1,3))*(Z-V(i,3,3))/(V(i,3,2)-V(i,3,3))+V(i,1,3) (V(i,2,2)-V(i,2,3))*(Z-V(i,3,3))/(V(i,3,2)-V(i,3,3))+V(i,2,3) Z];
            end
            hold on; grid on
            if one_two && one_three
                sx(u,:)= [P(j,1) Q(k,1)]; sy(u,:)= [P(j,2) Q(k,2)]; sz(u,:)= [Z Z];
                plot3(sx(u,:), sy(u,:), sz(u,:)) % plot slices in one figure
            elseif one_two && two_three
                sx(u,:)= [P(j,1) R(layer,1)]; sy(u,:)= [P(j,2) R(layer,2)]; sz(u,:)= [Z Z];
                plot3(sx(u,:), sy(u,:), sz(u,:)) % plot slices in one figure
            elseif two_three && one_three
                sx(u,:)= [R(layer,1) Q(k,1)]; sy(u,:)= [R(layer,2) Q(k,2)]; sz(u,:)= [Z Z];
                plot3(sx(u,:), sy(u,:), sz(u,:)) % plot slices in one figure
            end
        end
    end
    s= [sx sy sz]; % s contains all SEGMENTs (not rasters) for all layers. dim= ...x6 (x1 x2 y1 y2 z1 z2)
    axis([min(s(:,1))-1 max(s(:,1))+1 min(s(:,3))-1 max(s(:,3))+1 min(s(:,5))-1 max(s(:,5))+1],'equal')
    Z= Z+Zstep;
end

i= 1;
k= 0;
while i < length(s) % this loop obtains S from s just by manipulating the indices
    tmp= s(i,6);
    j= i+1;
    layer= 0;
    while (j <= length(s)) && (s(j,6)==tmp)
        j= j+1;
        layer= layer+1;
    end
    k= k+1;
    S(1:layer+1,:,k)= s(i:j-1,:); % S contains all SEGMENTs (not rasters) for all layers BUT SEPARATELY. dim= max no. seg x 6 x no. layers
    i= j;
end
%% Rastering
q= 0;
for i= 1:size(S,3) % for each layer find rasters
    SS= reshape(nonzeros(S(:,:,i)),length(nonzeros(S(:,:,i)))/6,6); % SS is S but for each layer
    
    Xmin= min(min(SS(:,1:2)));
    Xmax= max(max(SS(:,1:2)));
    X= Xmin+Xstep/2;
    j= 0;
    t= [0 0 0];
    while X <= Xmax
        for u= 1:size(SS,1)
            if (X >= min(SS(u,1:2))) &&  (X <= max(SS(u,1:2))) && (SS(u,1) ~= SS(u,2))
                j= j+1;
                t(j,:)= [X    ((SS(u,4)-SS(u,3))*X+ SS(u,3)*SS(u,2)-SS(u,4)*SS(u,1))/(SS(u,2)-SS(u,1))    SS(u,6)];
                % t will be rasters matrix! The above line finds the intersection of rasters and segments. t= [tx ty tz]
            end
        end
        X= X+Xstep;
    end
    o= 1;
    while o < size(t,1) % this loop sorts "t" with respect to X
        tmpo= t(o,1);
        r= o+1;
        while (r <= size(t,1)) && (t(r,1)== tmpo)
            r= r+1;
        end
        t(o:r-1,:)= sort(t(o:r-1,:)); % this t is the sorted raster matrix
        o= r;
    end
    
    j= 1;
    ttemp= t;
    n= size(t,1);
    ft= zeros(2,3);
    while size(ft,1) < n % this loop reorders "t" and names it as "ft". ft is the final raster matrix and is used to plot data and ...
        layer=1;
        while layer < size(t,1)
            ft(j:j+1,:)= t(layer:layer+1,:);
            ttemp(layer:layer+1,:)= 0; % after using a raster, put zeros in it's place
            while (layer < size(t,1)) && (t(layer,1)== t(layer+1,1)) % jump over rasters with same X
                layer= layer+1;
            end
            layer= layer+1;
            j= j+2;
        end
        t= reshape(nonzeros(ttemp),length(nonzeros(ttemp))/3,3); % the new "t" is formed by removing the used rasters
        ttemp= t;
    end
    
    for k= 2:2:size(ft,1)
        if rem (k/2,2)== 0
            ft(k-1:k,:)= flipud(ft(k-1:k,:)); % so the next segment is in the oposite direction
        end
    end
    
    ft(1,2)= ft(1,2)+gap;
    for k= 2:2:size(ft,1)-1
        if rem (k/2,2)== 1
            ft(k:k+1,2)= ft(k:k+1,2)-gap; % adds the gap between rasters and segments
        else
            ft(k:k+1,2)= ft(k:k+1,2)+gap; % adds the gap between rasters and segments
        end
    end
    
    figure; axis([min(s(:,1))-2 max(s(:,1))+2 min(s(:,3))-2 max(s(:,3))+2],'equal')
    hold on; grid on
    for n= 1:size(SS,1) % plot segments
        plot(SS(n,1:2), SS(n,3:4))
    end
    
    m= 1;
    while m < size(ft,1) % plot rasters; stops are represented by red lines
        
        AA= (ft(m+1,1)== ft(m,1)); % the next point is on the same raster
        BB= (ft(m+1,1)== ft(m,1)+Xstep); % the next point is on the above raster
        CC= (abs(ft(m+1,2)-ft(m,2)) < 7*Xstep); % the x coordinate of the next point is close to current point
        if (~BB || (BB&&~CC)) && ~AA % if AA -> don't stop; if ~AA and ~BB -> stop; if BB and ~CC -> stop
            plot(ft(m:m+1,1),ft(m:m+1,2),'r','LineWidth',1)
        else
            plot(ft(m:m+1,1),ft(m:m+1,2),'g','LineWidth',1)
        end
        m= m+1;
    end
    
    T(q+1:q+size(ft,1), :)= ft; % T is ft but for all layers together
    q= size(T,1);
end
%% G-code
TP= T/ 25.4; % convert to inches
J= fopen('gcode.pmc','w');
fprintf(J, '%s\r\n','// start time: ');
fprintf(J, '%s\r\n','// finish time: ');
fprintf(J, '%s\r\n\r\n','// result: ');
fprintf(J, '%s\r\n','// paste: ');
fprintf(J, '%s\r\n','// force (N): ');
fprintf(J, '%s\r\n','// ambient temperature (C): ');
fprintf(J, '%s\r\n','// nozzle temperature (C): ');
fprintf(J, '%s\r\n\r\n','// syringe temperature (C): ');
fprintf(J, '%s%1.1f\r\n','// phi (deg)= ',phi);
fprintf(J, '%s%1.1f\r\n','// theta (deg)=  ',theta);
fprintf(J, '%s%1.1f\r\n\r\n','// psi (deg)= ',psi);
fprintf(J, '%s%1.3f\r\n','// Zstep (mm)= ',Zstep);
fprintf(J, '%s%1.3f\r\n','// Xstep (mm)= ',Xstep);
fprintf(J, '%s%1.3f\r\n','// gap (mm)= ',gap);
fprintf(J, '%s%1.3f\r\n\r\n','// raft raster spacing (mm)= ',ss);
fprintf(J, '%s%1.3f\r\n','// StartDwell (s)= ',StartDwell);
fprintf(J, '%s%1.3f\r\n','// LayerDwell (s)= ',LayerDwell);
fprintf(J, '%s%1.1f\r\n\r\n','// stop distance (mm)= ',sd);
fprintf(J, '%s%1.0f\r\n','// Vext (microns/s)= ',Vext);
fprintf(J, '%s%1.0f\r\n\r\n','// Vtab (mm/s)= ',Vtab);
fprintf(J, '%s%1.0f\r\n','// minX (mm)= ',minX);
fprintf(J, '%s%1.0f\r\n','// minY (mm)= ',minY);
fprintf(J, '%s%1.0f\r\n\r\n','// Zjump (mm)= ',Zjump);

fprintf(J, '%s\r\n','A'); % abort any other running commands
fprintf(J, '%s\r\n','close'); % close any other programs
fprintf(J, '%s\r\n','delete gather');
fprintf(J, '%s\r\n','open prog 400'); % this is program # 400
fprintf(J, '%s\r\n\r\n','clear');
fprintf(J, '%s\r\n','G20'); % programming in inches
fprintf(J, '%s\r\n','G90'); % absolute programming
fprintf(J, '%s\r\n','DIS PLC 18'); % so that we can change extrusion speed 
fprintf(J, '%s%1.0f\r\n\r\n','M1111=',Vext*550); % extrusion speed (5500 means 10 mic m/s)
fprintf(J, '%s\r\n','M1113==-20000'); % stop extrusion
fprintf(J, '%s\r\n','X0 Y0 F50.0'); % go to (0", 0") at 50 in/min 
fprintf(J, '%s\r\n','DWELL2000'); % stay for 2 sec

% print raft
maxX= max(max(V(:,1,:)));
maxY= max(max(V(:,2,:)));
fprintf(J, 'Z%1.3f\r\n', Zjump/25.4);
fprintf(J, 'X%1.3f Y%1.3f\r\n', minX/25.4, minY/25.4);%到达最左下角
fprintf(J, 'Z%1.3f F%1.1f\r\n',TP(1,3), Vtab*60/25.4);%到达第一层的Z
fprintf(J, '%s\r\n','M1113==+20000');%start extrusion
fprintf(J, '%s%1.0f\r\n','DWELL',StartDwell*1000);%start dwell
for i= 1:ceil((maxY-minY)/ss/2)+1%计算raft 的raster数，挨个打印
    fprintf(J, 'X%1.3f Y%1.3f\r\n', minX/25.4, (minY+ (2*i-2)*ss)/25.4);
    fprintf(J, 'X%1.3f Y%1.3f\r\n', maxX/25.4, (minY+ (2*i-2)*ss)/25.4);
    fprintf(J, 'X%1.3f Y%1.3f\r\n', maxX/25.4, (minY+ (2*i-1)*ss)/25.4);
    fprintf(J, 'X%1.3f Y%1.3f\r\n', minX/25.4, (minY+ (2*i-1)*ss)/25.4);
end
fprintf(J, '%s\r\n','M1113==-20000');%stop extrusion
fprintf(J, 'Z%1.3f F50.0\r\n', Zjump/25.4);
fprintf(J,'%s\r\n','X0 Y0');
fprintf(J,'%s\r\n','Z0');
fprintf(J,'%s%1.0f\r\n\r\n','DWELL',LayerDwell*1000);

% print part on top of raft
TP(:,3)= TP(:,3)+ TP(1,3);%所有层z坐标都+第一层的z
fprintf(J, '%s\r\n','P1986=1.0'); % layer number
fprintf(J, 'Z%1.3f\r\n', Zjump/25.4);%lift nozzle
fprintf(J, 'X%1.3f Y%1.3f\r\n', TP(1,1), TP(1,2));
fprintf(J, 'Z%1.3f F%1.1f\r\n',TP(1,3), Vtab*60/25.4);
fprintf(J, '%s\r\n','M1113==+20000');
fprintf(J, '%s%1.0f\r\n','DWELL',StartDwell*1000);

i= 2;
P1986= 1;
while i < size(TP,1)-1
    fprintf(J, 'X%1.3f Y%1.3f Z%1.3f\r\n', TP(i,1), TP(i,2), TP(i,3));
    
    A= (TP(i+2,1)== TP(i+1,1)); % the next point is on the same raster
    B= (abs(TP(i+2,1)-TP(i+1,1)-Xstep/25.4)<1e-10); % the next point is on the above raster
    C= (abs(TP(i+2,2)-TP(i+1,2)) < 7*Xstep/25.4); % the y coordinate of the next point is close to current point
    if (~B || (B&&~C)) && ~A % if A -> don't stop; if ~A and ~B -> stop; if B and ~C -> stop (如果stop)
        i= i+1;
        if TP(i,2) < TP(i-1,2)%（如果下一个点在下）
            fprintf(J, 'X%1.3f Y%1.3f Z%1.3f\r\n', TP(i,1), TP(i,2)+sd/25.4, TP(i,3)); % go to early stop point
        else%（如果下一个点在上）
            fprintf(J, 'X%1.3f Y%1.3f Z%1.3f\r\n', TP(i,1), TP(i,2)-sd/25.4, TP(i,3)); % go to early stop point
        end
        fprintf(J, '%s\r\n','M1113==-20000');
        fprintf(J, 'X%1.3f Y%1.3f Z%1.3f\r\n', TP(i,1), TP(i,2), TP(i,3));
        fprintf(J, 'Z%1.3f F50.0\r\n',TP(i-1,3)+ Zjump/25.4);
        
        if TP(i+1,3) > TP(i,3) % if next layer
            fprintf(J,'%s\r\n','X0 Y0');
            fprintf(J,'%s\r\n','Z0');
            fprintf(J,'%s%1.0f\r\n','DWELL',LayerDwell*1000);
            P1986= P1986+1;
            fprintf(J,'%s%1.1f\r\n','P1986=',P1986);
        end
        
        fprintf(J, 'Z%1.3f F50.0\r\n',TP(i-1,3)+ Zjump/25.4);
        fprintf(J, 'X%1.3f Y%1.3f \r\n', TP(i+1,1), TP(i+1,2));
        fprintf(J, 'Z%1.3f F%1.1f\r\n',TP(i+1,3), Vtab*60/25.4);
        fprintf(J, '%s\r\n','M1113==+20000');
        fprintf(J, '%s%1.0f\r\n','DWELL',StartDwell*1000);
        i= i+1;
    end
    i= i+1;
end
fprintf(J, 'X%1.3f Y%1.3f Z%1.3f\r\n', TP(i,1), TP(i,2), TP(i,3));
fprintf(J, 'X%1.3f Y%1.3f Z%1.3f\r\n', TP(i+1,1), TP(i+1,2), TP(i+1,3));
fprintf(J, '%s\r\n','M1113==-20000');
fprintf(J, 'Z%1.3f F50.0\r\n',TP(i,3)+ Zjump/25.4);
fprintf(J,'%s\r\n','X0 Y0');
fprintf(J, '%s','close');
fclose(J);