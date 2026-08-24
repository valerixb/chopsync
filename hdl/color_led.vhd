----------------------------------------------------------------------------------
--  
-- Bi-Color LED driver for frequency/phase lock indication 
-- 
-- latest rev: sept 20 2022
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity color_led is
    Port ( clk       : in STD_LOGIC;
           reset     : in STD_LOGIC;
           f_lock    : in STD_LOGIC;
           ph_lock   : in STD_LOGIC;
           RED_LED   : out STD_LOGIC;
           GREEN_LED : out STD_LOGIC);
end color_led;

architecture Behavioral of color_led is

begin

    main_process : process (clk, reset)
        begin
        if reset = '1' then
            RED_LED   <= '0';
            GREEN_LED <= '0';
        elsif rising_edge(clk) then
            RED_LED   <= f_lock nand ph_lock;
            GREEN_LED <= f_lock or ph_lock;
        end if;
    end process main_process;

end Behavioral;
