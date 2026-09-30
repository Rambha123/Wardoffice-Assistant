import { useState } from "react";

import { checkDocumentReadiness } from "../services/api.js";

export default function DocumentReadinessPage() {
  const [serviceId, setServiceId] = useState("");
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!serviceId || files.length === 0) return;

    setLoading(true);
    setError(null);
    try {
      const data = await checkDocumentReadiness({ serviceId, files });
      setResult(data);
    } catch (err) {
      setError("Could not run the readiness check. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold mb-2">Document Readiness Check</h1>
      <p className="text-sm text-gray-600 mb-6">
        This checks whether your documents look complete and readable before
        you visit the ward office. It does not verify legal validity.
        Uploaded files are deleted immediately after this check.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        {/* TODO: replace this free-text service_id input with the same
            <select> of services used in ChecklistPage once shared state
            (e.g. context or a service picker component) is factored out. */}
        <input
          type="text"
          placeholder="Service ID"
          value={serviceId}
          onChange={(e) => setServiceId(e.target.value)}
          className="w-full border rounded-md px-3 py-2"
        />
        <input
          type="file"
          multiple
          onChange={(e) => setFiles(Array.from(e.target.files))}
          className="w-full"
        />
        <button
          type="submit"
          className="bg-ward-primary text-white px-4 py-2 rounded-md disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Checking…" : "Check my documents"}
        </button>
      </form>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      {result && (
        <div className="bg-white border rounded-lg p-4">
          <p className="font-medium mb-3">
            {result.overall_ready ? "✅ You look ready to visit the office." : "⚠️ A few things need attention."}
          </p>
          <ul className="space-y-1">
            {result.checks.map((c, i) => (
              <li key={i}>
                {c.status === "ok" ? "✔" : "❌"} {c.document_name}
                {c.detail && <span className="text-gray-500 text-sm"> — {c.detail}</span>}
              </li>
            ))}
          </ul>
          {result.notes && <p className="text-xs text-gray-500 mt-3">{result.notes}</p>}
        </div>
      )}
    </div>
  );
}
