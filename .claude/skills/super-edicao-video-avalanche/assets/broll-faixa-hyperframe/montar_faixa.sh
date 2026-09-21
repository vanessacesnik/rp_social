cd /Users/naiarodrigues/naia-agent/entregas/vsl-broll
FF=/opt/homebrew/bin/ffmpeg
SRC="/Users/naiarodrigues/Desktop/vsl cortada no meio.mov"
# espera os 130
for i in $(seq 1 240); do
  ok=1; for n in $(seq 0 129); do nnn=$(printf "%03d" $n); [ -s "brolls/bar/bar-$nnn.mp4" ] || ok=0; done
  [ "$ok" = "1" ] && break; sleep 10
done
echo "[bar $(date +%H:%M:%S)] todos renderizados, concatenando" >> logs/auto-bar.log
> /tmp/bar-concat.txt
for n in $(seq 0 129); do nnn=$(printf "%03d" $n); echo "file '$PWD/brolls/bar/bar-$nnn.mp4'" >> /tmp/bar-concat.txt; done
$FF -y -f concat -safe 0 -i /tmp/bar-concat.txt -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -r 30 brolls/bar/bar-track.mp4 >> logs/auto-bar.log 2>&1
echo "[bar $(date +%H:%M:%S)] overlay na faixa preta (y=1076)" >> logs/auto-bar.log
$FF -y -i "$SRC" -i brolls/bar/bar-track.mp4 -filter_complex "[1:v]scale=1080:844,setsar=1,fps=30[bar];[0:v][bar]overlay=0:1076:shortest=0[v]" -map "[v]" -map 0:a -c:v h264_videotoolbox -b:v 12M -c:a aac -b:a 192k -movflags +faststart "/Users/naiarodrigues/Desktop/VSL-FAIXA-HYPERFRAME.mp4" >> logs/auto-bar.log 2>&1
if [ -s "/Users/naiarodrigues/Desktop/VSL-FAIXA-HYPERFRAME.mp4" ]; then
  osascript -e 'tell application "QuickTime Player" to quit' 2>/dev/null
  /usr/bin/open "/Users/naiarodrigues/Desktop/VSL-FAIXA-HYPERFRAME.mp4"
  echo "[bar $(date +%H:%M:%S)] PRONTO E ABERTO" >> logs/auto-bar.log
fi
