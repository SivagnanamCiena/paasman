# -*- mode: ruby -*-
# vi: set ft=ruby :

#Vagrant.require_plugin "coreos"

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  #config.vm.define "master" do |master|
  #  master.vm.box = "precise32"
  #  master.vm.box_url = "http://files.vagrantup.com/precise32.box"

  #  master.vm.synced_folder ".", "/vagrant/"

    #master.vm.network :private_network, :ip => "10.10.10.14"
  #end

  config.vm.define "dev" do |dev|
    dev.vm.box = "precise64"
    dev.vm.box_url = "http://files.vagrantup.com/precise64.box"
    #dev.vm.box_url = "http://files.vagrantup.com/precise32.box"
    #http://nitron-vagrant.s3-website-us-east-1.amazonaws.com/vagrant_ubuntu_12.04.3_amd64_virtualbox.box
    dev.vm.synced_folder ".", "/vagrant/"
    dev.vm.network :private_network, :ip => "10.10.10.25"

    dev.vm.provision :shell, :path => "bootstraps/bootstrap-dev.sh"

    dev.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024"]
    end
  end

  # coreos-master should be responsible for the router and director
  # and also hosting our private docker registry
  config.vm.define "coreos-master" do |coreos|
    coreos.vm.box = "coreos-72dev"
    #coreos.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/91.0.0/coreos_production_vagrant.box"
    coreos.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/dev-channel/coreos_production_vagrant.box"

    coreos.vm.hostname = "coreos-master"
    coreos.vm.network :private_network, :ip => "10.10.10.2"

    config.vm.network "forwarded_port", guest: 5000, host: 5100

    # TODO:
    coreos.vm.provision :shell, :path => "bootstraps/bootstrap-master.sh"

    coreos.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "512"]
    end
  end

  # coreos-n should be virtual machines in the cluster.

  1.times do |n|
    config.vm.define vm_name="coreos-#{n}" do |coreos|
      coreos.vm.box = "coreos-72dev"
      coreos.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/dev-channel/coreos_production_vagrant.box"
      #coreos.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/72.0.0/coreos_production_vagrant.box"

      coreos.vm.hostname = vm_name
      coreos.vm.network :private_network, :ip => "10.10.10.#{3+n}"

      # TODO:
      #coreos.vm.provision :shell, :path => "bootstrap-cluster.sh"

      coreos.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--memory", "512"]
      end
    end
  end

  #config.vm.define "coreos-3" do |coreos|
  #  coreos.vm.box = "coreos-72"
  #  coreos.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/72.0.0/coreos_production_vagrant.box"

    #coreos.vm.network :private_network, :ip => "10.10.10.15"
  #end

  # Every Vagrant virtual environment requires a box to build off of.
  #config.vm.box = "coreos-72"
  #config.vm.box = "precise32"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  #config.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/dev-channel/coreos_production_vagrant.box"
  #config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  #config.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/72.0.0/coreos_production_vagrant.box"
  #config.vm.box_url = "http://storage.core-os.net/coreos/amd64-generic/master/coreos_production_vagrant.box"

  #config.vm.synced_folder ".", "/home/core/share", id: "core", :nfs => true, :mount_options => ['nolock']
  #config.vm.synced_folder ".", "/home/core/share", id: "core", :nfs => true, :mount_options => ['nolock,udp,vers=3']

  #config.vm.network :private_network, :ip => "10.10.10.15"

  #config.vm.provision :shell, :path => "boostrap.sh"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network :forwarded_port, guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider :virtualbox do |vb|
  #   # Don't boot with headless mode
  #   vb.gui = true
  #
  #   # Use VBoxManage to customize the VM. For example to change memory:
  #   vb.customize ["modifyvm", :id, "--memory", "1024"]
  # end
  #
  # View the documentation for the provider you're using for more
  # information on available options.

  # Enable provisioning with Puppet stand alone.  Puppet manifests
  # are contained in a directory path relative to this Vagrantfile.
  # You will need to create the manifests directory and a manifest in
  # the file base.pp in the manifests_path directory.
  #
  # An example Puppet manifest to provision the message of the day:
  #
  # # group { "puppet":
  # #   ensure => "present",
  # # }
  # #
  # # File { owner => 0, group => 0, mode => 0644 }
  # #
  # # file { '/etc/motd':
  # #   content => "Welcome to your Vagrant-built virtual machine!
  # #               Managed by Puppet.\n"
  # # }
  #
  # config.vm.provision :puppet do |puppet|
  #   puppet.manifests_path = "manifests"
  #   puppet.manifest_file  = "site.pp"
  # end

  # Enable provisioning with chef solo, specifying a cookbooks path, roles
  # path, and data_bags path (all relative to this Vagrantfile), and adding
  # some recipes and/or roles.
  #
  # config.vm.provision :chef_solo do |chef|
  #   chef.cookbooks_path = "../my-recipes/cookbooks"
  #   chef.roles_path = "../my-recipes/roles"
  #   chef.data_bags_path = "../my-recipes/data_bags"
  #   chef.add_recipe "mysql"
  #   chef.add_role "web"
  #
  #   # You may also specify custom JSON attributes:
  #   chef.json = { :mysql_password => "foo" }
  # end

  # Enable provisioning with chef server, specifying the chef server URL,
  # and the path to the validation key (relative to this Vagrantfile).
  #
  # The Opscode Platform uses HTTPS. Substitute your organization for
  # ORGNAME in the URL and validation key.
  #
  # If you have your own Chef Server, use the appropriate URL, which may be
  # HTTP instead of HTTPS depending on your configuration. Also change the
  # validation key to validation.pem.
  #
  # config.vm.provision :chef_client do |chef|
  #   chef.chef_server_url = "https://api.opscode.com/organizations/ORGNAME"
  #   chef.validation_key_path = "ORGNAME-validator.pem"
  # end
  #
  # If you're using the Opscode platform, your validator client is
  # ORGNAME-validator, replacing ORGNAME with your organization name.
  #
  # If you have your own Chef Server, the default validation client name is
  # chef-validator, unless you changed the configuration.
  #
  #   chef.validation_client_name = "ORGNAME-validator"
end
