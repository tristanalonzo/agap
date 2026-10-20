import { useState } from "react";
import { civilDefense, checklistItems } from "../data/safety";
import StatusBadge from "./StatusBadge";
import HotlinesSection from "./HotlinesSection";

export default function ActionTab({ rainfall }) {
  // No known alert level (for example PAGASA could not be loaded) = no order shown.
  const status = civilDefense[rainfall.alert_level] ?? civilDefense.unknown;
  const [done, setDone] = useState(checklistItems.map(() => false));
  const doneCount = done.filter(Boolean).length;

  function toggle(i) {
    setDone((prev) => prev.map((v, idx) => (idx === i ? !v : v)));
  }

  return (
    <>
      <section className={`civil-card ${rainfall.alert_level}`}>
        <div className="card-head">
          <span className="mono tiny muted">CIVIL DEFENSE STATUS</span>
          <span className="order-tag">{status.badge}</span>
          <StatusBadge status={rainfall.status} time={rainfall.retrieved_at} />
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

      <HotlinesSection />
    </>
  );
}