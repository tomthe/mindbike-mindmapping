# MindBike Mindmapping #

MindBike is a Mindmap viewer and editor. It is still in alpha/beta-state - not ready for production-use. It reads and displays Mindmaps in the Freemind/Freeplane Format (*.mm). Its possible to edit and save the mindmaps in the same format, so they are still compatible with Freemind or Freeplane.

## Features ##
 * Displaying and Editing of Mindmaps
 * Fully compatible with Freemind and Freeplane
   * Mindbike can't display or edit notes, icons, node-details and node-attributes. But it will preserve them, so they don't get lost by opening/saving *.mm-Files
   * no rich-text yet. No unicode on Android (should be solved in time)
 * Collaborative editing: Mindbike can merge two mindmaps easily. If you have two copies of the same map - one on your desktop and one on your smartphone - you can add nodes on both maps and merge them later. After merging you have all the new nodes of both maps in both maps! (No additional software (like Git) required)
 * Hashtags. Add #hashtags in your node-text to easily access nodes with similar content. Mindbike will generate a #Hashmap that bundles all the nodes with the same #hashtags. Use #hashtag:subtag to build subgroups. This enables an easy GTD (GettingThingsDone) workflow.

## Download ##
[Download-Section](https://bitbucket.org/tomthe/mindbike-mindmapping/downloads)
Please note that the builds aren't always up-to-date. For now, I only provide packages for Android, sometimes for Windows.

### Multi-Platform ###

It's written in Python + Kivy, so it runs under Android, iOS, Windows, Linux and MacOS! So far I can only offer packages for Android. Please help me packaging it for other Platforms.

### Run the Code ###

Dependencies:
* Python 2.7
* [Kivy 1.8](http://kivy.org/)