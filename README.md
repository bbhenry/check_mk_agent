## Introduction
Here are some custom monitoring scripts that I have created to use with [check_mk local checks][1]. If you don't already know what check_mk is, I wrote another [blog post][2] about it and explaining why it is currently the best open source monitoring tool for any enterprise.

Since I have started using Check_MK based monitoring solution, I have been creating custom check scripts for functions that I can't find from [Nagios Exchange][3] or [Check_MK Exchange][4]. This post will be updated as I add more custom check_mk local checks to my Github repository. All of them are free to use and you can find them [here][5].

If you don't know how or where to install these custom checks on your Check_MK enabled Nagios server, or OMD, please refer to the official documentation [here][6]. I will only be covering what these custom checks are and what their intentions are for.

## Custom local checks for Check_MK (OMD) Monitoring
### check_asterisk
### check_freeswitch
### check_ipsec
### check_mount_rw
Even though the Check_MK agent already monitor the NFS mount points by default, weird situation could happen at the read and write level while the mount point seems perfectly fine. The script is used to catch those situations for not only NFS but also GlusterFS mount points.

**Feature**

1. The script finds all NFS or GlusterFS mount points on your system.
2. The script then write a temporary file with a random number as its content to all detected NFS or GlusterFS mount points.
3. Then the script will read from those files that just got written and verify the content.
4. Upon successful write and read verification, the script will return OK status, otherwise it will alert critial to Nagios through Check_MK agent.

**Sample Output**  

The service description will even specify what type of remote file system the mount point is using.
```
0 Mount_NFS_RW_:/server02 - Write and read test to the /server02 mount point was successful
0 Mount_NFS_RW_:/server01 - Write and read test to the /server01 mount point was successful
0 Mount_NFS_RW_:/dev-server-01 - Write and read test to the /dev-server-01 mount point was successful
0 Mount_GLUSTERFS_RW_:/storage - Write and read test to the /storage mount point was successful
```

## License
Copyright (c) 2013 Henry Huang. See the LICENSE file for license rights and limitations (MIT).

  [1]: http://mathias-kettner.de/checkmk_localchecks.html
  [2]: http://blog.unicsolution.com/2013/11/best-monitoring-solution-omd-nagios.html
  [3]: http://exchange.nagios.org/
  [4]: http://exchange.check-mk.org/
  [5]: https://github.com/bbhenry/check_mk_local
  [6]: http://mathias-kettner.de/checkmk_localchecks.html