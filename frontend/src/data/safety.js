// Civil defense status per alert level.
// Only "red" comes from the design. TODO: confirm orange/yellow wording.
export const civilDefense = {
  red: {
    badge: "MANDATORY ORDER",
    title: "Mandatory Civil Defense Evacuation",
    timeline: "TARGET TIMELINE: PROCEED TO REINFORCED SHELTER IMMEDIATELY",
  },
  orange: {
    badge: "PREPARE",
    title: "Prepare for Possible Evacuation",
    timeline: "TARGET TIMELINE: FOLLOW QCDRRMO DIRECTIVES (TODO: confirm)",
  },
  yellow: {
    badge: "MONITOR",
    title: "Stay Alert and Monitor Updates",
    timeline: "TARGET TIMELINE: NO ORDER YET (TODO: confirm)",
  },
  unknown: {
    badge: "NO ORDER LOADED",
    title: "No official evacuation order loaded",
    timeline: "FOLLOW QCDRRMO AND BARANGAY ANNOUNCEMENTS",
  },
};

export const checklistItems = [
  "Know where your nearest evacuation center is.",
  "Emergency dispatch may be suspended during peak gusts.",
  "Keep all family members physically together; avoid travel outdoors.",
  "Stay in lowest-level interior corridors away from glass.",
];
