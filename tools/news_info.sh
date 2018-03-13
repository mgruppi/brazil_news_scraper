#reads /data/data/br_news and gives some info

echo "Counting files... "
nfiles=$(find /data/data/br_news -type f | wc -l)
ndirs=$(ls -ld /data/data/br_news/* | wc -l)
echo "Total files in /data/data/br_news/: $nfiles"
echo "Total dirs in /data/data/br_news/: $ndirs"


nfiles_parsed=$(find /data/data/br_news_plain_text -type f | wc -l)
echo "Total files in /data/data/br_news_plain_text/: $nfiles_parsed"

