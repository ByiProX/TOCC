rm backup_files.tar.gz
tar zcvf backup_files.tar.gz ./

git add .
git commit -m 'backup files'
git push

echo "backup finished !"
