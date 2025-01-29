#!/usr/bin/bash

# get path of currently running script
script_path="$(realpath ${BASH_SOURCE})"

# remove script from base path
base_dir="${script_path%/*}"

packages_dir="${base_dir}/packages"

mkdir -p "${packages_dir}"

# write paths to package file
echo "{
    \"path\" : \"${base_dir}/garden-package\",
    \"package_path\" : \"${base_dir}/garden-package/packages\",
    \"env\": [
        {
            \"GARDEN_TEXTURES_DIR\": \"${base_dir}/garden-package/textures\"
        }
    ]
}" > "${packages_dir}/package.json"


export HOUDINI_PACKAGE_DIR="${packages_dir}"
goHoudini20.5
