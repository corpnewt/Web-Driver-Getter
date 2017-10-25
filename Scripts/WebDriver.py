import plistlib
import sys
import os
import time
import Downloader
import subprocess
# Python-aware urllib stuff
if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

class WebDriver:

    def __init__(self):
        self.dl = Downloader.Downloader()
        if os.path.exists("/System/Library/Extensions/NVDAStartupWeb.kext"):
            self.wd_loc = "/System/Library/Extensions/NVDAStartupWeb.kext"
        elif os.path.exists("/Library/Extensions/NVDAStartupWeb.kext"):
            self.wd_loc = "/Library/Extensions/NVDAStartupWeb.kext"
        else:
            self.wd_loc = None
        self.web_drivers = None
        self.os_build_number = None
        self.os_number = None
        self.installed_version = "Not Installed!"

        self.get_manifest()
        self.get_system_info()

    def _get_output(self, comm):
        try:
            p = subprocess.Popen(comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            c = p.communicate()
            if not p.returncode == 0:
                return c[1].decode("utf-8")
            return c[0].decode("utf-8")
        except:
            return c[1].decode("utf-8")

    # Helper methods
    def grab(self, prompt):
        if sys.version_info >= (3, 0):
            return input(prompt)
        else:
            return str(raw_input(prompt))

    # Header drawing method
    def head(self, text = "Web Driver Updater", width = 50):
        os.system("clear")
        print("  {}".format("#"*width))
        mid_len = int(round(width/2-len(text)/2)-2)
        middle = " #{}{}{}#".format(" "*mid_len, text, " "*((width - mid_len - len(text))-2))
        print(middle)
        print("#"*width)

    def custom_quit(self):
        self.head("Web Driver Updater")
        print("by CorpNewt\n")
        print("Thanks for testing it out, for bugs/comments/complaints")
        print("send me a message on Reddit, or check out my GitHub:\n")
        print("www.reddit.com/u/corpnewt")
        print("www.github.com/corpnewt\n")
        print("Have a nice day/night!\n\n")
        exit(0)

    def get_manifest(self):
        self.head("Retrieving Manifest...")
        print(" ")
        print("Retrieving manifest from \"https://gfe.nvidia.com/mac-update\"...")
        plist_data = self.dl.get_bytes("https://gfe.nvidia.com/mac-update")
        if not plist_data or not len(str(plist_data)):
            print("Looks like that site isn't responding!  Please check your intenet connection and try again.")
            time.sleep(5)
            custom_quit()
        if sys.version_info >= (3, 0):
            self.web_drivers = plistlib.loads(plist_data)
        else:
            self.web_drivers = plistlib.readPlistFromString(plist_data)

    def get_system_info(self):
        self.installed_version = "Not Installed!"
        self.os_build_number = self._get_output(["sw_vers", "-buildVersion"]).strip()
        self.os_number       = self._get_output(["sw_vers", "-productVersion"]).strip()
        if self.wd_loc:
            info_plist = plistlib.readPlist(self.wd_loc + "/Contents/Info.plist")            
            self.installed_version = info_plist["CFBundleGetInfoString"].split(" ")[-1].replace("(", "").replace(")", "")

    def check_dir(self, build):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("../")
        if not os.path.exists("Web Drivers"):
            os.mkdir("Web Drivers")
        os.chdir("Web Drivers")
        if not os.path.exists(build):
            os.mkdir(build)
        os.chdir(build)
        return os.getcwd()

    def download_for_build(self, build):
        self.head("Downloading for " + build)
        print(" ")
        dl_update = None
        for update in self.web_drivers["updates"]:
            if update["OS"].lower() == build.lower():
                dl_update = update
                break 
        if not dl_update:
            print("There isn't a version available for that build number!")
            time.sleep(5)
            return
        print("Downloading " + dl_update["version"])
        print(" ")
        self.check_dir(build)
        dl_file = self.dl.stream_to_file(dl_update["downloadURL"], dl_update["downloadURL"].split("/")[-1])
        if dl_file:
            print(dl_file + " downloaded successfully!")
            time.sleep(5)

    def format_table(self, items, columns):
        max_length = 0
        current_row = 0
        row_list = [[]]
        cur_list = []
        msg = ""
        sorted_list = sorted(items)
        for key in sorted_list:
            entry = key
            if len(entry) > max_length:
                max_length = len(entry)
            row_list[len(row_list)-1].append(entry)
            if len(row_list[len(row_list)-1]) >= columns:
                row_list.append([])
                current_row += 1
        for row in row_list:
            for entry in row:
                entry = entry.ljust(max_length)
                msg += entry + "  "
            msg += "\n"
        return msg

    def build_list(self):
        # Print 8 columns
        self.head("Web Drivers By Build Number")
        print(" ")
        build_list = []
        for update in self.web_drivers["updates"]:
            build_list.append(update["OS"])
        
        print("Available Build Numbers:\n")
        builds = self.format_table(build_list, 8)
        print(builds)
        print("M. Main Menu")
        print("Q. Quit")
        print(" ")
        menu = self.grab("Please type a build number to download the web driver:  ")

        if not len(menu):
            self.build_list()

        if menu[:1].lower() == "m":
            return
        elif menu[:1].lower() == "q":
            self.custom_quit()

        for build in build_list:
            if build.lower() == menu.lower():
                self.download_for_build(build)
                return
        self.build_list()

    def main(self):

        self.head("Web Driver Updater")
        print(" ")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        print("OS Version:  {} - {}".format(self.os_number, self.os_build_number))
        print("WD Version:  " + self.installed_version)
        
        newest_version = "None for this build number!"
        for update in self.web_drivers["updates"]:
            if update["OS"].lower() == self.os_build_number.lower():
                newest_version = update["version"]
                break 

        if self.installed_version.lower() == newest_version.lower():
            print("Newest:      " + newest_version + " (Current)")
        else:
            print("Newest:      " + newest_version)
        
        print(" ")
        print("D. Download For Current")
        print("B. Download By Build Number")
        print("")
        print("Q. Quit")
        print(" ")

        menu = self.grab("Please make a selection:  ")

        if not len(menu):
            return

        if menu[:1].lower() == "q":
            self.custom_quit()
        elif menu[:1].lower() == "d":
            self.download_for_build(self.os_build_number)
        elif menu[:1].lower() == "b":
            self.build_list()
        
        return

wd = WebDriver()

while True:
    try:
        wd.main()
    except Exception as e:
        print(e)
        time.sleep(5)
