// Turns one of the design mockup's replay examples (scenarios.js) into the same shape as
// docs/contract/assess.sample.json, so every card reads the same fields.
// These are made-up example values, so they are always marked as demo.
export function toDemoReplay(baseAssessment, scenario) {
  return {
    ...baseAssessment,
    run_context: { ...baseAssessment.run_context, mode: "demo" },
    cyclone_assessment: {
      ...baseAssessment.cyclone_assessment,
      status: "demo",
      is_demo: true,
      category_code: null,
      category_name: scenario.classification,
      sustained_wind_kph: scenario.windKmh,
      warnings: ["Example values from the design mockup. Not a real prediction."],
    },
    rainfall_warning: {
      ...baseAssessment.rainfall_warning,
      status: "demo",
      alert_level: scenario.alert.level,
      raw_text: `${scenario.hrws.rainfall}: ${scenario.hrws.text}`,
    },
  };
}
