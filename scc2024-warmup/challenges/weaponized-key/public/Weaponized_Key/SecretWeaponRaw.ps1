$Symb0l = "X1Vu"
$M1sc = "NWgz"
$D1g1t = "bDM0"
$C0d3 = "TjFu"
$R4nd0m = "Awd"
$Sp3c14l = "zNy"
$End = "RH0="
$L3tt3r = "akE1"
$Num3r1c = "De1"
$T3xt = "TExf"
$Alph4 = "U0N"
$Extr4 = "c2gz"

Write-Host "
          ooo,    .---.
         o`  o   /    |\________________
        o`   'oooo()  | ________   _   _)
        `oo   o` \    |/        / / / /
          `ooo'   `---'         / / / /
"

Write-Host "Rebuilding secret key..."

$Part1 = $D1g1t + $Extr4 + $End -join ''
$Part2 = $C0d3 + $L3tt3r + $Symb0l -join ''
$Part3 = $Alph4 + $Num3r1c + $R4nd0m -join ''
$Part4 = $Sp3c14l + $M1sc + $T3xt -join ''

$K3yV4lu3 = ($Part3, $Part4, $Part2, $Part1) -join ''

$B4s3Ur1 = "https://cyberhero.rs/secret_weapon?key="
$T4rg3tUr1 = $B4s3Ur1 + [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($K3yV4lu3))

function Invoke-MysteriousDownload {
    param ([string]$url)
    $wc = New-Object System.Net.WebClient
    $wc.Headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64)"
    $data = $wc.DownloadString($url)
    Write-Output "Data retrieved: `n$data"
}

Invoke-MysteriousDownload -url $T4rg3tUr1

$Output = "Decrypting the secrets of the universe... or just a file."
Write-Output $Output