# fbwifi-build

To clone openwrt (at the correct revision) and prepare to build it targeting a particular device type:
```
python3 setup.py --clone --target tplink_re200-v4
```

After that, to switch to targeting another device type:
```
python3 setup.py --target comfast_cf-wr752ac-v1
```

Additional configurations are picked up from `config.yml`.
