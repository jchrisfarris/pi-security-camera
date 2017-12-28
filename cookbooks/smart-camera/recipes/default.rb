#
# Cookbook Name:: pht-camera
# Recipe:: default
#
# Copyright 2017, PrimeHarbor Technologies
#
# All rights reserved - Do Not Redistribute
#

secret = Chef::EncryptedDataBagItem.load_secret('/etc/chef/encrypted_data_bag_secret')
camera_data = Chef::EncryptedDataBagItem.load('pht-enc', node['camera']['api_key_databag'], secret)

%w(gdebi-core ssmtp mailutils mpack openssh-server awscli).each do |p|
  apt_package p
end

# Create a blank directory
directory node['camera']['base_dir'] do
  owner 'pi'
  group 'pi'
  mode '00755'
  action :create
  recursive true
end

%w(log etc scripts images tmp).each do |d|
  directory "#{node['camera']['base_dir']}/#{d}" do
    owner 'pi'
    group 'pi'
    mode '00755'
    action :create
    recursive true
  end
end

mask_file_string = ""
if node['camera']['mask_file'] != "false"
  mask_file_string = "mask_file #{node['camera']['base_dir']}/etc/#{node['camera']['mask_file']}"
end

cookbook_file "#{node['camera']['base_dir']}/etc/#{node['camera']['mask_file']}" do
  source node['camera']['mask_file']
  owner 'pi'
  group 'pi'
  mode 00600
  not_if { node['camera']['mask_file'] == "false" }
end


template "#{node['camera']['base_dir']}/etc/motion.conf" do
  source 'motion.aws.conf.erb'
  user 'pi'
  group 'pi'
  mode '00600'
  variables(
    base_dir: node['camera']['base_dir'],
    camera_name: node['camera']['camera_name'],
    camera_auth_string: node['camera']['camera_auth_string'],
    mask_file_string: mask_file_string,
    motion: node['camera']['motion_conf']
  )
  notifies :restart, 'service[motion]', :delayed
end

%w(process-picture.sh process-movie.sh).each do |f|
  template "#{node['camera']['base_dir']}/scripts/#{f}" do
    user 'pi'
    group 'pi'
    mode '00755'
    variables(
      bucket: node['camera']['s3_bucket']
    )
  end
end

template '/etc/init.d/motion' do
  source 'motion-init.erb'
  user 'root'
  group 'root'
  mode '00755'
  variables(
    base_dir: node['camera']['base_dir']
  )
end

# Configure AWS for pi and ????
%w(pi).each do |user|
  directory "/home/#{user}/.aws" do
    owner user
    group user
    mode '00755'
    action :create
    recursive true
  end

  template "/home/#{user}/.aws/credentials" do
    source 'credentials.erb'
    owner user
    group user
    mode 00600
    variables(
      AWS_ACCESS_KEY: camera_data['AWS_ACCESS_KEY'],
      AWS_SECRET_KEY: camera_data['AWS_SECRET_KEY']
    )
  end

  cookbook_file "/home/#{user}/.aws/config" do
    source 'config'
    owner user
    group user
    mode 00600
  end
end




# Enable SSH
directory '/home/pi/.ssh' do
  owner 'pi'
  group 'pi'
  mode '00700'
  action :create
  recursive true
end

cookbook_file '/home/pi/.ssh/authorized_keys' do
  source 'pi-camera.pub'
  owner 'pi'
  group 'pi'
  mode 00600
end

service 'motion' do
  action [:enable, :start]
end

service 'ssh' do
  action [:enable, :start]
end
