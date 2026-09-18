// SPDX-License-Identifier: Apache-2.0
#include "AliothHealth.h"
#include "Current.h"

namespace aidl::android::hardware::health {
ndk::ScopedAStatus AliothHealth::getCurrentNowMicroamps(int32_t* out) {
    auto status = Health::getCurrentNowMicroamps(out);
    if (!status.isOk()) return status;
    if (!alioth::health::ToAndroidCurrent(*out, out)) {
        return ndk::ScopedAStatus::fromServiceSpecificError(IHealth::STATUS_UNKNOWN);
    }
    return status;
}

ndk::ScopedAStatus AliothHealth::getCurrentAverageMicroamps(int32_t* out) {
    auto status = Health::getCurrentAverageMicroamps(out);
    if (!status.isOk()) return status;
    if (!alioth::health::ToAndroidCurrent(*out, out)) {
        return ndk::ScopedAStatus::fromServiceSpecificError(IHealth::STATUS_UNKNOWN);
    }
    return status;
}

void AliothHealth::UpdateHealthInfo(HealthInfo* info) {
    // The base returns raw sysfs fields each time, including callback updates.
    // Do not infer polarity from STATUS: net current can differ while plugged in.
    Health::UpdateHealthInfo(info);
    alioth::health::ToAndroidCurrent(info->batteryCurrentMicroamps,
                                    &info->batteryCurrentMicroamps);
    alioth::health::ToAndroidCurrent(info->batteryCurrentAverageMicroamps,
                                    &info->batteryCurrentAverageMicroamps);
}
}  // namespace aidl::android::hardware::health
