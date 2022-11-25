#!/usr/bin/env bash
source "../../collection/configs/$1"

function configBiosArgs() {
	echo "rp_bios_setting = $biosArgs" >../bios_setup/conf/rpBiosSetting.py
}

function install_bios() {

	taskdir=$(echo vd* | awk '{print $1}')# Setup the bios on RP Board (like wilsonCity, moroCity, ArcherCity)
	#1.copy bios_setup to your SUT
	mkdir /root/bios_setup
	cd /root/bios_setup/
	git clone http://renlefux:Welcome,7375@gitlab.devtools.intel.com/yzhao18/bios_setup.git

	#2.unzip it to /root/
	apt install unzip
	cd /root/bios_setup/installation/bios_commercial
	unzip pysvtools.xmlcli-1.5.8.zip -d /root

	#3.cd bios_setup/installation/bios
	cd /root/bios_setup/installation/bios_rp

	#4.chmod 777 install_for_rp_board.sh
	chmod 777 install_for_rp_board.sh
	#5.sed -i "s/\r//g" *.sh
	sed -i "s/\r//g" *.sh

	#6. ./install_for_rp_board.sh
	./install_for_rp_board.sh
	cd ..
	pip3 install -r requirements.txt

	#7. go to the bios_setup/conf.
	cd /root/bios_setup/conf

	#8. edit rp_bios_setting in the rpBiosSetting.py file based on your requirement.
	#(please make sure bios name is in the system.)
	echo "add bios name to rpBiosSetting.py"
	#9. cd bios_setup/testLibs
	cd /root/bios_setup/testLibs

	#10. run the setup bios command based:
	pytest testRpBiosSetting.py::Test_rpBiosSetting::test_rp_bios_setting
	#pytest testRpBiosSetting.py::Test_rpBiosSetting::test_save_xml -s

	#11. the SUT will be rebooted after running the command above.
	sudo reboot now
	#12. after the sut started, the bios is all set.
	# everying is ok!

	#12. To save the current SUT bios to a XML file, run the command:
	#pytest testRpBiosSetting.py::Test_rpBiosSetting::test_save_xml -s

	#13. To tranform a bios bin file to a xml file with bios key path, run the following commands:
	#pytest testRpBiosSetting.py::Test_rpBiosSetting::test_save_xml_bin --binfile yourbinFileFullPath

	#14. there is biosSettingExample in the conf folder for your reference.

}
configBiosArgs
#install_bios
