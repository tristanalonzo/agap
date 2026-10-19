export default function HrwsCard({ scenario }) {
  const { alert, hrws } = scenario;

  return (
    <section className="card">
      <div className="card-head">
        <div>
          <h3>Official Heavy Rainfall Warning (HRWS)</h3>
          <p className="muted small">PAGASA NCR-PRSD Advisory Snapshot</p>
        </div>
        <span className="pill-green">FRESH</span>
      </div>

      <div className={`alert-box ${alert.level}`}>
        <div className="alert-row">
          <span className="alert-chip">{alert.label}</span>
          <strong className="mono">{hrws.rainfall}</strong>
        </div>
        <p>{hrws.text}</p>
      </div>

      <div className="two-col">
        <div className="box">
          <p className="box-label">AFFECTED SECTOR</p>
          <p className="mono bold">Quezon City (District 1-6)</p>
        </div>
        <div className="box">
          <p className="box-label">SOURCE VERIFICATION</p>
          <p className="mono green-text">bagong.pagasa.dost.gov.ph</p>
        </div>
      </div>
    </section>
  );
}