# Prosjektplan – Radionette Raspberry Pi 3

## 1. Formål og avgrensning

Bygge om en original 1950–60-talls Radionette til internett-radio, med originalt brukergrensesnitt. Første utgave fokuserer **kun på internett-radio**, ikke Bluetooth, DAB eller lokal musikk.

## 2. Brukeropplevelse

1. Brukeren slår på radioen med original kontroll.
2. Raspberry Pi starter radiotjenesten automatisk.
3. Brukeren velger FM, AM, K eller L med én av fire originale knapper.
4. Frekvensknotten flytter en virtuell tuner langs skalaen for det valgte båndet.
5. Mellom stasjoner høres analogt inspirert susing. Ved en konfigurert stasjon fades støyen ut og strømmen fades inn.
6. Volum justeres med original volumknapp; play/pause kan knyttes til egnet knapp.

## 3. Kanalmodell

Hvert bånd har separat virtuell frekvensskala og et sett med kanaler. Stasjonene kan ha feltene `name`, `url`, `position` (normalisert 0–1) og `capture_width`. Den normaliserte posisjonen skiller internettstrømmer fra reelle kringkastingsfrekvenser. FM/AM/K/L er navn på originale bånd, ikke løfte om faktisk RF-mottak.

Eksempel (illustrasjon, ingen verifiserte stream-URL-er):

```yaml
bands:
  FM:
    stations:
      - name: "Kanal A"
        url: "https://example.invalid/stream-a"
        position: 0.25
        capture_width: 0.035
  AM:
    stations: []
  K:
    stations: []
  L:
    stations: []
```

## 4. Maskinvare

- Raspberry Pi 3, stabil 5 V strømforsyning dimensjonert for modellen.
- Originale fire båndknapper: undersøk om de er låsende og hvordan de er elektrisk koblet.
- Frekvensvelger: identifiser om den driver potensiometer, dreiekondensator eller snorhjul; velg MCP3008/encoder/sensor etter inspeksjon.
- Volum: vurder mekanisk kobling til Logitech-volumkontroll mot potensiometer via ADC eller encoder.
- Logitech 2.1: originale satellitter monteres inne; subwoofer holdes eksternt. Behold egnet Logitech-forsterker og impedanstilpasning.
- Lyd: test USB-DAC opp mot Pi 3 analogutgang for brum, susing og jordsløyfer.
- Strøm: planlegg sikker Pi-avslutning før eventuell fysisk frakobling. Skill lavspenning og nettspenning.

## 5. Programvaremoduler (planlagt)

```text
radionette/
  config.py          # lesing og validering av kanaler og bånd
  inputs.py          # GPIO, ADC eller encoder
  tuner.py           # posisjon, stasjonsdeteksjon og hysterese
  player.py          # nettstream, reconnect, volum og pause
  noise.py           # støygenerator og crossfade
  app.py             # tilstandsmaskin og hovedløkke
config/
  stations.example.yaml
systemd/
  radionette.service
tests/
```

Dette er en foreslått struktur, ikke ferdig implementerte filer.

## 6. Viktige designvalg

- **Tuning:** filtrer analoge målinger for jitter; bruk hysterese slik at en kanal ikke hopper inn/ut på grensen.
- **Støy:** generer kontrollert lavnivå-støy, med separat lydmiks og begrenset maksimalnivå; ikke bruk fullstyrke hvit støy.
- **Nett:** timeout og reconnect ved brutt radiostrøm. Ved fravær av nett skal radioen ikke henge.
- **Volum:** én tydelig volum-master for å unngå dobbel regulering og plutselige lydsprang.
- **Power:** Pi bør avsluttes kontrollert. En mekanisk nettbryter alene kan gi filsystemkorrupsjon.
- **Service:** logg feil, start ved boot og restart ved uventet prosessfeil.
- **Konfigurasjon:** kanalnavn, posisjoner, stasjonsbredde og stream-URL-er kan endres uten kodeendring.

## 7. Akseptansekriterier for første fungerende versjon

- Radioen starter uten skjerm eller tastatur.
- Alle fire bånd kan velges fysisk.
- Frekvensknotten velger en kanal på riktig bånd.
- Susing mellom stasjonene og jevn overgang ved kanalvalg.
- Lyd går til Logitech 2.1, med kontrollerbart volum.
- Avspilling gjenopptas etter kortvarig nettutfall.
- Ingen GPIO-tilkoblinger overstiger 3,3 V, og strømforsyning er sikker.

## 8. Neste arbeid

1. Ta tydelige bilder av radioens innside, skala og kontrollmekanikk.
2. Dokumenter Logitech 2.1-modell og volumkontroll.
3. Fastsett ADC/encoder, GPIO-pinout og faktisk strømkrets.
4. Implementer Python-prototype og test med ekte kanal-URL-er.
