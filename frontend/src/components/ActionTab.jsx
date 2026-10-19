import { useState } from "react";
import { civilDefense, checklistItems, hotlines } from "../data/safety";

export default function ActionTab({ scenario }) {
  const status = civilDefense[scenario.alert.level];
  const [done, setDone] = useState(checklistItems.map(() => false));
  const doneCount = done.filter(Boolean).length;

  function toggle(i) {
    setDone((prev) => prev.map((v, idx) => (idx === i ? !v : v)));
  }

  return (
    <>
      <section className={`civil-card ${scenario.alert.level}`}>
        <div className="card-head">
          <span className="mono tiny muted">CIVIL DEFENSE STATUS</span>
          <span className="order-tag">{status.badge}</span>
        </div>
        <h3>{status.title}</h3>
        <p className="mono tiny timeline">{status.timeline}</p>
      </section>

      <section className="card">
        <div className="card-head">
          <h3>Emergency Preparedness Checklist</h3>
          <span className="mono tiny muted">
            {doneCount} / {checklistItems.length} DONE
          </span>
        </div>
        {checklistItems.map((item, i) => (
          <label className="check-row" key={item}>
            <input type="checkbox" checked={done[i]} onChange={() => toggle(i)} />
            <span className={done[i] ? "struck" : ""}>{item}</span>
          </label>
        ))}
      </section>

      <div className="section-head">
        <p className="mono tiny muted">EMERGENCY HOTLINES:</p>
        <span className="green-text mono tiny">QC VERIFIED</span>
      </div>
      <div className="hotline-grid">
        {hotlines.map((h) => (
          <a className="hotline" key={h.number} href={`tel:${h.number}`}>
            <span className="bold">{h.label}</span>
            <span className="mono tiny muted">{h.sub}</span>
          </a>
        ))}
      </div>
    </>
  );
}