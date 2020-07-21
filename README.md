# TSreporter

## For users

### What is TSReporter
TSReporter is a utility tool that helps automate the process between making a screenshot in the game and inputing the information into Mantis. 

### How to install and set up
Just copy the folder containing this README onto your computer. When you first launch it, it will run setup. You will have to input some paths to relevant folders.

1. Trunk
For TSReporter to be able to find your current trunk revision, your trunk directory must be structured accordingly:

Trunk  
+--ATS  
+--ETS2

Trunk is the directory you select, it can be named anything. However, the game subdirectories MUST be named ATS and ETS2 in order to avoid ambiguity, where some people have their folders within trunk named ATS_old and ATS_new.

If you only use one Trunk game, that's okay. However, if you have the games in different directories, the program will crash! If you have multiple trunk versions of the same game and you report from any of them, it will report from the CURRENT of the game selected here.

Trunk_1  
+--ATS  
Trunk_2  
+--ETS2  
WILL CRASH!

2. Documents
Your documents directory is where the game files are automatically saved. 

Documents  
+--American Truck Simulator  
|	+--bugs.txt  
|	+--game.log.txt  
+--Euro Truck Simulator  
|	+--bugs.txt  
|	+--game_log.txt

3. Edited images
This is the folder where you save your edited images. They must be saved directly here, so if you have different folders for different games/dlcs/time periods, you will have to change it to the one where you want the program to get images from, otherwise the program will not find them! (you can just upload them manually as well)

4. Mantis username
What you use to log into Mantis (commonly in the format *firstName.lastName*). It is necessary because the session handler needs to log in every time during automated sessions.

Now you have to BACK UP YOUR bugs.txt!! The program works by scanning that file, reporting everything in it and saving it into bugs_archive.txt. If you don't clear the file first, it will try to report everything again. Best option is to rename it to bugs_archive.txt, your new reports will be appended to it


### How to use TSReporter
After you have set up the config, you can select mode 1 to report all the bugs from your bugs.txt. You will have to enter your Mantis password (don't worry, it's not saved or sent anywhere). If you want to  upload images with your report, you will have to edit them and save them into the directory in config.cfg. Make sure to save the image as either .jpg or .gif. It is important the edited image/gif is named exactly the same as the original screenshot, otherwise the program struggles in finding such image.

TSReporter will now revise each bug in the bugs.txt and do the following:
1. Open a browser window, log into mantis and search for bug duplicates, wait for your reply.
2. Open a browser window and pre-fill a Mantis report. If you followed the convention outlined below, all you have to do now is change priority/severity and add any optional info to the description.
3. Repeat the above for all bugs.

#### Convention
When using F11 or Shift+F11 in the game, you will have to fill in some additional information. 

[m|a|av|ac|ar|aa]\_reportname  
determines the category of the asset, as per the testing guide  
-m: Map  
-a: Asset - You will be asked to specify the type later!  
-av: Vegetation asset  
-ac: Animated character asset  
-ar: Road asset  
-aa: Other assets

.reportname  
Attatches this coordinate/screenshot to the previous report. 

!reportname  
This will not be reported. You can also leave the report blank in order for the program to ignore it.

reportname will be what is put into the Summary in Mantis, so you have to follow the testing guide in naming it.

Here are some examples:

m_Idaho - Twin Falls - floating cow 
.floating cow 2  
!dont forget to buy milk lol   
av_Utah - Salt Lake City - Tree without collision

This will create a map report with two images/coordinates attatched and an asset-vegetation report with one image
