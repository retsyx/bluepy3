BLUEZ_VERSION=5.70

BLUEZ_PATH=/tmp/bluez-$(BLUEZ_VERSION)

BLUEZ_SRCS  = lib/bluetooth.c lib/hci.c lib/sdp.c lib/uuid.c
BLUEZ_SRCS += attrib/att.c attrib/gatt.c attrib/gattrib.c attrib/utils.c
BLUEZ_SRCS += btio/btio.c src/log.c src/shared/mgmt.c
BLUEZ_SRCS += src/shared/crypto.c src/shared/att.c src/shared/queue.c src/shared/util.c
BLUEZ_SRCS += src/shared/io-glib.c src/shared/timeout-glib.c
BLUEZ_SRCS += src/shared/log.c
BLUEZ_SRCS += src/shared/gatt-client.c src/shared/gatt-db.c src/shared/gatt-helpers.c

IMPORT_SRCS = $(addprefix $(BLUEZ_PATH)/, $(BLUEZ_SRCS))
LOCAL_SRCS  = bluepy3-helper.c

CC ?= gcc
CFLAGS += -g -Wall # -Werror

CPPFLAGS += -DHAVE_CONFIG_H
ifneq ($(DEBUGGING),)
CFLAGS += -DBLUEPY_DEBUG=1 -O0
else
CFLAGS += -Os
endif

CPPFLAGS += -I$(BLUEZ_PATH)/attrib -I$(BLUEZ_PATH) -I$(BLUEZ_PATH)/lib -I$(BLUEZ_PATH)/src -I$(BLUEZ_PATH)/gdbus -I$(BLUEZ_PATH)/btio -I$(BLUEZ_PATH)/sys

CPPFLAGS += $(shell pkg-config glib-2.0 --cflags)
LDLIBS += $(shell pkg-config glib-2.0 --libs)

.PHONY: clone-srcs

all: bluepy3-helper

bluepy3-helper: $(LOCAL_SRCS) clone-srcs
	$(CC) -L. $(CFLAGS) $(CPPFLAGS) -o $@ $(LOCAL_SRCS) $(IMPORT_SRCS) $(LDLIBS)

clone-srcs:
	git -c advice.detachedHead=false clone --depth 1 --branch $(BLUEZ_VERSION) https://github.com/bluez/bluez.git $(BLUEZ_PATH)
	sed 's|BLUEPY3_BLUEZ_VERSION|$(BLUEZ_VERSION)|g' config.x.h > $(BLUEZ_PATH)/config.h

GET_SERVICES=get_services.py

uuids.json: $(GET_SERVICES)
	python $(GET_SERVICES) > uuids.json

TAGS: *.c $(BLUEZ_PATH)/attrib/*.[ch] $(BLUEZ_PATH)/btio/*.[ch]
	etags $^

clean:
	rm -rf *.o bluepy3-helper TAGS $(BLUEZ_PATH)
