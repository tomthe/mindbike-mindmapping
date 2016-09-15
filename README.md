# MindBike Mindmapping

MindBike is a Mindmap viewer and editor. It is still in alpha/beta-state but usable for mindmaps without extra-features.  It reads and displays Mindmaps in the Freemind/Freeplane Format (*.mm). Its possible to edit and save the mindmaps in the same format, so they are still compatible with Freemind or Freeplane. It is written in Python + Kivy and thus runs under Android, iOS, Windows, Linux and MacOS - but the main target ist Android. It is the best mindmapping-application for Freeplane and Freemind files on Android to date (though that doesn't mean much...). [Wikipedia links here](https://de.wikipedia.org/wiki/FreePlane).


## Features ##
 * Displaying and Editing of Mindmaps
 * Fully compatible with Freemind and Freeplane
   * Mindbike can't display or edit notes, icons, node-details and node-attributes. But it will preserve them, so they don't get lost by opening/saving *.mm-Files
   * no rich-text yet. No unicode on Android (should be solved in time)
 * Collaborative editing: Mindbike can merge two mindmaps easily. If you have two copies of the same map - one on your desktop and one on your smartphone - you can add nodes on both maps and merge them later. After merging you have all the new nodes of both maps in both maps! (No additional software (like Git) required)
 * Hashtags. Add #hashtags in your node-text to easily access nodes with similar content. Mindbike will generate a #Hashmap that bundles all the nodes with the same #hashtags. Use #hashtag:subtag to build subgroups. This enables an easy GTD (GettingThingsDone) workflow.


![screenshot_01_map.png](https://bitbucket.org/repo/Ee5dqy/images/3641041378-screenshot_01_map.png)
![screenshot_02_startmenu.png](https://bitbucket.org/repo/Ee5dqy/images/821495443-screenshot_02_startmenu.png)


# Installation
## Download ##
[Download-Section](https://bitbucket.org/tomthe/mindbike-mindmapping/downloads)
Please note that the builds aren't always up-to-date. For now, I only provide packages for Android, sometimes for Windows.
## Android
[How to install apk-files on android] (http://pc.answers.com/tablets/how-to-install-third-party-android-apps)
1. Allow the installation of 3rd-Party Apps (check Settings->Security->"Unknown Sources")
2. Copy the *.apk-file to your sd-card or internal memory. (tip: use dropbox over wifi)
3. Navigate to the apk-file and open it.

## Windows
1. Download the zip-file
2. Unpack into a new directory
3. Start Mindbike.....exe
(Note that packaging for Windows is still buggy)

## From source (For Windows, Linux and MacOS), for advanced Users! #
1. Install [Python 2.7](https://www.python.org/downloads/)
2. Install [Kivy](http://kivy.org/#download)
3. Check out the latest code via Mercurial or Git and Bitbucket
4. Run main.py as explained at [Kivy](http://kivy.org/#download)

# HowTo use MindBike
+ Double-tap into a node to edit its content
+ ﻿Tap outside to end editing
+ press the first of the 2 Buttons next to every node (f) to fold/unfold its children
+ press the second button (+) to add a child-node
+ On the desktop you can use your keyboard to navigate from node to node and to edit the nodes