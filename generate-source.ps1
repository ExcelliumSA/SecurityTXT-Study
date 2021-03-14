cls
$baseCmd = "docker run -it --rm postgres psql -P pager=off -P footer=off -U guest -d certwatch --host crt.sh -c `"select name_value from certificate_and_identities where name_type='san:dNSName' and right(name_value, 3) = '.lu' offset __OFFSET__ limit __CHUNCK__`""
$content = ""
$chunk = 100
for($offset = 0; $offset -le 10000; $offset += $chunk) {
    if($offset -eq 0){
        $cmd = $baseCmd.replace("__OFFSET__", 1).replace("__CHUNCK__",$chunk)
    }else{
        $cmd = $baseCmd.replace("__OFFSET__", $offset).replace("__CHUNCK__",$chunk)
    }
    write-host ">>>> $cmd"
    $output = Invoke-Expression $cmd | Out-String
    write-host "<< $output"
    while($output -notlike "*name_value*"){
        write-host "[RETRY]>>>> $cmd"
        $output = Invoke-Expression $cmd | Out-String
        write-host "[RETRY]<< $output"
        if($output -like "*max_client_conn*"){
            write-host "[WAIT] 120 sec - release all connections..."
            Start-Sleep -Seconds 120
        }
        if($output -like "*conflict with recovery*"){
            write-host "[WAIT] 20 sec - data conflicts..."
            Start-Sleep -Seconds 20
        }
        if($output -like "*connection to server was lost*"){
            write-host "[WAIT] 10 sec - let server breathe..."
            Start-Sleep -Seconds 10          
        }       
    }
    $content += $output
    Set-Content -Path '.\data.txt' -Value $content
}