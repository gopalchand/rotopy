# Clear metadata
exiftool -all= -overwrite_original .

# Reset create and modify dates
for($i=1; $i -le 15; $i++)
{
	# num = 1..15
	# num = 01..15
	$num=([string]$i).PadLeft(2,'0')

	# Reset Creation and Modification dates
	$new_date = '01/01/2000 01:'+$num+':00'
	Get-ChildItem  .\Muybridge_race_horse_$num.png | % {$_.CreationTime = $new_date}
	Get-ChildItem  .\Muybridge_race_horse_$num.png | % {$_.LastWriteTime =$new_date}
}

