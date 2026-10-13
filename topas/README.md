# TOPAS v4.3.0

This Dockerfile creates an image with TOPAS v4.3.0 installed. It allows for
extensions. So in order for the image to be created you need to have a folder
named 'extensions' where you have the .cc/.hh files. It can be empty.
See [the TOPAS github page](https://github.com/OpenTOPAS/OpenTOPAS/blob/main/OpenTOPAS_quickStart_Debian.md) for more information.

A docker compose file is also provided as an example on how to run the image
