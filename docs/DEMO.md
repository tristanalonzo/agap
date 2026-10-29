# Demo script — about 3 minutes

Rehearse this twice on the actual demo laptop before the defense. Timings are a guide, not a
target; the last beat is the one that matters, so do not let the earlier ones run long.

## Before you stand up

- [ ] Backend running (`uvicorn app.main:app --reload --port 8000`) and http://127.0.0.1:8000/health/live returns `{"status":"ok"}`
- [ ] Frontend running (`npm run dev`), app open at http://localhost:5173 in device/phone view
- [ ] Browser zoom at 100%, console closed, notifications off
- [ ] Refresh once so "Updated just now" is fresh when you start
- [ ] Backup video and screenshots on the desktop, in case the Wi-Fi dies (see the end)
- [ ] Know your own answer to "is this a real warning app?" — it is not, and say so first

## The run

**0:00 — What it is (20s).**
"AGAP shows a Quezon City resident four things for their own location: a cyclone category,
the live PAGASA rainfall warning, a flood hazard map, and their nearest evacuation shelter.
It is a prototype, not an official warning service, and the app says so on every card."

**0:20 — Location (15s).**
Overview tab. Point at the location card: Quezon City, coordinates, QC BOUNDS OK.
Tap **Use my location** (or **Set location** and type a QC coordinate if GPS is slow).
"Everything below updates for that point. Outside Quezon City the API rejects it — we do not
pretend to cover a city we have no data for."

**0:35 — The four cards (50s).** Walk down the Overview, then the tabs.
- Rainfall banner: read the current PAGASA state aloud and point at the **LIVE** badge and time.
- Cyclone card: "This one is fake, on purpose." Point at the **DEMO** badge, the purple banner,
  and the warning line. "The model is Team A's and is not delivered yet. Rather than hide the
  gap, the app marks it."
- Debris tab: material hazards for the category, with its own tier label.
- Action / SOS tab: civil defense status and the preparedness checklist.

**1:25 — Flood scenarios (25s).** Hazard Map tab. Tap **5-year**, **25-year**, **100-year**.
"These are static historical scenarios from Project NOAH — not a live flood forecast, which is
why the card is badged STATIC. The user picks the scenario; it is never chosen from the cyclone
category, because a storm category does not tell you a return period."
Point at the legend: "Areas with no colour are not marked safe. We never tell anyone they are safe."

**1:50 — Nearest shelter (25s).** Same tab, scroll to the map and the shelter card.
Black pin is you, green is the nearest of 239 shelters, blue are the rest.
"Straight-line distance, not a walking route — we say that on the card. And every shelter is
tagged **UNVERIFIED**, because they come from OpenStreetMap, which does not prove a place is an
open evacuation centre. The card tells the user to confirm with their barangay."

**2:15 — Hotlines (15s).** Action / SOS tab, scroll to the hotlines.
Tap one and let the phone dialer open. "Six numbers, from the QC government, with the date we
last checked them."

**2:30 — The honesty feature (30s). Do not skip this one.**
Turn off the Wi-Fi.
- Within a minute the rainfall card goes **UNAVAILABLE** and the alert level reads `unknown`.
- The bar at the top turns to **STALE** with the age of the last good update.
- The hotlines stay, badged **STALE**, from the last good list.

"This is the part we are proudest of. A disaster app that says 'no warning' because its internet
dropped is worse than no app. When the fetch fails we say `unknown`, never 'no warning', and the
card keeps its last known text with a timestamp so the user can judge it themselves."
Turn the Wi-Fi back on and refresh to recover.

## If they ask

- **"Is the cyclone category a Signal No.?"** No. It is a model estimate of storm intensity.
  PAGASA wind signals account for terrain and lead time; this does not, and the card says so.
- **"Why is the shelter distance straight-line?"** Routing needs a road-network service we did
  not have. The card labels it rather than implying a walking time we cannot compute.
- **"Can it work offline?"** Partly. Hotlines and the last assessment are cached and shown as
  STALE. The map needs the internet, because the tiles are downloaded.
- **"What is left?"** The real model. The seam is built — flip one setting and it runs — but
  the model and its preprocessing come from Team A, and we still need to decide which satellite
  frames to feed it.

## The replay chips

The **Replay: TS / TY / STY** chips at the top are example values from the design mockup, so
the examiner can see the UI at higher categories. They are labelled DEMO. If you show them,
say they are mockup values — they are not archived model runs. The "past storms, model result
versus the official category" view is not built.

## If it breaks

Keep going and narrate. A prototype failing live is a better story than a frozen screen.
- Map blank → "the tiles need internet" and move on to the shelter card, which still works.
- Backend down → the app shows its error state with a Retry button; that is a real state worth
  showing. Restart uvicorn in the other terminal.
- Everything down → switch to the backup video. Record it the night before and keep it on the
  desktop, not in the cloud.
