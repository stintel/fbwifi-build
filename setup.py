#!/usr/bin/env python3

from pathlib import Path
from subprocess import run
import os
import shutil
import sys
import yaml
import getopt

def clone_tree():
	try:
		makefile = openwrt +"/Makefile"
		if Path(makefile).is_file():
			print("### OpenWrt checkout is already present. Please remove it, or run without --clone")
			sys.exit(-1)

		print("### Cloning tree")
		Path(openwrt).mkdir(exist_ok=True, parents=True)
		if git_ref != "":
			run(["git", "clone", "--reference", git_ref, config["repo"], openwrt], check=True)
		else:
			run(["git", "clone", config["repo"], openwrt], check=True)
		print("### Clone done")
	except:
		print("### Cloning the tree failed")
		sys.exit(1)

def fetch_tree():
	try:
		makefile = openwrt +"/Makefile"
		if not Path(makefile).is_file():
			print("### OpenWrt checkout is not present. Please run --clone")
			sys.exit(-1)

		print("### Fetch tree")
		os.chdir(openwrt)
		run(["git", "fetch"], check=True)
		print("### Fetch done")
	except:
		print("### Fetching the tree failed")
		sys.exit(1)
	finally:
		os.chdir(base_dir)

def reset_tree():
	try:
		print("### Resetting tree")
		os.chdir(openwrt)
		run(
			["git", "checkout", config["branch"]], check=True,
		)
		run(
			["git", "reset", "--hard", config.get("revision", config["branch"])],
			check=True,
		)
		run(
			["rm", "-r", "profiles"],
		)
		print("### Reset done")
	except:
		print("### Resetting tree failed")
		sys.exit(1)
	finally:
		os.chdir(base_dir)

def setup_tree():
	try:
		print("### Applying patches")

		patches = []
		for folder in config.get("patch_folders", []):
			patch_folder = base_dir / folder
			if not patch_folder.is_dir():
				print(f"Patch folder {patch_folder} not found")
				sys.exit(-1)

			print(f"Adding patches from {patch_folder}")

			patches.extend(
				sorted(list((base_dir / folder).glob("*.patch")), key=os.path.basename)
		)

		print(f"Found {len(patches)} patches")

		os.chdir(openwrt)

		for patch in patches:
			run(["git", "am", "-3", str(base_dir / patch)], check=True)
		run(
			["ln", "-s", profiles, "profiles"], check=True,
		)
		print("### Patches done")
	except:
		print("### Setting up the tree failed")
		sys.exit(1)
	finally:
		os.chdir(base_dir)


base_dir = Path.cwd().absolute()
clone = False
config = "config.yml"
target = None
profiles = "../profiles"
openwrt = "openwrt"
git_ref = ""

try:
	opts, args = getopt.getopt(sys.argv[1:], "", ["clone", "config=", "target=", "reference=" ])
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)


for o, a in opts:
	if o in ("--clone"):
		clone = True
	elif o in ("--config"):
		config = a
	elif o in ("--reference"):
		git_ref = a
	elif o in ("--target"):
		target = a
	else:
		assert False, "unhandled option"

if not Path(config).is_file():
	print(f"Missing {config}")
	sys.exit(1)
config = yaml.safe_load(open(config))

if not target:
	print("Missing --target option")
	sys.exit(1)
targetconfig_folder = config.get("targetconfig_folder")
if not targetconfig_folder:
	print("Missing targetconfig_folder within config file")
	sys.exit(1)
if not Path(targetconfig_folder).is_dir():
	print(f"Missing targetconfig_folder {targetconfig_folder}")
	sys.exit(1)
targetconfig_file = os.path.join(targetconfig_folder, target)
if not Path(targetconfig_file).is_file():
	print(f"Missing targetconfig_file {targetconfig_file}")
	sys.exit(1)

if clone:
	clone_tree()
else:
	fetch_tree()
reset_tree()
setup_tree()
shutil.copyfile(targetconfig_file, os.path.join(openwrt, ".config"))

print("")
print("Ready to build!  Run the following:")
print(f"  cd {openwrt}")
print("  make -j $(nproc) defconfig clean world")
