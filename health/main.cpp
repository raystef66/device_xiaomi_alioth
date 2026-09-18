// SPDX-License-Identifier: Apache-2.0
#define LOG_TAG "android.hardware.health-service.alioth"

#include <android-base/logging.h>
#include <android/binder_interface_utils.h>
#include <health/utils.h>
#include <health-impl/ChargerUtils.h>
#include <health-impl/HalHealthLoop.h>
#include <unistd.h>

#include <fstream>
#include <memory>
#include <string_view>

#include "AliothHealth.h"

using aidl::android::hardware::health::AliothHealth;
using aidl::android::hardware::health::HalHealthLoop;
using aidl::android::hardware::health::Health;

#if !CHARGER_FORCE_NO_UI
using aidl::android::hardware::health::charger::ChargerCallback;
using aidl::android::hardware::health::charger::ChargerModeMain;
class AliothChargerCallback final : public ChargerCallback {
  public:
    explicit AliothChargerCallback(const std::shared_ptr<Health>& service)
        : ChargerCallback(service) {}
    bool ChargerEnableSuspend() override { return true; }
};
#endif

int main(int argc, char** argv) {
#ifdef __ANDROID_RECOVERY__
    android::base::InitLogging(argv, android::base::KernelLogger);
#endif
    // Keep the QTI service's bounded probe wait; never depend on a fake SOC.
    for (unsigned int attempt = 0; attempt < 100; ++attempt) {
        int capacity;
        std::ifstream input("/sys/class/power_supply/battery/capacity");
        if (input >> capacity) break;
        usleep(100000);
    }

    auto config = std::make_unique<healthd_config>();
    ::android::hardware::health::InitHealthdConfig(config.get());
    config->batteryCurrentNowPath = "/sys/class/power_supply/bms/current_now";
    config->batteryCurrentAvgPath = "/sys/class/power_supply/bms/current_avg";
    auto service = ndk::SharedRefBase::make<AliothHealth>("default", std::move(config));

    if (argc >= 2 && std::string_view(argv[1]) == "--charger") {
#if !CHARGER_FORCE_NO_UI
        return ChargerModeMain(service, std::make_shared<AliothChargerCallback>(service));
#endif
    }
    return std::make_shared<HalHealthLoop>(service, service)->StartLoop();
}
