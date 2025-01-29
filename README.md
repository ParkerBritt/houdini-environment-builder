To neatly contain all the parts of my tool and maintain portability, I've packaged it using the Houdini packaging standard.

The included start script will automatically load the package and start Houdini using the ```houdini``` command.
If the houdini binary is not in your ```$PATH``` environment variable you will need to change this line to path to your Houdini binary.
> [!NOTE]
> I designed this tool to work ad hoc and I cannot gauruntee functionality on other operating systems.

Installation can also be done manually by adding a package json file to your '$HOUDINI_USER_PREF_DIR/packages' directory.
You can use this template to create the package file, make sure to replace the paths with where you saved the package.

```
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
