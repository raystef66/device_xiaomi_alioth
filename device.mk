#
# Copyright (C) 2021 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# A/B
TARGET_IS_VAB := true

# Inherit from sm8250-common
$(call inherit-product, device/xiaomi/sm8250-common/kona.mk)

# AAPT
PRODUCT_AAPT_CONFIG := normal
PRODUCT_AAPT_PREF_CONFIG := xxhdpi

# Audio configs
PRODUCT_COPY_FILES += \
    $(call find-copy-subdir-files,*,$(LOCAL_PATH)/audio/,$(TARGET_COPY_OUT_VENDOR)/etc)

# Boot animation
TARGET_SCREEN_HEIGHT := 2400
TARGET_SCREEN_WIDTH := 1080

# Camera
PRODUCT_PACKAGES += \
    libpiex_shim

# Display Config
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/display/display_id_4630946736638489729.xml:$(TARGET_COPY_OUT_VENDOR)/etc/displayconfig/display_id_4630946736638489729.xml

# Health: device-local Android polarity conversion; QTI kernel ABI is unchanged.
PRODUCT_PACKAGES += \
    android.hardware.health-service.alioth \
    android.hardware.health-service.alioth_recovery

# Init
$(call soong_config_set,xiaomi_kona,variant_lib,//$(LOCAL_PATH):libvariant_xiaomi_alioth)

# Miui Camera
include device/xiaomi/camera/miuicamera.mk

# Miui Camera STLicense
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/camera/st_license.lic:$(TARGET_COPY_OUT_VENDOR)/etc/camera/st_license.lic

# Overlays
PRODUCT_PACKAGES += \
    FrameworkResOverlayDevice \
    LineageSettingsOverlayDevice \
    LineageSystemUIOverlayDevice \
    SystemUIOverlayDevice

# This product includes MiuiCamera, which replaces Aperture.
# Keep the Lineage Dialer overlay only for the non-GMS communications suite.
ifneq ($(WITH_GMS_COMMS_SUITE),true)
PRODUCT_PACKAGES += \
    LineageDialerOverlayDevice
endif

# Shipping API level
PRODUCT_SHIPPING_API_LEVEL := 30

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(LOCAL_PATH)

# Inherit from vendor blobs
$(call inherit-product, vendor/xiaomi/alioth/alioth-vendor.mk)
