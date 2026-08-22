.SUFFIXES:

ifeq ($(strip $(DEVKITARM)),)
$(error "Please set DEVKITARM in your environment")
endif

export TOPDIR ?= $(CURDIR)
include $(DEVKITARM)/3ds_rules

CTRPFLIB ?= $(DEVKITPRO)/libctrpf
TARGET   := Pokebot3DSBridge
BUILD    := build
SOURCES  := Sources
INCLUDES := Includes
PSF      := Pokebot3DSBridge.plgInfo

ARCH     := -march=armv6k -mtune=mpcore -mfloat-abi=hard -mtp=soft
CFLAGS   := -O2 -mword-relocations -ffunction-sections -fdata-sections \
            -fno-strict-aliasing -fomit-frame-pointer $(ARCH)
CFLAGS   += $(INCLUDE) -D__3DS__
CXXFLAGS := $(CFLAGS) -fno-rtti -fno-exceptions -std=gnu++11
ASFLAGS  := $(ARCH)
LDFLAGS  := -T $(TOPDIR)/3gx.ld $(ARCH) -Os \
            -Wl,--gc-sections,--section-start,.text=0x07000100
LIBS     := -lctrpf -lctru -lm
LIBDIRS  := $(CTRPFLIB) $(CTRULIB) $(PORTLIBS)

ifneq ($(BUILD),$(notdir $(CURDIR)))

export OUTPUT   := $(TOPDIR)/$(TARGET)
export VPATH    := $(foreach dir,$(SOURCES),$(TOPDIR)/$(dir))
export DEPSDIR  := $(TOPDIR)/$(BUILD)

CPPFILES := $(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.cpp)))
CFILES   := $(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.c)))
SFILES   := $(foreach dir,$(SOURCES),$(notdir $(wildcard $(dir)/*.s)))

export LD       := $(CXX)
export OFILES   := $(CPPFILES:.cpp=.o) $(CFILES:.c=.o) $(SFILES:.s=.o)
export INCLUDE  := $(foreach dir,$(INCLUDES),-I$(TOPDIR)/$(dir)) \
                   -I$(CTRPFLIB)/include \
                   -I$(CTRPFLIB)/include/CTRPluginFramework \
                   $(foreach dir,$(CTRULIB) $(PORTLIBS),-I$(dir)/include) \
                   -I$(TOPDIR)/$(BUILD)
export LIBPATHS := $(foreach dir,$(LIBDIRS),-L$(dir)/lib)

.PHONY: all clean $(BUILD)

all: $(TARGET).3gx

$(TARGET).3gx: $(BUILD)

$(BUILD):
	@[ -d $@ ] || mkdir -p $@
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(TOPDIR)/Makefile

clean:
	@rm -rf $(BUILD) $(TARGET).elf $(TARGET).3gx

else

DEPENDS := $(OFILES:.o=.d)

$(OUTPUT).3gx: $(OUTPUT).elf
	@echo creating $(notdir $@)
	@3gxtool -s $< $(TOPDIR)/$(PSF) $@

$(OUTPUT).elf: $(OFILES)

-include $(DEPENDS)

endif
