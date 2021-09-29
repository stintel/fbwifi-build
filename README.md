# fbwifi-build

A "wrapper repo" to build OpenWrt as needed for FBWifi devices.
Checks out the OpenWrt code at a specific revision, and applies any patches/feeds/etc as needed.

Prerequisites are the same as OpenWrt itself (see https://openwrt.org/docs/guide-developer/build-system/install-buildsystem)

To clone openwrt (at the correct revision) and prepare to build it targeting a particular device type:
```
python3 setup.py --clone --target tplink_re200-v4
```

After that, to switch to targeting another device type:
```
python3 setup.py --target comfast_cf-wr752ac-v1
```

Additional configurations are picked up from `config.yml`.

Once setup.py has successfully completed, you are ready to build OpenWrt:
```
cd openwrt
make -j $(nproc) defconfig clean world
```

Or, if you're like me and you want to make sure the build will keep running even if you log out, you can use [nohup](https://en.wikipedia.org/wiki/Nohup):
```
cd openwrt
rm -f nohup.out && nohup bash -c 'date >starttime ; make -j $(nproc) defconfig clean world ; date >endtime' &
```
