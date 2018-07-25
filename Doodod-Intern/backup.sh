rm backup_files.tar.gz
tar zcvf backup_files.tar.gz ./source/

git add .
git commit -m 'backup files'
git push

echo "backup finished !"
