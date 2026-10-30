// Debris hazards. Source: design mockup. TODO: replace with debris_matrix.json
export const debrisHazards = [
  {
    title: "Heavy Roofing & Steel Trusses",
    tag: "Catastrophic Airborne Debris",
    text: "Industrial steel sheets and unanchored trusses stripped airborne.",
  },
  {
    title: "Uprooted Hardwood Trees & Poles",
    tag: "Total Roadway Blockage",
    text: "Century-old trees and concrete utility poles snapped; access blocked.",
  },
  {
    title: "Facade & Window Implosions",
    tag: "Lethal Shrapnel Hazard",
    text: "Move strictly into interior corridors with reinforced concrete walls.",
  },
];

// Civil defense status per alert level.
export const civilDefense = {
  red: {
    badge: "MANDATORY ORDER",
    title: "Mandatory Civil Defense Evacuation",
    timeline: "TARGET TIMELINE: PROCEED TO REINFORCED SHELTER IMMEDIATELY",
  },
  orange: {
    badge: "PREPARE",
    title: "Prepare for Possible Evacuation",
    timeline: "TARGET TIMELINE: FOLLOW QCDRRMO AND BARANGAY DIRECTIVES",
  },
  yellow: {
    badge: "MONITOR",
    title: "Stay Alert and Monitor Updates",
    timeline: "TARGET TIMELINE: MONITOR PAGASA AND BARANGAY ANNOUNCEMENTS",
  },
  none: {
    badge: "NO ACTIVE ORDER",
    title: "No heavy rainfall warning in effect",
    timeline: "CONTINUE MONITORING PAGASA AND QCDRRMO UPDATES",
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
