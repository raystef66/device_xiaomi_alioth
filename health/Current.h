// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <cstdint>
#include <limits>

namespace alioth::health {
// Qualcomm FG uses positive discharge current. Android requires positive input.
// Zero is the HealthInfo unavailable value; a direct getter also returns an error.
inline bool ToAndroidCurrent(int32_t raw, int32_t* value) {
    if (raw == std::numeric_limits<int32_t>::min()) {
        *value = 0;
        return false;
    }
    *value = -raw;
    return true;
}
}  // namespace alioth::health
