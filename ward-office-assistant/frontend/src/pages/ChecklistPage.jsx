import { useEffect, useState } from "react";

import { listServices, getNextChecklistStep } from "../services/api.js";

export default function ChecklistPage() {
  const [services, setServices] = useState([]);
  const [selectedServiceId, setSelectedServiceId] = useState("");
  const [answers, setAnswers] = useState([]); // [{question_id, answer}]
  const [step, setStep] = useState(null); // ChecklistResponse
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listServices()
      .then(setServices)
      .catch(() => {
        // TODO: surface a toast/error state once a shared UI notification
        // pattern exists across pages.
      });
  }, []);

  async function startOrAdvance(newAnswers) {
    setLoading(true);
    try {
      const data = await getNextChecklistStep({ serviceId: selectedServiceId, answers: newAnswers });
      setStep(data);
    } finally {
      setLoading(false);
    }
  }

  function handleServiceSelect(serviceId) {
    setSelectedServiceId(serviceId);
    setAnswers([]);
    setStep(null);
    startOrAdvance([]);
  }

  function handleAnswer(value) {
    const nextAnswers = [...answers, { question_id: step.next_question.question_id, answer: value }];
    setAnswers(nextAnswers);
    startOrAdvance(nextAnswers);
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Personalized document checklist</h1>

      <select
        className="border rounded-md px-3 py-2 mb-6 w-full"
        value={selectedServiceId}
        onChange={(e) => handleServiceSelect(e.target.value)}
      >
        <option value="" disabled>
          Select a service…
        </option>
        {services.map((s) => (
          <option key={s.id} value={s.id}>
            {s.name}
          </option>
        ))}
      </select>

      {loading && <p className="text-gray-500 text-sm">Loading…</p>}

      {step?.next_question && (
        <div className="bg-white border rounded-lg p-4">
          <p className="font-medium mb-3">{step.next_question.question_text}</p>
          {/* TODO: render question_type "single_select"/"text" properly;
              this only handles yes/no for now. */}
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded-md bg-ward-primary text-white" onClick={() => handleAnswer("yes")}>
              Yes
            </button>
            <button className="px-4 py-2 rounded-md border" onClick={() => handleAnswer("no")}>
              No
            </button>
          </div>
        </div>
      )}

      {step?.is_complete && step?.checklist && (
        <div className="bg-white border rounded-lg p-4">
          <h2 className="font-medium mb-3">Your document checklist</h2>
          <ul className="list-disc list-inside space-y-1">
            {step.checklist.map((doc, i) => (
              <li key={i}>{doc}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
