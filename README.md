# Radionette – Raspberry Pi 3 Internet Radio

Restaurering og modernisering av en original Radionette-radio fra 1950–60-tallet, med originalt utseende og betjening, men internett-radio som lydkilde.

> **Status:** Planlegging / prototype. Ingen elektronikkoblinger eller programvare er ennå verifisert på fysisk radio.

## Mål

- Bevare originalt kabinett, frekvensskala, knotter og retrofølelse.
- Raspberry Pi 3 kjører Raspberry Pi OS Lite og Python.
- Internett-radiokanaler velges med radioens originale frekvensvelger.
- Fire bånd (FM, AM, K og L) velges med de originale båndknappene; hvert bånd får sin egen justerbare kanalliste.
- Kanaler plasseres på virtuelle frekvenser, med justerbare navn og posisjoner.
- Simulert analog susing/støy når tuneren står mellom kanalene, med overgang til ren radiolyd ved innstilling.
- Original volumknapp og av/på-kontroll gjenbrukes om praktisk mulig.
- Logitech 2.1: to satellitthøyttalere inne i kabinettet og subwoofer utenfor.

## Arkitektur

```text
Originale båndknapper ─┐
Frekvensvelger ────────┼──> GPIO / ADC / encoder ──> Python radio-controller
Av/på og play/pause ───┘                                 │
                                                         ├──> kanal-/båndkonfigurasjon
                                                         ├──> stream-avspilling
                                                         └──> simulert tuning-støy
Raspberry Pi lydutgang / USB-DAC ──> Logitech 2.1 forsterker ──> satellitter + sub
```

**Viktig:** Raspberry Pi 3 har ingen innebygd analog-til-digital-omformer. Dersom frekvensvelgeren er et potensiometer, trengs en ekstern ADC (f.eks. MCP3008). Dersom mekanikken bruker en dreiekondensator, må vi velge en egnet sensor/encoder eller annen målekrets. GPIO må aldri mates med 5 V.

## Teknologivalg (foreløpig)

| Del | Plan |
| --- | --- |
| Datamaskin | Raspberry Pi 3 |
| OS | Raspberry Pi OS Lite |
| Kontrollprogram | Python 3 |
| Lyd | VLC/libVLC eller mpv (avgjøres etter test) |
| Tuning | Potensiometer + MCP3008, eller rotary encoder, etter inspeksjon |
| Båndvalg | Fire fysiske knapper via GPIO med debounce |
| Lydutgang | USB-DAC foretrekkes for mindre støy; analog 3,5 mm kan testes |
| Oppstart | systemd-service |
| Kanaler | Redigerbar YAML/JSON-konfigurasjon |

## Utviklingsfaser

1. **Kartlegg radioen:** dokumenter chassis, frekvensvelger, knapper, volumkontroll og tilgjengelig plass.
2. **Prototype på benken:** Pi 3, kanalstrømmer, simulert båndvalg og tuning i Python.
3. **Les fysiske kontroller:** GPIO/ADC/encoder og kalibrering.
4. **Tuning-effekt:** justerbare kanalområder, terskler, susing og myke overganger.
5. **Integrer Logitech 2.1:** sikker strømføring, volumkontroll, lydtest og høyttalerplassering.
6. **Autostart og robusthet:** systemd, reconnect ved nettutfall, logging og trygg avslutning.
7. **Monter i kabinett:** mekanisk tilpasning uten å skade originalfronten.

## Avklaringer

- Eksakt Radionette-modell og innvendig mekanikk.
- Om volumknappen kan styre Logitech-forsterkeren direkte, eller bør leses av Pi.
- Om av/på skal bryte nettstrøm, styre Pi via safe shutdown, eller begge deler med egnet krets.
- Hvordan den originale skalaens mekaniske vandring skal kalibreres.
- Hvilke kanaler/stream-URL-er som skal ligge på hvert bånd.

## Sikkerhet

Originale radioer kan inneholde nettspenning og kondensatorer med farlig restladning. Koble fra strøm og la kvalifisert person vurdere original innmat før demontering. Nettspenning, jord og strømforsyning må utføres forsvarlig; aldri koble nettspenning direkte til Raspberry Pi GPIO.

Se [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for detaljert spesifikasjon.
