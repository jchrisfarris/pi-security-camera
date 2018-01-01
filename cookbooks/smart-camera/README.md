smart-camera Cookbook
===================
Deploys the Smart Camera software onto a raspberry pi

Requirements
------------

1. Encrypted Databag to hold your AWS API Keys
2. Role file


Attributes
----------
{
  "name": "foyercam",
  "description": "Foyer Cam on rPi",
  "json_class": "Chef::Role",
  "default_attributes": {
    "camera": {
      "base_dir": "/pht/svc/motion",
      "camera_name": "FoyerCam",
      "camera_auth_string": "camera:XXXXXXX",
      "s3_bucket": "XXX-MYCAMERA-BUCKETXXX",
      "mask_file": "FoyerCam-Mask.pgm",
      "motion_conf": {
        "threshold": "5000",
        "minimum_motion_frames": "10",
        "rotate": "270",
        "locate_motion_mode": "off"
      }
    }
  },
  "override_attributes": {
  },
  "chef_type": "role",
  "run_list": [
      "recipe[smart-camera]"
    ],
  "env_run_lists": {
  }
}

Usage
-----
TBD

License and Authors
-------------------
Authors: Chris Farris <chris@room17.com>

Based on work by @markwest1972 https://github.com/markwest1972/smart-security-camera
