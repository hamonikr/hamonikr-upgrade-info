#!/usr/bin/python3

import os, sys, apt, tempfile, gettext
import subprocess
import logging, syslog

# ~/.hamonikr/log/FILENAME.log 형식으로 로그파일 동적 생성
user_home = os.path.expanduser("~")
log_dir = os.path.join(user_home, ".hamonikr/log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, os.path.basename(__file__) + ".log")
logging.basicConfig(filename=log_file, level=logging.DEBUG)

gettext.install("mintupdate", "/usr/share/locale")

if os.getuid() != 0:
    logging.error("Run this code as root!")  # 로깅 추가
    print("Run this code as root!")
    sys.exit(1)

if len(sys.argv) != 3:
    logging.error("Missing arguments!")  # 로깅 추가
    print("Missing arguments!")
    sys.exit(1)

codename = sys.argv[1]
window_id = int(sys.argv[2])
sources_list = "/usr/share/hamonikr-upgrade-info/%s/official-package-repositories.list" % codename
sources_list2 = "/usr/share/hamonikr-upgrade-info/%s/hamonikr.list" % codename
# sources_list3 = "/usr/share/hamonikr-upgrade-info/%s/hamonikr-pkg.list" % codename
blacklist_filename = "/usr/share/hamonikr-upgrade-info/%s/blacklist" % codename
additions_filename = "/usr/share/hamonikr-upgrade-info/%s/additions" % codename
removals_filename = "/usr/share/hamonikr-upgrade-info/%s/removals" % codename
preremovals_filename = "/usr/share/hamonikr-upgrade-info/%s/preremovals" % codename

if not os.path.exists(sources_list):
    print("Unrecognized release: %s" % codename)
    sys.exit(1)


def install_packages(packages):
    if len(packages) > 0:
        cmd = ["sudo", "/usr/sbin/synaptic", "--hide-main-window", "--non-interactive", "--parent-window-id", "%s" % window_id, "-o", "Synaptic::closeZvt=true"]
        f = tempfile.NamedTemporaryFile()
        for package in packages:
            pkg_line = "%s\tinstall\n" % package
            f.write(pkg_line.encode("utf-8"))
        cmd.append("--set-selections-file")
        cmd.append("%s" % f.name)
        f.flush()
        try:
            subprocess.run(cmd)
            logging.info("install cmd string : %s" % ' '.join(cmd))
        except Exception as e:
            logging.exception("Exception occurred: {}".format(e))

def remove_packages(packages):
    if len(packages) > 0:
        cmd = ["sudo", "/usr/sbin/synaptic", "--hide-main-window", "--non-interactive", "--parent-window-id", "%s" % window_id, "-o", "Synaptic::closeZvt=true"]
        f = tempfile.NamedTemporaryFile()
        for package in packages:
            pkg_line = "%s\tdeinstall\n" % package
            f.write(pkg_line.encode("utf-8"))
        cmd.append("--set-selections-file")
        cmd.append("%s" % f.name)
        f.flush()
        try:
            subprocess.run(cmd)
            logging.info("remove cmd string : %s" % ' '.join(cmd))
        except Exception as e:
            logging.exception("Exception occurred: {}".format(e))
        
def purge_packages(packages):
    if len(packages) > 0:
        cmd = ["sudo", "/usr/sbin/synaptic", "--hide-main-window", "--non-interactive", "--parent-window-id", "%s" % window_id, "-o", "Synaptic::closeZvt=true"]
        f = tempfile.NamedTemporaryFile()
        for package in packages:
            pkg_line = "%s\tpurge\n" % package
            f.write(pkg_line.encode("utf-8"))
        cmd.append("--set-selections-file")
        cmd.append("%s" % f.name)
        f.flush()
        try:
            subprocess.run(cmd)
            logging.info("purge cmd string : %s" % ' '.join(cmd))
        except Exception as e:
            logging.exception("Exception occurred: {}".format(e))
        
def file_to_list(filename):
    returned_list = []
    if os.path.exists(filename):
        with open(filename, 'r') as file_handle:
            for line in file_handle:
                line = line.strip()
                if line == "" or line.startswith("#"):
                    continue
                returned_list.append(line)
    return returned_list

# STEP 0.5 : PRE REMOVE PACKAGE (depends probrem)
# 저장소를 바꾸기 전에 이 과정을 해야 함

removals = file_to_list(preremovals_filename)
# purge_packages(removals)
try:
    purge_packages(removals)
except Exception as e:
    logging.exception("Exception occurred: {}".format(e))

# STEP 1: UPDATE APT SOURCES
#---------------------------
if os.path.exists("/etc/apt/sources.list.d/official-source-repositories.list"):
    subprocess.run(["rm", "-f", "/etc/apt/sources.list.d/official-source-repositories.list"])

if os.path.exists("/etc/apt/sources.list.d/hamonikr.list"):
    subprocess.run(["rm", "-f", "/etc/apt/sources.list.d/hamonikr.list"])

if os.path.exists("/etc/apt/sources.list.d/hamonikr-pkg.list"):
    subprocess.run(["rm", "-f", "/etc/apt/sources.list.d/hamonikr-pkg.list"])

subprocess.run(["cp", sources_list, "/etc/apt/sources.list.d/official-package-repositories.list"])
subprocess.run(["cp", sources_list2, "/etc/apt/sources.list.d/hamonikr.list"])
# subprocess.run(["cp", sources_list3, "/etc/apt/sources.list.d/hamonikr-pkg.list"])

# TO-DO
# 하모니카 6.0에서 사용하던 ppa 또는 직접 추가한 저장소 중 focal 코드명이 있는 경우 7.0에서는 jammy 환경으로 변경되어야 함

# STEP 2: UPDATE APT CACHE
#-------------------------

cache = apt.Cache()
# subprocess.run(["sudo", "/usr/sbin/synaptic", "--hide-main-window", "--update-at-startup", "--non-interactive", "--parent-window-id", "%d" % window_id])
try:
    cmd = ["sudo", "/usr/sbin/synaptic", "--hide-main-window", "--update-at-startup", "--non-interactive", "--parent-window-id", "%d" % window_id]
    subprocess.run(' '.join(cmd))
    logging.info("install cmd string : %s" % ' '.join(cmd))
except Exception as e:
    logging.exception("Exception occurred: {}".format(e))



# STEP 3: INSTALL MINT UPDATES
#--------------------------------

dist_upgrade = True

# Reopen the cache to reflect any updates
cache.open(None)
cache.upgrade(dist_upgrade)
changes = cache.get_changes()

blacklist = file_to_list(blacklist_filename)

packages = []
for pkg in changes:
    if (pkg.is_installed and pkg.marked_upgrade):
        package = pkg.name
        newVersion = pkg.candidate.version
        oldVersion = pkg.installed.version
        size = pkg.candidate.size
        sourcePackage = pkg.candidate.source_name
        short_description = pkg.candidate.raw_description
        description = pkg.candidate.description
        if sourcePackage not in blacklist:
            if (newVersion != oldVersion):
                update_type = "package"
                for origin in pkg.candidate.origins:
                    if origin.origin == "linuxmint" or origin.origin == "repo.hamonikr.org":
                        if origin.component != "romeo" and package != "linux-kernel-generic":
                            packages.append(package)

# install_packages(packages)

try:
    install_packages(packages)
except Exception as e:
    logging.exception("Exception occurred: {}".format(e))

# STEP 4: ADD PACKAGES
#---------------------

additions = file_to_list(additions_filename)
# install_packages(additions)

try:
    install_packages(packages)
except Exception as e:
    logging.exception("Exception occurred: {}".format(e))


# STEP 5: REMOVE PACKAGES
#------------------------

removals = file_to_list(removals_filename)
# remove_packages(removals)

try:
    remove_packages(removals)
except Exception as e:
    logging.exception("Exception occurred: {}".format(e))

# STEP 6: MAKE kumkangupdate.dummy FILE
# 7.0 업그레이드 시 해야하는 일이 있으면 이 파일로 체크해서 hamonikr-system 의 set-user-env 에서 수행
if not os.path.exists("/var/log/kumkangupdate.dummy"):
    subprocess.run(["touch", "/var/log/kumkangupdate.dummy"])

# STEP 7: UPDATE GRUB
#--------------------

try:
    subprocess.run(["update-grub"])
    if os.path.exists("/usr/share/ubuntu-system-adjustments/systemd/adjust-grub-title"):
        subprocess.run(["/usr/share/ubuntu-system-adjustments/systemd/adjust-grub-title"])
except Exception as detail:
    syslog.syslog("Couldn't update grub: %s" % detail)
