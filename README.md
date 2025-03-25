# ARC_tools

To make your life easier. Please change your hostnames to arc and xt2 respectively. To do this, navigate to your ~/.ssh directory and open your config file, if it doesnt exist create it using 

```
touch config
```

Note that this file has no file type extension.

Now, insert the following into the file:

```
Host xt2
  Hostname <address to xct server>
  User <your xct username>
  KexAlgorithms +diffie-hellman-group1-sha1,diffie-hellman-group14-sha1
  PubkeyAcceptedAlgorithms ssh-rsa
  HostKeyAlgorithms +ssh-dss

Host arc
  HostName arc.ucalgary.ca
  User <your username on ARC>

Host *
  ForwardAgent yes
  ForwardX11 yes
```

Note that this is just replacing typing out the entire ssh User@Hostname line to connect to the server. All scripts are hard coded to look for and connect to xt2 and arc. It is much easier this way. You can look into implementing environment variables for this instead but I confidently think this is the best way.

Another piece of valuable life advice, use ssh keys to connect to these ssh servers rather than passwords. To do this, generate an ssh key using:

```
ssh-keygen 
```

Click enter a few times (do not enter a password) and now you have an ssh key (.pub file), keep this safe. You can use this to conect to ARC, xCT, make git changes all without a password. Think of it like the remember me checkbox before you log-in to Facebook.

To copy this ssh key onto ARC, You have to copy the key in the .pub file onto the file called authorized_keys. An easy way to do this is to use the ssh-copy-id command:

```
ssh-copy-id arc
```

Enter your ARC (UCalgary) password. Try to login to ARC using:

```
ssh arc
```

If this still requests a password, enter your password and then enter the following command:

```
chmod 700 ~/.ssh
```

This is the last time you will have to use your password to connect to ARC. 

xCT, GitHub, and Compute Canada servers will have different instructions. For xCT, contact Steve Boyd. The remaining have instructions on their website.

You will need ssh key access to both ARC and 