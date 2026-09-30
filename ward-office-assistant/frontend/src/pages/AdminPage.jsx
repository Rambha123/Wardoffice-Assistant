export default function AdminPage() {
  // TODO: gate this route behind JWT auth (role === "ward_staff" | "admin")
  // once login exists — right now it's reachable by anyone, which is fine
  // for local development only.

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-xl font-semibold">Admin Panel</h1>
      <p className="text-sm text-gray-600">
        Ward staff can upload new Citizen Charters, forms, and circulars here.
        Uploads are pushed into the ingestion pipeline and become searchable
        by the AI Service Assistant.
      </p>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Upload a document</h2>
        <p className="text-gray-500 text-sm">
          TODO: build a form (doc_type select, title, file input) that posts
          to POST /api/documents/admin-upload once that endpoint is
          implemented on the backend.
        </p>
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Manage services & checklist questions</h2>
        <p className="text-gray-500 text-sm">
          TODO: CRUD UI for Service.checklist_questions / base_documents so
          non-technical ward staff can edit the checklist logic without
          touching the database directly.
        </p>
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="font-medium mb-2">Update office info & notices</h2>
        <p className="text-gray-500 text-sm">
          TODO: forms for OfficeInfo, Notice, and FAQ CRUD.
        </p>
      </section>
    </div>
  );
}
