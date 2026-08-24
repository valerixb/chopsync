# Sentinel file to track whether setup has been run
SETUP_SENTINEL := .setup_done
SETUP_SCRIPT   := /xilinxworks/ZCU106/v2025.2/chopsync/sdk-linux/environment-setup-cortexa72-cortexa53-amd-linux

OBJ_LOCAL = can.o server.o
TARGET = chopsync-scpi-serv
SYSROOT_PATH = /xilinxworks/ZCU106/v2025.2/chopsync/sdk-linux/sysroots/cortexa72-cortexa53-amd-linux

CC = /tools/Xilinx/2025.2/Vitis/gnu/aarch64/lin/aarch64-linux/bin/aarch64-linux-gnu-gcc
CFLAGS = -O0 -g3 -Wall -I../common \
         --sysroot=$(SYSROOT_PATH) \
         -I$(SYSROOT_PATH)/usr/include
LDFLAGS = -Wall \
          --sysroot=$(SYSROOT_PATH) \
          -L$(SYSROOT_PATH)/usr/lib \
          -lm
OBJ_DIR = ./obj
_OBJ = $(patsubst %,$(OBJ_DIR)/%,$(OBJ_LOCAL))

DEP=$(_OBJ:%.o=%.d)
-include $(DEP)

.PHONY: all
all: $(SETUP_SENTINEL) bindir $(TARGET)
default: all

# Run setup script once; create sentinel file on success
# sources the script and captures all exported variables into .setup_env. 
# This is necessary because each shell spawned by Make is independent; 
# the environment can't be inherited across recipe lines or targets.
$(SETUP_SENTINEL): $(SETUP_SCRIPT)
	@echo "Running setup..."
	@bash -c "source $(SETUP_SCRIPT) && export -p" \
		| grep -v 'BASH_FUNC\|LS_COLORS\|TERMCAP' \
		> .setup_env
	@touch $@

bindir:
	@mkdir -p $(OBJ_DIR)

$(_OBJ): $(OBJ_DIR)/%.o: %.c $(SETUP_SENTINEL)
	@env -i bash -c "source .setup_env && $(CC) $(CFLAGS) -MMD -c $< -o $@"

$(TARGET): $(_OBJ)
	@env -i bash -c "source .setup_env && $(CC) $^ $(LDFLAGS) -o $@"
	# rm $^

.PHONY: clean
clean:
	-rm -rf $(OBJ_DIR)
	-rm -f $(TARGET)
	-rm -f $(SETUP_SENTINEL) .setup_env
	
