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

# Add our own custom feeds, and run scripts/feeds/update and scripts/feeds/install.
def update_feeds():
	try:
		print("### Updating feeds")
		feeds_conf_filepath = os.path.join(openwrt, "feeds.conf")
		print(f"Updating feed config at {feeds_conf_filepath}")
		shutil.copyfile(os.path.join(openwrt, "feeds.conf.default"), feeds_conf_filepath)
		with open(feeds_conf_filepath, "a") as feeds_conf_file:
			feeds_conf_file.write("src-git fbc https://github.com/facebookincubator/fbc_owrt_feed.git^b67be64f5086df4ace5f2c550d8abae5f8951be2\n")

		os.chdir(openwrt)
		scripts_feeds_path = os.path.join(".", "scripts", "feeds")
		print(f"Calling {scripts_feeds_path} update -a")
		os.system(f"{scripts_feeds_path} update -a");
		print(f"Calling {scripts_feeds_path} install -a")
		os.system(f"{scripts_feeds_path} install -a");

		print("### Updating feeds done")
	except:
		print("### Updating feeds failed")
		sys.exit(1)
	finally:
		os.chdir(base_dir)

def apply_patches():
	try:
		print("### Applying patches")
		patches = []

		folder = config.get("patches_folder")
		if not folder:
			print("Missing patches_folder within config file")
			sys.exit(1)
		patch_folder = base_dir / folder
		if not patch_folder.is_dir():
			print(f"Patch folder {patch_folder} not found")
			sys.exit(-1)

		print(f"Applying patches from {patch_folder}")

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
		print("### Applying patches failed")
		sys.exit(1)
	finally:
		os.chdir(base_dir)

# Add files to the OpenWrt build, using
# https://openwrt.org/docs/guide-developer/build-system/use-buildsystem#custom_files
def add_files():
	try:
		print("### Adding files")

		folder = config.get("additions_folder")
		if not folder:
			print("Missing additions_folder within config file")
			sys.exit(1)
		additions_folder = base_dir / folder
		if not additions_folder.is_dir():
			print(f"Additions folder {additions_folder} not found")
			sys.exit(-1)

		print(f"Adding files from {additions_folder}")
		os.chdir(openwrt)
		shutil.rmtree("files", ignore_errors=True)
		shutil.copytree(additions_folder, "files")
		os.chdir(base_dir)
		build_info_filepath = os.path.join(openwrt, "files", "fbwifi-build-info")
		os.system("git show --no-patch >" + build_info_filepath)
		print("### Adding files done")
	except:
		print("### Adding files failed")
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
update_feeds()
apply_patches()
add_files()
shutil.copyfile(targetconfig_file, os.path.join(openwrt, ".config"))
