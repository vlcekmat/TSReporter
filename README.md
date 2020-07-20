# TSreporter

## For users

### What is TSReporter
TSReporter is a utility tool that helps automate the process between making a screenshot in the game and inputing the information into Mantis. 

### How to install and set up
Just copy the folder containing this README onto your computer. When you first launch it, it will run setup. You will have to input some paths to relevant folders.

1. Trunk
For TSReporter to be able to find your current trunk revision, your trunk directory must be structured accordingly:

Trunk<br/>
+--ATS<br/>
+--ETS2

Trunk is the directory you select, it can be named anything. However, the game subdirectories MUST be named ATS and ETS2. This is to avoid ambiguity, where some people have an ATS_old and ATS_new.

If you only use one Trunk game, that's okay. However, if you have the games in different directories, it will crash! If you have multiple trunk versions of the same game and you report from any of them, it will report from the CURENT of the game selected here.

Trunk_1<br/>
+--ATS<br/>
Trunk_2<br/>
+--ETS2<br/>
WILL CRASH!

2. Documents
Your documents directory is the one where the games automatically save files. 

Documents<br/>
+--American Truck Simulator<br/>
|	+--bugs.txt<br/>
|	+--game.log.txt<br/>
+--Euro Truck Simulator<br/>
|	+--bugs.txt<br/>
|	+--game_log.txt

3. Edited images
This is the folder where you save your edited images. They must be saved directly here, so if you have different folders for different games/dlcs/time periods, you will have to change it to the one where you want to program to get the images from, otherwise it won't find them! (you can just also them manually)

4. Mantis username
What you use to log into Mantis. It is necessary because the session handler needs to log in every time during automated sessions.

Now you have to BACK UP YOUR bugs.txt!! The program works by scanning that file, reporting everything in it and saving it into bugs_archive.txt. If you don't clear the file first, it will try to report everything again. Best option is to rename it to bugs_archive.txt, your new reports will be appended to it


### How to use TSReporter
After you have set up the config, you can select mode 1 to report all the bugs from your bugs.txt. You will have to enter your Mantis password (don't worry, it's not saved or sent anywhere). If you want to  upload images with your report, you will have to edit them and save them into the directory in config.cfg

TSReporter will now take every bug and do the following:
1. Open a browser window, log into mantis and search for bug duplicates, wait for your reply.
2. Open a browser window and pre-fill a Mantis report. If you followed the convention outlined below, all you have to do now is change priority/severity and add any optional info to the description.
3. Repeat the above for all bugs.

#### Convention
When using F11 or Shift+F11 in the game, you will have to fill in some additional information. 

[m|a|av|ac|ar|aa]\_reportname<br/>
determines the category of the asset, as per the testing guide<br/>
-m: Map<br/>
-a: Asset - You will be asked to specify the type later!<br/>
-av: Vegetation asset<br/>
-ac: Animated character asset<br/>
-ar: Road asset<br/>
-aa: Other assets

.reportname<br/>
Attatches this coordinate/screenshot to the previous report. 

!reportname<br/>
This will not be reported. You can also leave the report blank and it will not be reported.

reportname will be what is put into the Summary in Mantis, so you have to follow the testing guide in naming it.

Here are some examples:

m_Idaho - Twin Falls - floating cow<br/>
.floating cow 2<br/>
!dont forget to buy milk lol<br/>
av_Utah - Salt Lake City - Tree without collision

This will create a map report with two images/coordinates attatched and an asset-vegetation report with one image