format long eng
clear all
close all
clc

rf=2.9985e9/30;
bunch_xing=rf/32;    % bunch xing frequency from accelerator/EVR
R=33;
Fref=bunch_xing/R;
% test for Raimund Feifel at 1 kHz chopper speed
% Fref=1./192e-9/43;

Tref=1./Fref;
Nslits=120;

FPGA_CLK=125e6;             % Hz, CLK of the fast part of the FPGA (PFD+TDC)
FPGA_Ts=1./FPGA_CLK;
PFD_CLK=100e3;              % Hz, CLK at which a new measurement of delta phase is available
PFD_Ts=1./PFD_CLK;
PHCTRLR_CLK=100;            % Hz, CLK of the phase controller
PHCTRLR_Ts=1./PHCTRLR_CLK;

actual_FPGA_CLK=124986108;  % Hz: actual (measured) value from 33.33 MHz PS crystal (with its tolerance)
                            %     which undergoes a *45/12 in a FPGA PLL;
                            %     used for accurate frequency readout

%PWM_CLK= PHCTRLR_CLK*100;
PWM_CLK= 5.e3;              % Hz: value = 2* desired freq of the INC/DEC 
                            % pulses sent to the MECOS freq controller;
                            % it must be a multiple of PHCTRLR_CLK (100 Hz)
                            % and also a submultiple of FPGA_CLK (125 MHz)
                            % -> multiplier must be 2^n*5^m ; n<=4; m<=7
PWM_Ts= 1./PWM_CLK;

%MAXPULSES= (PWM_CLK/2)*PHCTRLR_Ts;
MECOS_CTRLR_CLK=6127.5;
MECOS_CTRLR_Ts=1/MECOS_CTRLR_CLK;
MAXPULSES=floor(MECOS_CTRLR_CLK/PHCTRLR_CLK);

debouncer_cycles=5;
debouncer_mecos_cycles=5000;

phase_setpoint_degrees=0;

TDC_cnt_per_period = round(FPGA_CLK/Fref);

F_lock_thr=1;
PH_lock_thr=4;


%--- MECOS speed controller
f_step=5.6e-6;          % Hz: frequency step command to MECOS controller
MECOS_MAX_PULSES=7000;  % max INC/DEC pulses per second
f0_MECOS=0.4;           % Hz: closed loop cutoff freq
zeta_MECOS=0.6;         % damping factor of II ord sys 
                        % approximating the MECOS closed loop
          
%--- loop filter
G_loopfilt=1e-3;
fzero_loopfilt=0.02;    % Hz; frequency of lead-lag zero
fpole_loopfilt=2;       % Hz; frequency of lead-lag pole

% %--- additional integrator
% wi=0.01*2*pi;

%--- FW model
Nbit_Cntr=37;           % NCO counter bit width
FTW_nom_100kHz=round(Fref/FPGA_CLK*2^(Nbit_Cntr+1));
FTW_nom_3MHz=round(bunch_xing/FPGA_CLK*2^(Nbit_Cntr+1));
MECOS_dec=round(FPGA_CLK/MECOS_CTRLR_CLK);  % MECOS DSP I/O sampling freq
MECOS_CLK=FPGA_CLK/MECOS_dec;       % Hz: the sampling freq of our model of MECOS
                                    % done like this just to have an
                                    % integer decimation ratio and be
                                    % coherent with that in the IIR
                                    % implementation
MECOS_Ts=1/MECOS_CLK;

%---------------------------



% continuous time system
kv=2*pi*f_step./PHCTRLR_Ts; % accel command = delta omega / delta t
w0_MECOS=f0_MECOS*2*pi;
MECOS_cl_den=[1/w0_MECOS^2 2*zeta_MECOS/w0_MECOS 1];
MECOS=tf(kv,[MECOS_cl_den 0]);

% IIR of the MECOS closed loop equivalent:
WT = w0_MECOS*MECOS_Ts;
Bet0 =  4/WT^2 + 4.*zeta_MECOS/WT + 1;
Bet1 = -8/WT^2 +                    2;
Bet2 =  4/WT^2 - 4.*zeta_MECOS/WT + 1;
MECOS_A0 = 1./Bet0;
MECOS_A1 = 2./Bet0;
MECOS_A2 = 1./Bet0;
MECOS_B1 = Bet1/Bet0;
MECOS_B2 = Bet2/Bet0;

PFD = tf(Tref/(2*pi),[1 0]);
%TDC = 1./Tref*Ts./Tclock;
TDC = FPGA_CLK;     % TDC gain is just its clock 
                    % remember that PFD output is a time, 
                    % with Tf corresponding to 2pi of phase
% decimation
decimation_fact=PFD_CLK/PHCTRLR_CLK;
decim_passband=10;          % Hz: lowpass antialias on the PFD
decim_shift=2^20;           % I put a shift after the CIC -> gain = 1/1024.
decim_gain= decimation_fact*decimation_fact/decim_shift;    % it's a two-stage CIC

% loop filter
phlead=tf([1/(fzero_loopfilt*2*pi) 1],[1/(fpole_loopfilt*2*pi) 1]);
%integr=tf([1 wi],[1 0]);
loopfilt=G_loopfilt*phlead;
%loopfilt=G_loopfilt*integr*phlead;


% the additional LP doesn't seem to influence the overall loop 
% (we designed it that way), so just plot the continuous regular stuff
forw      = PFD * TDC * decim_gain * loopfilt * MECOS;
%forw      = PFD * TDC * decim_gain * LP_add_c * loopfilt * MECOS;
open_loop = forw * Nslits;

choPLL = feedback(forw,Nslits);
%choPLL = feedback(open_loop,1);

figure(1)
%bode(choPLL);
bode(open_loop);
grid on


% convert loopfilt to discrete for simulink
% do phase lead and integrator separately

% phase lead
% first: let matlab do it
phleadz= c2d(phlead,PHCTRLR_Ts,'tustin');
[num_loop_filtZ, den_loop_filtZ]=tfdata(phleadz,'v');
% then: check it yourself
wz=fzero_loopfilt*2*pi;
wp=fpole_loopfilt*2*pi;
Ts=PHCTRLR_Ts;
Sz=Ts/2*wz+1;
Dz=Ts/2*wz-1;
Sp=Ts/2*wp+1;
Dp=Ts/2*wp-1;
A_lf=wp/wz*Sz/Sp;
my_num_loop_filtZ = A_lf*[1 Dz/Sz];
my_den_loop_filtZ = [1 Dp/Sp];
% compare them: the difference should be ~10e-15 = float precision
my_num_loop_filtZ-num_loop_filtZ
my_den_loop_filtZ-den_loop_filtZ
% coefficients for the IIR implementation in sysgen
IIR_C_Y1= -my_den_loop_filtZ(2);
IIR_C_X = G_loopfilt*my_num_loop_filtZ(1);
IIR_C_X1= G_loopfilt*my_num_loop_filtZ(2);

% % additional integrator
% A0_integr = wi*PHCTRLR_Ts/2. + 1;
% A1_integr = wi*PHCTRLR_Ts/2. - 1;
% integrz= c2d(integr,PHCTRLR_Ts,'tustin');
% [num_integrZ, den_integrZ]=tfdata(integrz,'v');
% DIY_num_integrZ=[A0_integr A1_integr];
% DIY_den_integrZ=[1 -1];
% % compare them: the difference should be ~10e-15 = float precision
% DIY_num_integrZ - num_integrZ
% DIY_den_integrZ - den_integrZ
% 
% % check effect of finite bit length on additional integrator implementation
% Afract=16;
% Bfract=0;
% mynum=round(DIY_num_integrZ*2^Afract)./2^Afract;
% myden=round(DIY_den_integrZ*2^Bfract)./2^Bfract;
% integr_precise=tf(DIY_num_integrZ, DIY_den_integrZ, PHCTRLR_Ts);
% integr_approx=tf(mynum, myden,PHCTRLR_Ts);
% figure(6)
% bode(integr_precise, integr_approx, {1.e-5,10});
% grid on;
% legend();
% title('Additional Integrator Bode');


% % check effect of finite bit length on phase lead implementation
% Afract=7;
% Bfract=17;
% mynum=round(my_num_loop_filtZ*2^Afract)./2^Afract;
% myden=round(my_den_loop_filtZ*2^Bfract)./2^Bfract;
% PHL_precise=tf(my_num_loop_filtZ, my_den_loop_filtZ, PHCTRLR_Ts);
% PHL_approx=tf(mynum, myden,PHCTRLR_Ts);
% figure(5)
% bode(PHL_precise);
% grid on;
% hold on
% bode(PHL_approx);
% hold off
% legend();




% Now compare matlab and DIY discretization of Mecos closed loop

MECOS_cl_equiv = tf(1,MECOS_cl_den);
MECOS_cl_z = c2d(MECOS_cl_equiv,MECOS_Ts,'tustin');
[matlab_num_MECOS_cl_z, matlab_den_MECOS_cl_z]=tfdata(MECOS_cl_z,'v');

DIY_num_MECOS_cl_z= [MECOS_A0 MECOS_A1 MECOS_A2];
DIY_den_MECOS_cl_z= [1 MECOS_B1 MECOS_B2];
% compare them: the difference should be ~10e-15 = float precision
matlab_num_MECOS_cl_z-DIY_num_MECOS_cl_z
matlab_den_MECOS_cl_z-DIY_den_MECOS_cl_z

% check effect of finite bit length on IIR implementation
%Afract=40;
%Bfract=16;
Afract=40;
Bfract=24;
mynum=round(DIY_num_MECOS_cl_z*2^Afract)./2^Afract;
myden=round(DIY_den_MECOS_cl_z*2^Bfract)./2^Bfract;
IIR_precise=tf(DIY_num_MECOS_cl_z, DIY_den_MECOS_cl_z, MECOS_Ts);
IIR_approx=tf(mynum, myden,MECOS_Ts);
figure(2)
bode(IIR_precise);
grid on;
hold on
bode(IIR_approx);
hold off
legend();



% TDC unwrap shenanigans
max_unwrap_periods=50;      % saturate at this max number of unwrap periods
%unwrap_res_thr=20;
unwrap_res_thr=10;          % INC/DEC pulses to declare frequency lock 
                            % (but not yet phase lock)
unwrap_res_period_thr=0;    % if the freq correction is small and we have 
                            % unwrapped more than unwrap_res_period_thr 
                            % periods, then reset the unwrapper
unwrap_reset_inhibit_cycles = 20000;    % number of 100 kHz cycles to wait 
                                        % after a unwrap reset has been 
                                        % issued, before allowing another 
                                        % reset; this gives the controller 
                                        % the time to build a DF command
%wrap_detect_thr=round(TDC_cnt_per_period*0.9);
wrap_detect_thr=round(TDC_cnt_per_period*0.55);


% load decimation fir, designed with filterDesigner
load firnum Num
dectaps_int=round(Num*2^20);    % FIR taps are sfix 18.20
dectaps=dectaps_int/(2^20);     % FIR taps are sfix 18.20

% noise
ENBW=1.e6;                              % Hz
sigma_noise=50e-9;                      % sec (we are on TDC output)
PFD_noise_corrtime=1./ENBW;
PFD_jitter_PSD=sigma_noise^2./ENBW;     % noise power spectral density to inject

% additional LowPass
load LPnum LP_num
LP_additional=tf(LP_num,[1],PHCTRLR_Ts);
LP_add_c= d2c(LP_additional,'tustin');
figure(3)
bode(LP_additional);
grid on;
hold on;
bode(LP_add_c);
legend();
lptaps_int=round(LP_num*2^20);    % FIR taps are sfix 18.20
lptaps=lptaps_int/(2^20);         % FIR taps are sfix 18.20

% ratio between MECOS FW model NCO resolution
% and nominal MECOS deltaF step

%MECOS_DF_gain= (f_step*Nslits) / (FPGA_CLK/2^(Nbit_Cntr+1));
% for some reason, on the physical system I measure ~0.25 the gain that 
% I see from my MECOS emulator; I was not able to understand why; I just
% put a correction factor (0.25), for now
MECOS_DF_gain= 0.25* (f_step*Nslits) / (FPGA_CLK/2^(Nbit_Cntr+1));


% ----------- notch  ----------------------------------------------------
%notch_f0=2.125;       % Hz
%notch_bw=1;      % Hz, 3-dB BW
notch_f0=2.125;       % Hz
notch_bw=0.2;      % Hz, 3-dB BW

% matlab version
w0=notch_f0/(PHCTRLR_CLK/2);
bw=notch_bw/(PHCTRLR_CLK/2);
[num_notch_m, den_notch_m]= iirnotch(w0, bw)
IIR_n_matlab=tf(num_notch_m, den_notch_m, PHCTRLR_Ts);

% DIY version
wn0=notch_f0*2*pi;
Q=notch_f0/notch_bw;
x=2/(PHCTRLR_Ts*wn0);
al0=1+x^2;
al1=2*(1-x^2);
al2=1+x^2;
be0=1+x/Q+x^2;
be1=2*(1-x^2);
be2=1-x/Q+x^2;

notch_A0=al0/be0;
notch_A1=al1/be0;
notch_A2=al2/be0;
notch_B1=be1/be0;
notch_B2=be2/be0;

diynum=[notch_A0 notch_A1 notch_A2]
diyden=[1 notch_B1 notch_B2]

IIR_n_diy=tf(diynum, diyden, PHCTRLR_Ts);


% use sfix 16.14 for both num and den
A_n_fract=14;
B_n_fract=14;
approxnum_n=round(diynum*2^A_n_fract)./2^A_n_fract;
approxden_n=round(diyden*2^B_n_fract)./2^B_n_fract;
IIR_n_approx=tf(approxnum_n, approxden_n,PHCTRLR_Ts);

% % plot
% figure(4)
% bode(IIR_n_matlab);
% grid on;
% hold on
% bode(IIR_n_diy);
% bode(IIR_n_approx);
% hold off
% legend();

% there is a little discrepancy betwee DIY and matlab, but I don't know
% whether "iirnotch" uses a non-pre-warped bilinear or something else
% anyway, I'm happy with that and I'll use my coeffs

% print out IIR coefficients in hex
A0_int=round(notch_A0*2^A_n_fract);
A1_int=round(notch_A1*2^A_n_fract);
A2_int=round(notch_A2*2^A_n_fract);
B1_int=round(notch_B1*2^B_n_fract);
B2_int=round(notch_B2*2^B_n_fract);
fprintf("notch_A0=A2=0x%s\n",dec2hex(A0_int,4));
fprintf("notch_A1=B1=0x%s\n",dec2hex(A1_int,4));
fprintf("notch_B2=0x%s\n",dec2hex(B2_int,4));


% check effect of finite bit length on decimator lowpass

% mynum=dectaps;
% myden=1;
% LPD=tf(mynum, myden,PFD_Ts);
% figure(4)
% bode(LPD);
% grid on;







