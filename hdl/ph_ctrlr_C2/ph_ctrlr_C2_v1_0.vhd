library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity ph_ctrlr_C2_v1_0 is
	generic (
		-- Users to add parameters here
        UNWRAP_RES_THR_DEFAULT : integer := 10;
        REF_SCALER_DEFAULT : integer := 33;
        CHOP_SCALER_DEFAULT : integer := 1;
        TRIGOUT_PHASE_DEFAULT : integer := 1;
        EXTRA_GAIN_DEFAULT  : integer := 16#6000#;

		-- User parameters ends
		-- Do not modify the parameters beyond this line


		-- Parameters of Axi Slave Bus Interface S00_AXI
		C_S00_AXI_DATA_WIDTH	: integer	:= 32;
		C_S00_AXI_ADDR_WIDTH	: integer	:= 6
	);
	port (
		-- Users to add ports here

        -- input
        Df_cmd                  : in STD_LOGIC_VECTOR (21 downto 0);
        ph_err                  : in STD_LOGIC_VECTOR (23 downto 0);
        f_lock                  : in STD_LOGIC;
        ph_lock                 : in STD_LOGIC;
        ce_phctrlr              : in STD_LOGIC;
        REF_freq_meas           : in STD_LOGIC_VECTOR (31 downto 0);
        REF_freq_strobe         : in STD_LOGIC;
        VCO_freq_meas           : in STD_LOGIC_VECTOR (31 downto 0);
        VCO_freq_strobe         : in STD_LOGIC;
        MECOS_freq_meas         : in STD_LOGIC_VECTOR (31 downto 0);
        MECOS_freq_strobe       : in STD_LOGIC;
        
        -- output
        siggen_DFTW             : out STD_LOGIC_VECTOR (31 downto 0);
        ph_setpoint_cnts        : out STD_LOGIC_VECTOR (16 downto 0);
        unwr_en                 : out STD_LOGIC;
        unwr_res_en             : out STD_LOGIC;
        unwr_res_thr            : out STD_LOGIC_VECTOR (16 downto 0);
        phctrlr_soft_res        : out STD_LOGIC;
        R                       : out STD_LOGIC_VECTOR (15 downto 0);
        N                       : out STD_LOGIC_VECTOR (15 downto 0);
        TRIGPH                  : out STD_LOGIC_VECTOR (15 downto 0);
        Extra_Gain              : out STD_LOGIC_VECTOR (15 downto 0);
        FMC_INTF_EN1            : out STD_LOGIC;
        FMC_INTF_EN2            : out STD_LOGIC;

		-- User ports ends
		-- Do not modify the ports beyond this line


		-- Ports of Axi Slave Bus Interface S00_AXI
		s00_axi_aclk	: in std_logic;
		s00_axi_aresetn	: in std_logic;
		s00_axi_awaddr	: in std_logic_vector(C_S00_AXI_ADDR_WIDTH-1 downto 0);
		s00_axi_awprot	: in std_logic_vector(2 downto 0);
		s00_axi_awvalid	: in std_logic;
		s00_axi_awready	: out std_logic;
		s00_axi_wdata	: in std_logic_vector(C_S00_AXI_DATA_WIDTH-1 downto 0);
		s00_axi_wstrb	: in std_logic_vector((C_S00_AXI_DATA_WIDTH/8)-1 downto 0);
		s00_axi_wvalid	: in std_logic;
		s00_axi_wready	: out std_logic;
		s00_axi_bresp	: out std_logic_vector(1 downto 0);
		s00_axi_bvalid	: out std_logic;
		s00_axi_bready	: in std_logic;
		s00_axi_araddr	: in std_logic_vector(C_S00_AXI_ADDR_WIDTH-1 downto 0);
		s00_axi_arprot	: in std_logic_vector(2 downto 0);
		s00_axi_arvalid	: in std_logic;
		s00_axi_arready	: out std_logic;
		s00_axi_rdata	: out std_logic_vector(C_S00_AXI_DATA_WIDTH-1 downto 0);
		s00_axi_rresp	: out std_logic_vector(1 downto 0);
		s00_axi_rvalid	: out std_logic;
		s00_axi_rready	: in std_logic
	);
end ph_ctrlr_C2_v1_0;

architecture arch_imp of ph_ctrlr_C2_v1_0 is

	-- component declaration
	component ph_ctrlr_C2_v1_0_S00_AXI is
		generic (
        UNWRAP_RES_THR_DEFAULT : integer := 10;
        REF_SCALER_DEFAULT  : integer := 33;
        CHOP_SCALER_DEFAULT : integer := 1;
        TRIGOUT_PHASE_DEFAULT : integer := 1;
        EXTRA_GAIN_DEFAULT  : integer := 16#6000#;
		C_S_AXI_DATA_WIDTH	: integer	:= 32;
		C_S_AXI_ADDR_WIDTH	: integer	:= 6
		);
		port (
		-- user ports
		-- input
		Df_cmd                  : in STD_LOGIC_VECTOR (21 downto 0);
        ph_err                  : in STD_LOGIC_VECTOR (23 downto 0);
        f_lock                  : in STD_LOGIC;
        ph_lock                 : in STD_LOGIC;
        ce_phctrlr              : in STD_LOGIC;
        REF_freq_meas           : in STD_LOGIC_VECTOR (31 downto 0);
        REF_freq_strobe         : in STD_LOGIC;
        VCO_freq_meas           : in STD_LOGIC_VECTOR (31 downto 0);
        VCO_freq_strobe         : in STD_LOGIC;
        MECOS_freq_meas         : in STD_LOGIC_VECTOR (31 downto 0);
        MECOS_freq_strobe       : in STD_LOGIC;
        
        -- output
        siggen_DFTW             : out STD_LOGIC_VECTOR (31 downto 0);
        ph_setpoint_cnts        : out STD_LOGIC_VECTOR (16 downto 0);
        unwr_en                 : out STD_LOGIC;
        unwr_res_en             : out STD_LOGIC;
        unwr_res_thr            : out STD_LOGIC_VECTOR (16 downto 0);
        phctrlr_soft_res        : out STD_LOGIC;
        R                       : out STD_LOGIC_VECTOR (15 downto 0);
        N                       : out STD_LOGIC_VECTOR (15 downto 0);
        TRIGPH                  : out STD_LOGIC_VECTOR (15 downto 0);
        Extra_Gain              : out STD_LOGIC_VECTOR (15 downto 0);
        FMC_INTF_EN1            : out STD_LOGIC;
        FMC_INTF_EN2            : out STD_LOGIC;

		-- auto generated ports
		S_AXI_ACLK	: in std_logic;
		S_AXI_ARESETN	: in std_logic;
		S_AXI_AWADDR	: in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
		S_AXI_AWPROT	: in std_logic_vector(2 downto 0);
		S_AXI_AWVALID	: in std_logic;
		S_AXI_AWREADY	: out std_logic;
		S_AXI_WDATA	: in std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
		S_AXI_WSTRB	: in std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0);
		S_AXI_WVALID	: in std_logic;
		S_AXI_WREADY	: out std_logic;
		S_AXI_BRESP	: out std_logic_vector(1 downto 0);
		S_AXI_BVALID	: out std_logic;
		S_AXI_BREADY	: in std_logic;
		S_AXI_ARADDR	: in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
		S_AXI_ARPROT	: in std_logic_vector(2 downto 0);
		S_AXI_ARVALID	: in std_logic;
		S_AXI_ARREADY	: out std_logic;
		S_AXI_RDATA	: out std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
		S_AXI_RRESP	: out std_logic_vector(1 downto 0);
		S_AXI_RVALID	: out std_logic;
		S_AXI_RREADY	: in std_logic
		);
	end component ph_ctrlr_C2_v1_0_S00_AXI;

begin

-- Instantiation of Axi Bus Interface S00_AXI
ph_ctrlr_C2_v1_0_S00_AXI_inst : ph_ctrlr_C2_v1_0_S00_AXI
	generic map (
        UNWRAP_RES_THR_DEFAULT => UNWRAP_RES_THR_DEFAULT,
        REF_SCALER_DEFAULT => REF_SCALER_DEFAULT,
        CHOP_SCALER_DEFAULT => CHOP_SCALER_DEFAULT,
        TRIGOUT_PHASE_DEFAULT => TRIGOUT_PHASE_DEFAULT,
        EXTRA_GAIN_DEFAULT => EXTRA_GAIN_DEFAULT,
		C_S_AXI_DATA_WIDTH	=> C_S00_AXI_DATA_WIDTH,
		C_S_AXI_ADDR_WIDTH	=> C_S00_AXI_ADDR_WIDTH
	)
	port map (
		-- user ports
		-- input
		Df_cmd => Df_cmd, 
        ph_err => ph_err,
        f_lock => f_lock,
        ph_lock => ph_lock,
        ce_phctrlr => ce_phctrlr,
        REF_freq_meas => REF_freq_meas,
        REF_freq_strobe => REF_freq_strobe,
        VCO_freq_meas => VCO_freq_meas,
        VCO_freq_strobe => VCO_freq_strobe,
        MECOS_freq_meas => MECOS_freq_meas,
        MECOS_freq_strobe => MECOS_freq_strobe,
        
        -- output
        siggen_DFTW => siggen_DFTW,
        ph_setpoint_cnts => ph_setpoint_cnts,
        unwr_en => unwr_en,
        unwr_res_en => unwr_res_en,
        unwr_res_thr => unwr_res_thr,
        phctrlr_soft_res => phctrlr_soft_res,
        R => R,
        N => N,
        TRIGPH => TRIGPH,
        Extra_Gain   => Extra_Gain,
        FMC_INTF_EN1 => FMC_INTF_EN1,
        FMC_INTF_EN2 => FMC_INTF_EN2,

		-- auto generated ports
		S_AXI_ACLK	=> s00_axi_aclk,
		S_AXI_ARESETN	=> s00_axi_aresetn,
		S_AXI_AWADDR	=> s00_axi_awaddr,
		S_AXI_AWPROT	=> s00_axi_awprot,
		S_AXI_AWVALID	=> s00_axi_awvalid,
		S_AXI_AWREADY	=> s00_axi_awready,
		S_AXI_WDATA	=> s00_axi_wdata,
		S_AXI_WSTRB	=> s00_axi_wstrb,
		S_AXI_WVALID	=> s00_axi_wvalid,
		S_AXI_WREADY	=> s00_axi_wready,
		S_AXI_BRESP	=> s00_axi_bresp,
		S_AXI_BVALID	=> s00_axi_bvalid,
		S_AXI_BREADY	=> s00_axi_bready,
		S_AXI_ARADDR	=> s00_axi_araddr,
		S_AXI_ARPROT	=> s00_axi_arprot,
		S_AXI_ARVALID	=> s00_axi_arvalid,
		S_AXI_ARREADY	=> s00_axi_arready,
		S_AXI_RDATA	=> s00_axi_rdata,
		S_AXI_RRESP	=> s00_axi_rresp,
		S_AXI_RVALID	=> s00_axi_rvalid,
		S_AXI_RREADY	=> s00_axi_rready
	);

	-- Add user logic here

	-- User logic ends

end arch_imp;
