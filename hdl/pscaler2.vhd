--
-- prescaler outside the default 125 MHz clock domain
-- made to provide a gated but not resampled TRIG_OUT signal
--
-- latest rev mar 18 2024
--


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity pscaler2 is
  Port(
    clk         :  in std_logic;
    reset       :  in std_logic;
    sc_fact     :  in std_logic_vector(15 downto 0);
    trig_ph     :  in std_logic_vector(15 downto 0);
    pulse_in    :  in std_logic;
    pulse_out   : out std_logic;
    trig_out    : out std_logic
    );
end pscaler2;

architecture Behavioral of pscaler2 is

    signal pipe1        : std_logic_vector(2 downto 0);
    attribute ASYNC_REG : string;
      attribute ASYNC_REG of pipe1 : signal is "TRUE";
    signal pulse_in_s, pulse_dly   : std_logic;
    subtype DIVIDER_TYPE is unsigned(15 downto 0);
    signal intcount     : DIVIDER_TYPE;
    signal pout_gate, trigout_gate : std_logic;

  function INRANGE(val, minv, maxv: DIVIDER_TYPE) return DIVIDER_TYPE is
      variable tv : DIVIDER_TYPE;
    begin
      if(val>minv) then
        tv:=val;
      else
        tv:=minv;
      end if;
      if(tv>maxv) then
        tv:=maxv;
      end if;
      return tv;
    end; 

begin

  -- synchronize pulse in to our clock
  sync_pulse: process(clk, reset)
    begin
      if rising_edge(clk) then
        if(reset='1') then
          pipe1 <= (others=>'0');
          pulse_in_s <= '0';
        else
          pipe1 <= pipe1(1 downto 0) & pulse_in;
          pulse_in_s <= pipe1(2);
        end if;  -- if not reset
      end if;  -- if clock edge
    end process sync_pulse;


  delayed_sig: process(clk, reset)
    begin
      if rising_edge(clk) then
        if(reset='1') then
          pulse_dly <= '0';
        else
          pulse_dly <= pulse_in_s;
        end if;  -- if not reset
      end if;  -- if clock edge
    end process delayed_sig;


  -- scale down
  main_proc: process(clk, reset)
    begin
      if rising_edge(clk) then
        if(reset='1') then
          intcount <= to_unsigned(1,16);
          pout_gate <= '0';
          trigout_gate <= '0';
        else
          -- if FALLING edge of PULSE_IN
          if( pulse_in_s = '0' and pulse_dly = '1' ) then
            
            -- output pulse + counter increment
            if(intcount=(unsigned(sc_fact))) then
              intcount <= to_unsigned(1,16);
              pout_gate <= '1';
            else
              intcount <= intcount+1;
              pout_gate <= '0';
            end if;

            -- trig out
            if(intcount=INRANGE(unsigned(trig_ph),to_unsigned(1,16),unsigned(sc_fact))) then
              trigout_gate <= '1';
            else
              trigout_gate <= '0';
            end if;
          end if;  -- if PULSE_IN falling edge
                    
        end if;  -- if not reset
      end if;  -- if clock edge
    end process main_proc;

  
  -- gate 
  pulse_out <= pulse_in and pout_gate;
  trig_out  <= pulse_in and trigout_gate;
    
end Behavioral;
