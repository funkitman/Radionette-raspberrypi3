# Første benkprototype

## Arkitektur og avgrensning

Terminal (senere GPIO/ADC) → Python tuner med hysterese → én mpv-prosess → standard lydutgang.
Python bruker bare standardbiblioteket og JSON. mpv dekoder HTTP(S)-lyd. Controlleren forsøker igjen fem sekunder etter at mpv avslutter; nettlesing har ti sekunders timeout. Referanse: https://mpv.io/manual/stable/

Implementert: fire bånd, normalisert tuning, stopp/start, oppstartsvolum, dry-run og valgfri systemd-autostart. Capture width er avstand på hver side av posisjonen; frigivelsesgrensen er ytterligere 0,01. Overlapp velger nærmeste kanal, mens fanget kanal beholdes innen hysteresegrensen.

Mellom stasjoner er det stille. GPIO, ADC, encoder, støymiks/crossfade, fysisk volum/power og lagring av sist valgte kanal gjenstår. Dette leverer programvarebenken i prosjektplanens fase 2, ikke alle kriteriene for ferdig fysisk radio.

## Manglende krav

- Radionette-modell, mekanikk, bryterkontakter og skalaens vandring må kartlegges før sensor, pinout og kalibrering velges.
- Kanalvalg og direkte strøm-URL-er må bestemmes. Eksemplet bruker lokal HTTP-testlyd, ingen lovet radiotjeneste.
- Pi-lydutgang, Logitech-modell, volumkobling, isolasjon, strømforsyning og trygg avslutning må avklares før montering.

## Installer og prøv uten Pi

På Raspberry Pi OS Lite eller Debian/Ubuntu, fra repoets rot:

```sh
sudo apt update
sudo apt install python3 mpv git
cp config/stations.example.json config/stations.json
python3 radio.py --config config/stations.json --dry-run
```

Kommandoer: `band FM`, `band AM`, `band K`, `band L`, `tune 0.25`, `tune 0.8`, `stop`, `play`, `quit`. Stop stanser lyd; play eller ny tuning starter igjen. EOF, Ctrl+C og SIGTERM rydder avspilleren. Dry-run krever verken mpv, nett eller lydkort.

Erstatt navn og URL i egen JSON-konfigurasjon med direkte HTTP(S)-lydstrømmer, og start ekte lyd:

```sh
python3 radio.py --config config/stations.json --volume 20
```

Konfigurasjonsendringer krever omstart. Volum settes ved oppstart, standard 30/100. Tomme bånd er tillatt.

## Reproduserbar lokal lydtest

Lag ti sekunder svak 440 Hz tone, fra repoets rot:

```sh
python3 - <<'PY'
import math, struct, wave
with wave.open('tone.wav', 'wb') as w:
    w.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
    w.writeframes(b''.join(struct.pack('<h', int(2000*math.sin(2*math.pi*440*i/22050))) for i in range(220500)))
PY
python3 -m http.server 8000 --bind 127.0.0.1
```

I annen terminal: `python3 radio.py --volume 20`. Eksemplet velger testtonen på FM/0.25. Etter filslutt starter den igjen etter fem sekunder. Prøv `tune 0.8` (stille), `tune 0.25` (tone) og tomme bånd. Stans HTTP-serveren og start den igjen for å teste nytt forsøk etter feil/timeout. Controlleren overvåker prosessavslutning, ikke avspillingsfremdrift: alle typer hengende strømmer er ikke dekket.

## Automatiske tester

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile radio.py
```

Testene dekker hysterese, overlapp, ugyldige tall, alle bånd i CLI, dry-run, prosessopprydding og retry med simulert mpv. De verifiserer ikke faktisk dekoding, lyd eller internettilgang.

## Valgfri autostart på Pi

Test manuell lyd først. Deretter fra repoets rot:

```sh
sudo install -d /opt/radionette /etc/radionette
sudo install -m 644 radio.py /opt/radionette/radio.py
sudo install -m 644 config/stations.json /etc/radionette/stations.json
sudo install -m 644 systemd/radionette.service /etc/systemd/system/radionette.service
sudo systemctl daemon-reload
sudo systemctl enable --now radionette.service
systemctl status radionette.service
journalctl -u radionette.service -f
```

Tjenesten spiller FM/0.25 uten terminal. Den bruker standard lydutgang og audio-gruppen, beregnet på Pi OS Lite med ALSA. Desktop/PipeWire kan kreve brukertjeneste eller separat lydoppsett. Endre ExecStart for annen startkanal/volum, kjør daemon-reload og restart. Fysiske knapper er ennå ikke aktive. Tjenesten er ikke testet på Pi.

Fjern autostart med `sudo systemctl disable --now radionette.service`, fjern `/etc/systemd/system/radionette.service` og kjør `sudo systemctl daemon-reload`. Kode og konfigurasjon kan beholdes.

## Akseptanse

Uten Pi: tester passerer, fire bånd kan velges, lokal tone spiller, tuning utenfor kanal stanser lyd, kildebrudd utløser nytt forsøk, og avslutning etterlater ingen mpv-prosess. Med fysisk Pi: bekreft ARM-pakker, boot, lydutgang, nivå og nettutfall. GPIO og mekanikk krever separat implementasjon og maskinvaretest.

Original radio kan inneholde nettspenning og farlig restladning. Denne benkprototypen krever ingen kobling til originalelektronikken.
