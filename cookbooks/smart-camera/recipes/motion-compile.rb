
%w(git autoconf automake pkgconf libtool libjpeg8-dev build-essential libzip-dev ).each do |p|
  apt_package p
end

%w(libavformat-dev libavcodec-dev libavutil-dev libswscale-dev libavdevice-dev ).each do |p|
  apt_package p
end

directory '/home/pi/src/' do
  owner 'pi'
  group 'root'
  mode '00755'
  action :create
  recursive true
end

git '/home/pi/src/motion' do
  repository 'https://github.com/Motion-Project/motion.git'
  action :sync
end

bash 'compile_motion' do
  cwd '/home/pi/src/motion'
  code <<-EOH
    autoreconf -fiv && \
    ./configure && \
    make
    make install
    EOH
  not_if { ::File.exist?('/usr/local/bin/motion') }
end
