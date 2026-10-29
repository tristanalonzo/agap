# Demo script — about 3½ minutes

Rehearse this twice on the actual demo laptop before the defense. Timings are a guide, not a
target; the last beat is the one that matters, so do not let the earlier ones run long.

## Before you stand up

- [ ] Backend running (`uvicorn app.main:app --reload --port 8000`) and http://127.0.0.1:8000/health/live returns `{"status":"ok"}`
- [ ] Frontend running (`npm run dev`), app open at http://localhost:5173 in device/phone view
- [ ] Browser zoom at 100%, console closed, notifications off
- [ ] Refresh once so "Updated just now" is fresh when you start
- [ ] Backend terminal visible and practised: the honesty beat needs **Ctrl+C**, **↑**, **Enter**
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

**2:30 — The honesty feature (45s). Do not skip this one.**

*Part 1 — PAGASA unreachable.* Overview tab. Turn off the Wi-Fi. In the backend terminal press
**Ctrl+C**, then **↑** and **Enter** to start it again. Click **Refresh** in the app.
- The banner reads **UNKNOWN — not loaded**, badged **UNAVAILABLE**.
- The rainfall card says *"This does NOT mean there is no warning. Check PAGASA directly."*

"A disaster app that says 'no warning' because its internet dropped is worse than no app. When
we can't reach PAGASA and have nothing recent, we say unknown — never 'no warning'."

> **Why the restart is not optional.** The backend keeps the last good PAGASA reading for 10
> minutes so it does not hammer PAGASA's site. Turning off the Wi-Fi alone changes nothing on
> screen for up to 10 minutes — and after that it shows the *old* reading marked STALE, not
> unknown, because an old real reading is more useful than none. Restarting empties that memory,
> so the failure shows at once. Checked on 2026-10-29.

*Part 2 — the server itself unreachable.* Press **Ctrl+C** in the backend terminal and leave it
stopped. Click **Refresh**.
- A line appears: *"Couldn't update … Showing the last result."* with **Retry**. The cards keep
  their last data and timestamps rather than going blank.
- Tap another tab, then **Action / SOS** again. The hotlines are now badged **STALE**, under
  *"Showing a cached list, may be outdated"* — and still tappable. (This works because you opened
  the hotlines at 2:15 while the server was up; that visit is what filled the cache.)

"With no server at all, the emergency numbers are still on the phone — labelled as old, not hidden."

To recover: **↑** and **Enter** in the backend terminal, Wi-Fi back on, **Refresh**.

Do not promise that the bar at the top turns STALE. It only does once the last good update is
over 5 minutes old, which will not happen inside this beat.

## If they ask

- **"Is the cyclone category a Signal No.?"** No. It is a model estimate of storm intensity.
  PAGASA wind signals account for terrain and lead time; this does not, and the card says so.
- **"Why is the shelter distance straight-line?"** Routing needs a road-network service we did
  not have. The card labels it rather than implying a walking time we cannot compute.
- **"Can it work offline?"** Partly, and it depends what is offline. With no internet but the
  server running, everything but the map keeps working: shelters and hotlines are files on our
  server, and rainfall shows the last PAGASA reading — marked STALE once it is old, or `unknown`
  if there is none. With the server down too, the app keeps its last result and the hotlines come
  from the phone's own cache, marked STALE. The map always needs the internet for its tiles.
- **"What is left?"** The real model. The code that runs it is built and tested, but it needs two
  things from Team A — the model and its preprocessing details — and one decision from us: which
  satellite frames to feed it. The app only knows your location, not an image, so turning the
  model on today would honestly report "unavailable" rather than a category.

## The replay chips

The **Replay: TS / TY / STY** chips at the top are example values from the design mockup, so
the examiner can see the UI at higher categories. They are labelled DEMO. If you show them,
say they are mockup values — they are not archived model runs. The "past storms, model result
versus the official category" view is not built.

## If it breaks

Keep going and narrate. A prototype failing live is a better story than a frozen screen.
- Map blank → "the tiles need internet" and move on to the shelter card, which still works.
- Backend down → if the app had loaded, it keeps the last result with a "Couldn't update" line;
  if not, it shows an error screen. Both have **Retry**, and both are real states worth showing.
  Restart uvicorn in the other terminal.
- Everything down → switch to the backup video. Record it the night before and keep it on the
  desktop, not in the cloud.
