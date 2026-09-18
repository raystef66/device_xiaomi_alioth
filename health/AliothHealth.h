// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <health-impl/Health.h>

namespace aidl::android::hardware::health {
class AliothHealth : public Health {
  public:
    using Health::Health;
    ndk::ScopedAStatus getCurrentNowMicroamps(int32_t* out) override;
    ndk::ScopedAStatus getCurrentAverageMicroamps(int32_t* out) override;

  protected:
    void UpdateHealthInfo(HealthInfo* info) override;
};
}  // namespace aidl::android::hardware::health
