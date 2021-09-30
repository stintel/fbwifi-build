# fbwifi-build

A "wrapper repo" to build OpenWrt and install our custom packages/scripts, as needed for FBWifi devices.
Checks out the OpenWrt code at a specific revision, and applies any patches/feeds/etc as needed.

## Prerequisites

Prerequisites are the same as OpenWrt itself (see https://openwrt.org/docs/guide-developer/build-system/install-buildsystem)

## Running setup.py

You'll need to run `setup.py` to download all the source code and configure things properly, and then `make` to actually execute the build.

The first time you run `setup.py`, you need to include the `--clone` option (to clone the OpenWrt source tree and check it out as of the appropriate commit hash).

Every time you run `setup.py`, you need to include `--target <plaform>` so the script knows what platform to configure your build for.  (There must be a matching file within the [deviceconfigs](https://github.com/epoger/fbwifi-build/tree/main/deviceconfigs) folder.)

For example, the first time you might run:
```
python3 setup.py --clone --target tplink_re200-v4
```

After that, to switch to targeting another device type:
```
python3 setup.py --target comfast_cf-wr752ac-v1
```

See [setup.py](https://github.com/epoger/fbwifi-build/blob/main/setup.py) and [config.yml](https://github.com/epoger/fbwifi-build/blob/main/config.yml) for other settings you can tweak.

## Building OpenWrt

Once setup.py has successfully completed, you are ready to build OpenWrt.  The resulting flash image will include OpenWrt along with our custom packages and boot scripts.

```
cd openwrt
make -j $(nproc) defconfig clean world
```

Note that the build can take a while.  If you want to make sure the build will keep running even if you log out, you can use [nohup](https://en.wikipedia.org/wiki/Nohup):
```
cd openwrt
rm -f nohup.out && nohup bash -c 'date >starttime ; make -j $(nproc) defconfig clean world ; date >endtime' &
```

Once the build is complete, you will find the output files in (e.g.) `openwrt/bin/targets/ath79/generic/`
