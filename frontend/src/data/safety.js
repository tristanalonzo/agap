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
};

export const checklistItems = [
  "COMPLETE IMMEDIATE EVACUATION to Barangay Evacuation Gymnasium.",
  "Emergency dispatch may be suspended during peak gusts.",
  "Keep all family members physically together; avoid travel outdoors.",
  "Stay in lowest-level interior corridors away from glass.",
];

// Source: design mockup. TODO: replace with qc_hotlines.json
export const hotlines = [
  { number: "122", label: "QC 122", sub: "QCDRRMO EOC" },
  { number: "911", label: "NATIONAL 911", sub: "Inter-Agency" },
  { number: "143", label: "RED CROSS 143", sub: "Rescue / Triage" },
];