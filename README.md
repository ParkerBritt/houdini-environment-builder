<h1 align="center">Houdini Garden Builder</h1>
<p align="center">
  <a href="https://www.sidefx.com/"><img src="https://img.shields.io/badge/-Houdini-FF4713?style=for-the-badge&logo=houdini&logoColor=FF4713&labelColor=282828"></a>
  <a href="https://github.com/ParkerBritt?tab=repositories&q=&type=&language=python&sort="><img src="https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=3776AB&labelColor=282828"></a><br>
</p>

<image src="screenshots/example_render.jpg">


# Installation
To neatly contain all the parts of my tool and maintain portability, I've packaged it using the Houdini packaging standard.

The included start script will automatically generate and load the package.json and start Houdini using the ```houdini``` command.
If the houdini binary is not in your ```$PATH``` environment variable you will need to change this line to path to your Houdini binary.
eg.
```sh
/opt/hfs20.5.332/bin/houdini
```

> [!NOTE]
> I designed this tool to work ad hoc on linux and I cannot gauruntee functionality on other operating systems.

Installation can also be done manually by adding a package json file to your ```$HOUDINI_USER_PREF_DIR/packages``` directory.
You can use this template to create the package file, make sure to replace the paths with where you saved the package.

```json
{
    "path" : "/path/to/garden-package",
    "env": [
        {
            "GARDEN_TEXTURES_DIR": "/path/to/garden-package/textures"
        }
    ]
}
```

Additional guidance on generating these files can be found here
https://www.sidefx.com/docs/houdini/ref/plugins.html
