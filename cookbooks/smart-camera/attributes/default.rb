# Camera Defaults


default['camera']['base_dir'] = "/usr/local/motion"

default['camera']['camera_name'] = "SetCameraNameInRoleAttrib"
default['camera']['camera_auth_string'] = "camera:password"
default['camera']['rotate'] = "0"
default['camera']['s3_bucket'] = "FIXME"

default['camera']['mask_file'] = "false"

# Settings for the motion.conf file
default['camera']['motion_conf']['threshold'] = "1500"
default['camera']['motion_conf']['minimum_motion_frames'] = "5"
default['camera']['motion_conf']['rotate'] = "0"
default['camera']['motion_conf']['framerate'] = "30"
default['camera']['motion_conf']['pre_capture'] = "3"
default['camera']['motion_conf']['post_capture'] = "3"
default['camera']['motion_conf']['event_gap'] = "30"
default['camera']['motion_conf']['output_pictures'] = "best"
default['camera']['motion_conf']['locate_motion_mode'] = "preview"

default['camera']['api_key_databag'] = "camera"

# <%= @motion['rotate'] %>