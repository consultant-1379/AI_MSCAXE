#!/bin/bash

# This is to backup in git the files used by jenkins 
# It will copy from jenkins directories inside of local git .jenkins 

# xmlstarlet sel -t -v '//listView[name="AI_ML"]/jobNames' /home/eaxeci/.jenkins/config.xml

rm -rf .jenkins/jobs

for i in $(xmlstarlet sel -t -v '//listView[name="AI_ML"]/jobNames' /home/eaxeci/.jenkins/config.xml 2>/dev/null )
do 
echo $i
mkdir -p .jenkins/jobs/$i
cp /home/eaxeci/.jenkins/jobs/$i/config.xml .jenkins/jobs/$i
done



#cp /home/eaxeci/.jenkins/nodes/AI_LINUX/config.xml .jenkins/nodes/AI_LINUX/
#cp /home/eaxeci/.jenkins/jobs/testmktr/config.xml .jenkins/jobs/testmktr/
#cp /home/eaxeci/.jenkins/jobs/triggerjob/config.xml .jenkins/jobs/triggerjob/




