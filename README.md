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

References:
- https://openwrt.org/docs/guide-developer/build-system/use-buildsystem

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

## Updating the OpenWrt image on the target device

References:
- https://openwrt.org/docs/guide-user/installation/sysupgrade.cli 
- https://openwrt.org/docs/techref/sysupgrade 

*Assuming your target device is already running some version of OpenWrt*, you can install your newly built system image as follows:

On your build machine, cd into the directory containing the output files (e.g., `openwrt/bin/targets/ath79/generic/`) and scp the `sha256sums` and `openwrt-*-squashfs-sysupgrade.bin` files to your target device's `/tmp` directory.

Then ssh into your target device and run the following commands (as root):
```
cd /tmp
sha256sum openwrt-*-squashfs-sysupgrade.bin
grep sysupgrade sha256sums 
#  ensure the two values are the same
sysupgrade -n -v openwrt-*-squashfs-sysupgrade.bin
```

The sysupgrade process may take up to 5 minutes or so, and the device should be up and running the new code without further intervention (no need for additional power cycle, etc.).

Once it is up and running again, if you ssh into the target device and view contents of the `/fbwifi-build-info` file, you'll see the commit hash at which this system image was built.
