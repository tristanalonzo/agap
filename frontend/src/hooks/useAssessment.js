import { useEffect, useState } from "react";
import { getAssessment } from "../api/client";

// Loads the assessment once. (Refresh + 60 s polling comes later, task F2.)
export default function useAssessment(lat, lon, years) {
  const [assessment, setAssessment] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getAssessment(lat, lon, years)
      .then((data) => {
        if (!cancelled) setAssessment(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [lat, lon, years]);

  return { assessment, error, loading: !assessment && !error };
}
